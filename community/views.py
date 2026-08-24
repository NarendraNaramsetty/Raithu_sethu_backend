from django.db.models import Count, Q, Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from .models import ForumPost, PostReply, CommunityHelpful, CommunityReport, MachineryListing
from .serializers import (
    ForumPostSerializer,
    PostReplySerializer,
    MachineryListingSerializer,
    CommunityReportSerializer,
)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class MachineryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


# ---------------------------------------------------------------------------
# Helper: resolve display name from authenticated user (never trusts client)
# ---------------------------------------------------------------------------

def _get_safe_author_name(user):
    """Return the display name from the server-side user profile."""
    if user and user.is_authenticated:
        profile = getattr(user, 'farmer_profile', None)
        if profile and profile.name:
            return profile.name
        return user.get_full_name() or user.username
    return 'Farmer'


def _get_user_location(user):
    """Return (locality, district, state) from the user's profile."""
    if user and user.is_authenticated:
        profile = getattr(user, 'farmer_profile', None)
        if profile:
            return profile.village or '', profile.district or '', profile.state or ''
    return '', '', ''


# ---------------------------------------------------------------------------
# Posts list + create
# ---------------------------------------------------------------------------

class ForumPostListCreateView(APIView):
    """
    GET  /api/community/posts/   — paginated post feed (public read)
    POST /api/community/posts/   — create a post (auth required)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]

    def _build_queryset(self, request):
        qs = (
            ForumPost.objects
            .filter(status='active')
            .select_related('user', 'user__farmer_profile')
            .prefetch_related(
                Prefetch(
                    'replies',
                    queryset=PostReply.objects.filter(status='active')
                    .select_related('user', 'user__farmer_profile')
                    .order_by('created_at'),
                ),
            )
            .annotate(
                helpful_count_annotated=Count('helpful_marks', distinct=True),
                reply_count_annotated=Count('replies', filter=Q(replies__status='active'), distinct=True),
            )
        )

        # --- Filters ---
        crop = request.query_params.get('crop')
        if crop:
            qs = qs.filter(crop__iexact=crop)

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        district = request.query_params.get('district')
        if district:
            qs = qs.filter(district__icontains=district)

        state = request.query_params.get('state')
        if state:
            qs = qs.filter(state__icontains=state)

        locality = request.query_params.get('locality')
        if locality:
            qs = qs.filter(
                Q(locality__icontains=locality) |
                Q(district__icontains=locality) |
                Q(location__icontains=locality)
            )

        is_rental = request.query_params.get('is_rental')
        if is_rental in ('true', '1'):
            qs = qs.filter(is_rental=True)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(content__icontains=search) |
                Q(crop__icontains=search) |
                Q(locality__icontains=search) |
                Q(district__icontains=search) |
                Q(location__icontains=search) |
                Q(author__icontains=search)
            )

        # --- Ordering ---
        order = request.query_params.get('order', 'newest')
        if order == 'helpful':
            qs = qs.order_by('-helpful_count_annotated', '-created_at')
        elif order == 'discussed':
            qs = qs.order_by('-reply_count_annotated', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get(self, request):
        qs = self._build_queryset(request)
        paginator = PostPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ForumPostSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'detail': 'Please log in as a farmer to create a community post.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = ForumPostSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Determine location: prefer client-submitted values, fall back to profile
        validated = serializer.validated_data
        profile_locality, profile_district, profile_state = _get_user_location(request.user)

        locality = validated.get('locality') or profile_locality
        district = validated.get('district') or profile_district
        state = validated.get('state') or profile_state

        # Legacy location string for backward compat
        loc_parts = [p for p in [locality, district, state] if p]
        location_str = ', '.join(loc_parts) if loc_parts else ''

        # Detect language from Accept-Language header or request body
        language = validated.get('language', 'en')

        post = ForumPost.objects.create(
            user=request.user,
            author=_get_safe_author_name(request.user),  # server-side; ignore client-sent name
            content=validated['content'],
            crop=validated.get('crop', 'All Crops'),
            category=validated.get('category', 'general'),
            locality=locality,
            district=district,
            state=state,
            location=location_str,
            show_location=validated.get('show_location', True),
            is_rental=validated.get('is_rental', False),
            language=language,
            status='active',
        )

        # Handle optional image upload
        image = request.FILES.get('image')
        if image:
            post.image = image
            post.save()

        out = ForumPostSerializer(post, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Single post detail + edit + delete
# ---------------------------------------------------------------------------

class ForumPostDetailView(APIView):
    """
    GET    /api/community/posts/<pk>/   — retrieve a single post
    PATCH  /api/community/posts/<pk>/   — edit own post
    DELETE /api/community/posts/<pk>/   — delete own post
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]

    def _get_post(self, pk):
        try:
            return (
                ForumPost.objects
                .select_related('user', 'user__farmer_profile')
                .prefetch_related('replies__user', 'replies__user__farmer_profile')
                .get(pk=pk, status='active')
            )
        except ForumPost.DoesNotExist:
            return None

    def get(self, request, pk):
        post = self._get_post(pk)
        if not post:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ForumPostSerializer(post, context={'request': request}).data)

    def patch(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        post = self._get_post(pk)
        if not post:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({'detail': 'You can only edit your own posts.'}, status=status.HTTP_403_FORBIDDEN)

        allowed = ['content', 'crop', 'category', 'locality', 'district', 'state', 'show_location', 'is_rental', 'language']
        for field in allowed:
            if field in request.data:
                setattr(post, field, request.data[field])

        image = request.FILES.get('image')
        if image:
            post.image = image

        # Rebuild legacy location string
        loc_parts = [p for p in [post.locality, post.district, post.state] if p]
        post.location = ', '.join(loc_parts)
        post.save()

        return Response(ForumPostSerializer(post, context={'request': request}).data)

    def delete(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post = ForumPost.objects.get(pk=pk)
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
            return Response({'detail': 'You can only delete your own posts.'}, status=status.HTTP_403_FORBIDDEN)

        post.status = 'removed'
        post.save()
        return Response({'detail': 'Post deleted.'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Replies
# ---------------------------------------------------------------------------

class PostRepliesView(APIView):
    """
    GET  /api/community/posts/<pk>/replies/   — list all replies for a post
    POST /api/community/posts/<pk>/replies/   — add a reply (auth required)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            post = ForumPost.objects.get(pk=pk, status='active')
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        replies = (
            post.replies
            .filter(status='active')
            .select_related('user', 'user__farmer_profile')
            .order_by('created_at')
        )
        return Response(PostReplySerializer(replies, many=True, context={'request': request}).data)

    def post(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'detail': 'Please log in as a farmer to reply.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            post = ForumPost.objects.get(pk=pk, status='active')
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'detail': 'Reply content is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(content) > 2000:
            return Response({'detail': 'Reply must be under 2000 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        reply = PostReply.objects.create(
            post=post,
            user=request.user,
            author=_get_safe_author_name(request.user),
            content=content,
            status='active',
        )

        # Keep the cached count in sync
        post.replies_count = post.replies.filter(status='active').count()
        post.save(update_fields=['replies_count'])

        return Response(PostReplySerializer(reply, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ReplyDeleteView(APIView):
    """DELETE /api/community/replies/<pk>/ — delete own reply"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            reply = PostReply.objects.get(pk=pk)
        except PostReply.DoesNotExist:
            return Response({'detail': 'Reply not found.'}, status=status.HTTP_404_NOT_FOUND)

        if reply.user != request.user:
            return Response({'detail': 'You can only delete your own replies.'}, status=status.HTTP_403_FORBIDDEN)

        post = reply.post
        reply.status = 'removed'
        reply.save()

        post.replies_count = post.replies.filter(status='active').count()
        post.save(update_fields=['replies_count'])

        return Response({'detail': 'Reply deleted.'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Helpful (idempotent toggle)
# ---------------------------------------------------------------------------

class PostHelpfulView(APIView):
    """POST /api/community/posts/<pk>/helpful/ — toggle Helpful (auth required)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = ForumPost.objects.get(pk=pk, status='active')
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        helpful, created = CommunityHelpful.objects.get_or_create(post=post, user=request.user)
        if not created:
            # Already marked — toggle off
            helpful.delete()
            marked = False
        else:
            marked = True

        count = post.helpful_marks.count()
        # Keep legacy likes counter in sync
        post.likes = count
        post.save(update_fields=['likes'])

        return Response({'helpful_count': count, 'is_helpful_by_me': marked}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

class PostReportView(APIView):
    """POST /api/community/posts/<pk>/report/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = ForumPost.objects.get(pk=pk)
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'other')
        description = request.data.get('description', '')

        CommunityReport.objects.create(
            post=post,
            reported_by=request.user,
            reason=reason,
            description=description,
        )

        # Auto-flag if post receives 3+ reports
        report_count = post.reports.count()
        if report_count >= 3 and post.status == 'active':
            post.status = 'flagged'
            post.save(update_fields=['status'])

        return Response({'detail': 'Report submitted. Thank you for helping keep the community safe.'}, status=status.HTTP_201_CREATED)


class ReplyReportView(APIView):
    """POST /api/community/replies/<pk>/report/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            reply = PostReply.objects.get(pk=pk)
        except PostReply.DoesNotExist:
            return Response({'detail': 'Reply not found.'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'other')
        description = request.data.get('description', '')

        CommunityReport.objects.create(
            reply=reply,
            reported_by=request.user,
            reason=reason,
            description=description,
        )

        report_count = reply.reports.count()
        if report_count >= 3 and reply.status == 'active':
            reply.status = 'flagged'
            reply.save(update_fields=['status'])

        return Response({'detail': 'Report submitted.'}, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Legacy like endpoint (kept for backward compat — NOT idempotent but won't break existing data)
# ---------------------------------------------------------------------------

class LikePostView(APIView):
    """POST /api/community/posts/<pk>/like/ — legacy; prefer /helpful/ for new clients"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            post = ForumPost.objects.get(pk=pk)
            post.likes += 1
            post.save(update_fields=['likes'])
            return Response({'likes': post.likes}, status=status.HTTP_200_OK)
        except ForumPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Machinery listings
# ---------------------------------------------------------------------------

class MachineryListView(APIView):
    """
    GET  /api/community/machinery/   — list available machinery (public)
    POST /api/community/machinery/   — create a listing (auth required)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = (
            MachineryListing.objects
            .filter(status='available')
            .select_related('owner', 'owner__farmer_profile')
        )

        # Filters
        machine_type = request.query_params.get('machine_type')
        if machine_type:
            qs = qs.filter(machine_type=machine_type)

        district = request.query_params.get('district')
        if district:
            qs = qs.filter(district__icontains=district)

        state = request.query_params.get('state')
        if state:
            qs = qs.filter(state__icontains=state)

        locality = request.query_params.get('locality')
        if locality:
            qs = qs.filter(
                Q(locality__icontains=locality) |
                Q(district__icontains=locality)
            )

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(machine_name__icontains=search) |
                Q(description__icontains=search) |
                Q(locality__icontains=search) |
                Q(district__icontains=search)
            )

        # Prioritise nearby results when user district is known
        user_district = request.query_params.get('user_district')
        if user_district:
            from django.db.models import Case, When, IntegerField
            qs = qs.annotate(
                proximity=Case(
                    When(district__iexact=user_district, then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            ).order_by('proximity', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        paginator = MachineryPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = MachineryListingSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'detail': 'Please log in to create a machinery listing.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MachineryListingSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        profile_locality, profile_district, profile_state = _get_user_location(request.user)

        listing = MachineryListing.objects.create(
            owner=request.user,
            machine_type=validated['machine_type'],
            machine_name=validated['machine_name'],
            description=validated.get('description', ''),
            locality=validated.get('locality') or profile_locality,
            district=validated.get('district') or profile_district,
            state=validated.get('state') or profile_state,
            availability=validated.get('availability', 'Available'),
            rental_price=validated.get('rental_price'),
            price_unit=validated.get('price_unit', 'per_day'),
            contact_method=validated.get('contact_method', 'Contact via community reply'),
            status='available',
        )

        image = request.FILES.get('image')
        if image:
            listing.image = image
            listing.save()

        return Response(
            MachineryListingSerializer(listing, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class MachineryDetailView(APIView):
    """
    PATCH  /api/community/machinery/<pk>/  — update own listing
    DELETE /api/community/machinery/<pk>/  — remove own listing
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticated]

    def _get_listing(self, pk, user):
        try:
            return MachineryListing.objects.get(pk=pk, owner=user)
        except MachineryListing.DoesNotExist:
            return None

    def patch(self, request, pk):
        listing = self._get_listing(pk, request.user)
        if not listing:
            return Response({'detail': 'Listing not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)

        allowed = ['machine_name', 'description', 'locality', 'district', 'state',
                   'availability', 'rental_price', 'price_unit', 'contact_method', 'status']
        for field in allowed:
            if field in request.data:
                setattr(listing, field, request.data[field])

        image = request.FILES.get('image')
        if image:
            listing.image = image

        listing.save()
        return Response(MachineryListingSerializer(listing, context={'request': request}).data)

    def delete(self, request, pk):
        listing = self._get_listing(pk, request.user)
        if not listing:
            return Response({'detail': 'Listing not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)

        listing.status = 'removed'
        listing.save(update_fields=['status'])
        return Response({'detail': 'Listing removed.'}, status=status.HTTP_200_OK)
