from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import ForumPost, PostReply, CommunityHelpful, CommunityReport, MachineryListing


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _time_ago(dt):
    """Human-readable relative time string."""
    if not dt:
        return 'Just now'
    diff = timezone.now() - dt
    if diff < timedelta(minutes=1):
        return 'Just now'
    if diff < timedelta(hours=1):
        m = int(diff.total_seconds() // 60)
        return f'{m} minute{"s" if m != 1 else ""} ago'
    if diff < timedelta(days=1):
        h = int(diff.total_seconds() // 3600)
        return f'{h} hour{"s" if h != 1 else ""} ago'
    if diff < timedelta(days=30):
        d = diff.days
        return f'{d} day{"s" if d != 1 else ""} ago'
    if diff < timedelta(days=365):
        m = diff.days // 30
        return f'{m} month{"s" if m != 1 else ""} ago'
    y = diff.days // 365
    return f'{y} year{"s" if y != 1 else ""} ago'


def _safe_author(user, legacy_name=''):
    """
    Return author dict with ONLY safe public fields.
    Never returns phone, email, password, or tokens.
    """
    if user and user.is_authenticated:
        profile = getattr(user, 'farmer_profile', None)
        name = (profile.name if profile else None) or user.get_full_name() or user.username
        avatar_url = None
        if profile and profile.avatar:
            try:
                avatar_url = profile.avatar.url
            except Exception:
                avatar_url = None
        return {'name': name, 'avatar': avatar_url}
    # Fall back to legacy CharField
    return {'name': legacy_name or 'Farmer', 'avatar': None}


# ---------------------------------------------------------------------------
# Reply serializer
# ---------------------------------------------------------------------------

class PostReplySerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    locality_display = serializers.SerializerMethodField()

    class Meta:
        model = PostReply
        fields = [
            'id', 'author_info', 'content', 'is_scientist',
            'time_ago', 'locality_display', 'created_at',
        ]
        read_only_fields = ['id', 'author_info', 'time_ago', 'locality_display', 'created_at']

    def get_author_info(self, obj):
        return _safe_author(obj.user, obj.author)

    def get_time_ago(self, obj):
        return _time_ago(obj.created_at)

    def get_locality_display(self, obj):
        """Show the replier's approximate locality from their profile."""
        profile = getattr(obj.user, 'farmer_profile', None) if obj.user else None
        if not profile:
            return ''
        parts = [p for p in [profile.village, profile.district, profile.state] if p]
        return ', '.join(parts[:2]) if parts else ''


# ---------------------------------------------------------------------------
# Forum post serializer
# ---------------------------------------------------------------------------

class ForumPostSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    helpful_count = serializers.SerializerMethodField()
    is_helpful_by_me = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    replies_list = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    # Write-only inputs for post creation
    content = serializers.CharField(min_length=10, max_length=2000)
    crop = serializers.CharField(max_length=100, required=False, default='All Crops')
    category = serializers.ChoiceField(choices=ForumPost.CATEGORY_CHOICES, required=False, default='general')
    locality = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    district = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    state = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    show_location = serializers.BooleanField(required=False, default=True)
    is_rental = serializers.BooleanField(required=False, default=False)
    language = serializers.ChoiceField(choices=ForumPost.LANGUAGE_CHOICES, required=False, default='en')

    # Legacy field accepted but not required from new clients
    author = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    location = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')

    class Meta:
        model = ForumPost
        fields = [
            'id',
            # Safe author — never exposes email/phone
            'author_info',
            # Content
            'content', 'crop', 'category', 'category_display',
            # Location — approximate only
            'locality', 'district', 'state', 'show_location', 'location_display',
            # Media
            'image_url',
            # Flags
            'is_rental', 'is_verified', 'is_official',
            # Social counts
            'helpful_count', 'is_helpful_by_me', 'reply_count',
            # Nested replies (up to 5 most recent shown inline)
            'replies_list',
            # Timestamps
            'time_ago', 'created_at',
            # Language
            'language',
            # Write fields (accepted on POST, ignored in read)
            'author', 'location',
        ]
        read_only_fields = [
            'id', 'author_info', 'location_display', 'image_url',
            'helpful_count', 'is_helpful_by_me', 'reply_count', 'replies_list',
            'time_ago', 'created_at', 'is_verified', 'is_official', 'category_display',
        ]

    # --- Read-only computed fields ---

    def get_author_info(self, obj):
        return _safe_author(obj.user, obj.author)

    def get_location_display(self, obj):
        return obj.get_display_location()

    def get_helpful_count(self, obj):
        # Use annotated value when available (avoids extra query per post)
        return getattr(obj, 'helpful_count_annotated', None) or obj.get_helpful_count()

    def get_is_helpful_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.is_helpful_by(request.user)
        return False

    def get_reply_count(self, obj):
        return getattr(obj, 'reply_count_annotated', None) or obj.replies.filter(status='active').count()

    def get_replies_list(self, obj):
        # Show up to 3 most recent active replies inline
        qs = obj.replies.filter(status='active').order_by('created_at')[:3]
        return PostReplySerializer(qs, many=True, context=self.context).data

    def get_time_ago(self, obj):
        return _time_ago(obj.created_at)

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            try:
                url = obj.image.url
                return request.build_absolute_uri(url) if request else url
            except Exception:
                return None
        return None

    def get_category_display(self, obj):
        return obj.get_category_display()


# ---------------------------------------------------------------------------
# Machinery listing serializer
# ---------------------------------------------------------------------------

class MachineryListingSerializer(serializers.ModelSerializer):
    owner_info = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    machine_type_display = serializers.SerializerMethodField()
    price_unit_display = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    # Write fields
    machine_type = serializers.ChoiceField(choices=MachineryListing.MACHINE_TYPES)
    machine_name = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    locality = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    district = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    state = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    availability = serializers.CharField(max_length=200, required=False, default='Available')
    rental_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    price_unit = serializers.ChoiceField(choices=MachineryListing.PRICE_UNITS, required=False, default='per_day')
    contact_method = serializers.CharField(
        max_length=200, required=False, allow_blank=True,
        default='Contact via community reply'
    )

    class Meta:
        model = MachineryListing
        fields = [
            'id', 'owner_info',
            'machine_type', 'machine_type_display', 'machine_name', 'description',
            'locality', 'district', 'state', 'location_display',
            'availability', 'rental_price', 'price_unit', 'price_unit_display',
            'image_url', 'contact_method', 'status',
            'time_ago', 'created_at',
        ]
        read_only_fields = [
            'id', 'owner_info', 'location_display', 'image_url',
            'machine_type_display', 'price_unit_display', 'time_ago', 'created_at',
        ]

    def get_owner_info(self, obj):
        return _safe_author(obj.owner, '')

    def get_location_display(self, obj):
        return obj.get_display_location()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            try:
                url = obj.image.url
                return request.build_absolute_uri(url) if request else url
            except Exception:
                return None
        return None

    def get_machine_type_display(self, obj):
        return obj.get_machine_type_display()

    def get_price_unit_display(self, obj):
        return obj.get_price_unit_display()

    def get_time_ago(self, obj):
        return _time_ago(obj.created_at)


# ---------------------------------------------------------------------------
# Report serializer (write-only; never returns reporter identity)
# ---------------------------------------------------------------------------

class CommunityReportSerializer(serializers.ModelSerializer):
    reason = serializers.ChoiceField(choices=CommunityReport.REASON_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    post_id = serializers.IntegerField(required=False, allow_null=True)
    reply_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = CommunityReport
        fields = ['reason', 'description', 'post_id', 'reply_id']
