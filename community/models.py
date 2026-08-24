from django.db import models
from django.contrib.auth.models import User


class ForumPost(models.Model):
    """A community post by a farmer. Author is resolved from the authenticated User."""

    CATEGORY_CHOICES = [
        ('crop_problem', 'Crop Problem'),
        ('disease', 'Disease'),
        ('pest', 'Pest'),
        ('irrigation', 'Irrigation'),
        ('fertilizer', 'Fertilizer'),
        ('seeds', 'Seeds'),
        ('market_price', 'Market Price'),
        ('weather', 'Weather'),
        ('govt_scheme', 'Government Scheme'),
        ('machinery', 'Machinery'),
        ('general', 'General Farming'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('flagged', 'Flagged'),
        ('removed', 'Removed'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
    ]

    # Author — linked to authenticated user; legacy posts keep the CharField fallback
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='community_posts',
    )
    # Legacy / display name (kept for backward-compat with old rows)
    author = models.CharField(max_length=120, blank=True, default='')

    # Post content
    content = models.TextField()

    # Classification
    crop = models.CharField(max_length=100, default='All Crops')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')

    # Location — only approximate info, never exact address
    locality = models.CharField(max_length=150, blank=True, default='')
    district = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    show_location = models.BooleanField(default=True)

    # Legacy single-string location field (kept for old rows)
    location = models.CharField(max_length=200, blank=True, default='')

    # Optional image attachment
    image = models.ImageField(upload_to='community_images/', null=True, blank=True)

    # Flags
    is_rental = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_official = models.BooleanField(default=False)

    # Moderation
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # Language of the original post
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    # Legacy: used to be a static string; computed on-the-fly now
    time_ago = models.CharField(max_length=50, default='Just now')

    # Counters — kept for quick reads; kept in sync by signals/views
    likes = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        author_str = self.author or (self.user.username if self.user else 'Unknown')
        return f"{author_str} ({self.crop}): {self.content[:50]}"

    def get_display_location(self):
        """Return a safe approximate location string, never an exact address."""
        if not self.show_location:
            return ''
        parts = []
        if self.locality:
            parts.append(self.locality)
        if self.district and self.district != self.locality:
            parts.append(self.district)
        if self.state:
            parts.append(self.state)
        if parts:
            return ', '.join(parts)
        # Fall back to legacy field
        return self.location or ''

    def get_helpful_count(self):
        return self.helpful_marks.count()

    def is_helpful_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.helpful_marks.filter(user=user).exists()


class PostReply(models.Model):
    """A reply to a community post."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('flagged', 'Flagged'),
        ('removed', 'Removed'),
    ]

    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')

    # Author linked to authenticated user
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='community_replies',
    )
    # Legacy / display name
    author = models.CharField(max_length=120, blank=True, default='')

    content = models.TextField()
    is_scientist = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        author_str = self.author or (self.user.username if self.user else 'Unknown')
        return f"Reply by {author_str} on Post #{self.post.id}"


class CommunityHelpful(models.Model):
    """Tracks which users marked a post as Helpful. Unique per user+post."""

    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='helpful_marks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helpful_marks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} found Post #{self.post.id} helpful"


class CommunityReport(models.Model):
    """Report for a post or reply."""

    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('misleading', 'Misleading Farming Information'),
        ('abusive', 'Abusive Language'),
        ('inappropriate', 'Inappropriate Content'),
        ('advertisement', 'Advertisement'),
        ('scam', 'Scam'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('actioned', 'Action Taken'),
    ]

    post = models.ForeignKey(
        ForumPost, on_delete=models.CASCADE,
        related_name='reports', null=True, blank=True,
    )
    reply = models.ForeignKey(
        PostReply, on_delete=models.CASCADE,
        related_name='reports', null=True, blank=True,
    )
    reported_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='submitted_reports',
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = f"Post #{self.post.id}" if self.post else f"Reply #{self.reply.id}"
        return f"Report on {target}: {self.reason}"


class MachineryListing(models.Model):
    """A machinery-for-rent listing posted by a farmer."""

    MACHINE_TYPES = [
        ('tractor', 'Tractor'),
        ('combine_harvester', 'Combine Harvester'),
        ('rotavator', 'Rotavator'),
        ('seed_drill', 'Seed Drill'),
        ('drone_sprayer', 'Drone Sprayer'),
        ('power_tiller', 'Power Tiller'),
        ('cultivator', 'Cultivator'),
        ('sprayer', 'Sprayer'),
        ('thresher', 'Thresher'),
        ('other', 'Other'),
    ]

    PRICE_UNITS = [
        ('per_hour', 'Per Hour'),
        ('per_day', 'Per Day'),
        ('per_acre', 'Per Acre'),
        ('negotiable', 'Negotiable'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Currently Rented'),
        ('unavailable', 'Unavailable'),
        ('removed', 'Removed'),
    ]

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='machinery_listings',
    )
    machine_type = models.CharField(max_length=30, choices=MACHINE_TYPES)
    machine_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')

    # Location — approximate only
    locality = models.CharField(max_length=150, blank=True, default='')
    district = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')

    availability = models.CharField(max_length=200, blank=True, default='Available')
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=15, choices=PRICE_UNITS, default='per_day')

    image = models.ImageField(upload_to='machinery_images/', null=True, blank=True)

    # Contact — public-facing only if the owner explicitly adds it
    contact_method = models.CharField(max_length=200, blank=True, default='Contact via community reply')

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.machine_name} ({self.get_machine_type_display()}) – {self.district or self.locality or 'Unknown location'}"

    def get_display_location(self):
        parts = []
        if self.locality:
            parts.append(self.locality)
        if self.district and self.district != self.locality:
            parts.append(self.district)
        if self.state:
            parts.append(self.state)
        return ', '.join(parts) if parts else ''
