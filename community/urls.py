from django.urls import path
from .views import (
    ForumPostListCreateView,
    ForumPostDetailView,
    PostRepliesView,
    ReplyDeleteView,
    PostHelpfulView,
    PostReportView,
    ReplyReportView,
    LikePostView,
    MachineryListView,
    MachineryDetailView,
)

urlpatterns = [
    # Posts feed + create
    path('posts/', ForumPostListCreateView.as_view(), name='posts-list-create'),

    # Single post detail / edit / delete
    path('posts/<int:pk>/', ForumPostDetailView.as_view(), name='post-detail'),

    # Replies for a post
    path('posts/<int:pk>/replies/', PostRepliesView.as_view(), name='post-replies'),

    # Helpful toggle (idempotent, auth required)
    path('posts/<int:pk>/helpful/', PostHelpfulView.as_view(), name='post-helpful'),

    # Report a post
    path('posts/<int:pk>/report/', PostReportView.as_view(), name='post-report'),

    # Legacy like endpoint (kept for backward compat)
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='post-like'),

    # Reply operations
    path('replies/<int:pk>/delete/', ReplyDeleteView.as_view(), name='reply-delete'),
    path('replies/<int:pk>/report/', ReplyReportView.as_view(), name='reply-report'),

    # Machinery listings
    path('machinery/', MachineryListView.as_view(), name='machinery-list'),
    path('machinery/<int:pk>/', MachineryDetailView.as_view(), name='machinery-detail'),
]
