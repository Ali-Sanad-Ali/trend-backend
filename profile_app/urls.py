from django.urls import path
from .views import (
    ProfileViewList,
    ProfileDetails,
    FollowViewList,
    #UpdateProfileView,
    FollowUserView,
    UnfollowUserView,
    FollowersListAPIView,
    FollowingListAPIView,
    #UserVlogsListView
)

urlpatterns = [
    # profile endpoints
    path('profile/', ProfileViewList.as_view(), name='profile'),
    path('profile/<int:pk>/', ProfileDetails.as_view(), name='profile-details'),
    #path('profile/edit-profile/', UpdateProfileView.as_view(), name='update-profile'),

    # follow endpoints
    path('follow/', FollowViewList.as_view(), name='follow'),
    path('follow-user/', FollowUserView.as_view(), name='follow-user'),  # for following a user
    path('unfollow/<int:pk>/', UnfollowUserView.as_view(), name='unfollow-user'),  # unfollowing a user
    path('profile/<int:pk>/followers/', FollowersListAPIView.as_view(), name='followers-list'),  # listing followers
    path('profile/<int:pk>/following/', FollowingListAPIView.as_view(), name='following-list'),  # listing following users
    #path('profile/<int:profile_id>/vlogs/', UserVlogsListView.as_view(), name='user-vlogs-list'),
]