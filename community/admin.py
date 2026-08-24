from django.contrib import admin
from .models import ForumPost, PostReply, CommunityHelpful, CommunityReport, MachineryListing


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_author', 'crop', 'category', 'get_location', 'status', 'is_rental', 'created_at']
    list_filter = ['status', 'category', 'crop', 'is_rental', 'state']
    search_fields = ['author', 'user__username', 'user__farmer_profile__name', 'content', 'locality', 'district']
    readonly_fields = ['created_at', 'updated_at', 'likes', 'replies_count']
    list_editable = ['status']
    ordering = ['-created_at']
    actions = ['mark_active', 'mark_flagged', 'mark_removed']

    def get_author(self, obj):
        if obj.user:
            profile = getattr(obj.user, 'farmer_profile', None)
            return profile.name if profile and profile.name else obj.user.username
        return obj.author or '—'
    get_author.short_description = 'Author'

    def get_location(self, obj):
        return obj.get_display_location() or '—'
    get_location.short_description = 'Location'

    @admin.action(description='Mark selected posts as Active')
    def mark_active(self, request, queryset):
        queryset.update(status='active')

    @admin.action(description='Flag selected posts for review')
    def mark_flagged(self, request, queryset):
        queryset.update(status='flagged')

    @admin.action(description='Remove selected posts')
    def mark_removed(self, request, queryset):
        queryset.update(status='removed')


@admin.register(PostReply)
class PostReplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_author', 'post_id', 'status', 'created_at']
    list_filter = ['status', 'is_scientist']
    search_fields = ['author', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']

    def get_author(self, obj):
        if obj.user:
            profile = getattr(obj.user, 'farmer_profile', None)
            return profile.name if profile and profile.name else obj.user.username
        return obj.author or '—'
    get_author.short_description = 'Author'


@admin.register(CommunityHelpful)
class CommunityHelpfulAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_id', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(CommunityReport)
class CommunityReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reason', 'get_target', 'get_reporter', 'status', 'created_at']
    list_filter = ['status', 'reason']
    search_fields = ['reported_by__username', 'description']
    readonly_fields = ['created_at']
    list_editable = ['status']
    ordering = ['-created_at']

    def get_target(self, obj):
        if obj.post:
            return f'Post #{obj.post.id}'
        if obj.reply:
            return f'Reply #{obj.reply.id}'
        return '—'
    get_target.short_description = 'Reported Content'

    def get_reporter(self, obj):
        if obj.reported_by:
            return obj.reported_by.username
        return 'Anonymous'
    get_reporter.short_description = 'Reported By'


@admin.register(MachineryListing)
class MachineryListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'machine_name', 'machine_type', 'get_owner', 'get_location', 'status', 'created_at']
    list_filter = ['status', 'machine_type', 'state']
    search_fields = ['machine_name', 'owner__username', 'locality', 'district']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']

    def get_owner(self, obj):
        profile = getattr(obj.owner, 'farmer_profile', None)
        return profile.name if profile and profile.name else obj.owner.username
    get_owner.short_description = 'Owner'

    def get_location(self, obj):
        return obj.get_display_location() or '—'
    get_location.short_description = 'Location'
