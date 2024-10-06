from django.urls import path

from .views import (
    PostList, PostDetail,
    CommentDetail,
    LikeToggleView,
    PostComments, CreatePost, CreateComment,  HideOrUnhidePostView,
    PostLikersList,ReactionToggleView,ReactionListView)


urlpatterns = [
    # posts endpoints
    path('post/createpost/', CreatePost.as_view(), name='create_post'),
    path('posts/', PostList.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    # comments endpoints
    path('post/createcomment/', CreateComment.as_view(), name='create_comment'),
    path('post/<int:pk>/comments/', PostComments.as_view(), name='post_comments'),
    path('comment/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    #path('post/comments/', CommentList.as_view(), name='comment-list'), COMMENTED BECAUSE IT CREATES COMMENT AND THIS IS REPETITIVE


    # likes endpoints
    path('post/<int:pk>/likers/', PostLikersList.as_view(), name='post-likers-list'),
    path('post/toggle-like/', LikeToggleView.as_view(), name='toggle-like'),

    path('post/hide-or-unhide-post/', HideOrUnhidePostView.as_view(), name='hide-or-unhide-post'),

    path('post/<int:pk>/toggle-reaction', ReactionToggleView.as_view(), name='toggle-reaction'),
    path('post/<int:pk>/reactions-list',  ReactionListView.as_view(), name='reactions-list'),
]