from rest_framework import generics, status
from .serializers import ProfileSerializer, FollowSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from .models import Profile, Follow
from django.db.models import Exists, OuterRef
from authentication.models import Block, CustomUser
from rest_framework.response import Response
from authentication.pagination import CustomPageNumberPagination
# from vlog.models import Video
# from vlog.serializers import VideoSerializer


# class ProfileViewList(generics.ListCreateAPIView):
#     """
#         List all profiles or create a new profile.
#     """
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     pagination_class = CustomPageNumberPagination

#     def get_queryset(self):
#         """
#         Filter out blocked profiles for authenticated users.
#         """
#         queryset = Profile.objects.all().order_by('-created_at')
#         user = self.request.user
#         if user.is_authenticated:
#             blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
#             blocked_by_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
#             users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
#             queryset = Profile.objects.exclude(user__in=users_to_exclude)
#         return queryset.order_by('-created_at')


class ProfileViewList(generics.ListAPIView):
    """
    List all profiles. Profile creation is not allowed because profiles are automatically
    created when a user registers.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Filter out blocked profiles for authenticated users.
        """
        queryset = Profile.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_authenticated:
            blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
            blocked_by_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
            users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
            queryset = Profile.objects.exclude(user__in=users_to_exclude)
        return queryset.order_by('-created_at')


# class ProfileDetails(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Retrieve, update or delete a profile instance.
#     """
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """
#         Filter out blocked profiles for authenticated users.
#         """
#         queryset = super().get_queryset()
#         user = self.request.user
#         if user.is_authenticated:
#             blocked_subquery = Block.objects.filter(blocker=OuterRef('user'), blocked=user)
#             queryset = queryset.annotate(is_blocked=Exists(blocked_subquery)).exclude(is_blocked=True)
#         return queryset



class ProfileDetails(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a profile instance. Deletion is not allowed because profiles are automatically 
    created when users are registered, and deleting a profile would not delete the associated user. 
    Allowing profile deletion could lead to inconsistencies in user data. 

    Only the owner of the profile is permitted to update their profile to maintain security and data integrity.
    Any authenticated user can retrieve profile details, but only the owner can make changes.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Allow retrieving profiles for any authenticated user,
        but exclude blocked profiles for the user.
        """
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            blocked_subquery = Block.objects.filter(blocker=OuterRef('user'), blocked=user)
            queryset = queryset.annotate(is_blocked=Exists(blocked_subquery)).exclude(is_blocked=True)
        return queryset

    def update(self, request, *args, **kwargs):
        """
        Only allow the profile owner to update the profile.
        """
        profile = self.get_object()

        # Check if the authenticated user is the owner of the profile
        if request.user != profile.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Disallow deletion of the profile.
        """
        raise PermissionDenied("Profile deletion is not allowed.")



# class UpdateProfileView(generics.UpdateAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return self.request.user.profile


class FollowViewList(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FollowUserView(generics.CreateAPIView):
    """
    View to follow a user.
    """
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        follower = request.user
        following_id = request.data.get('following_id')  # Assuming you send following user ID in request data

        try:
            following = CustomUser.objects.get(pk=following_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if follower == following:
            return Response({'error': 'Cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already following
        if Follow.objects.filter(follower=follower, following=following).exists():
            return Response({'error': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        # Create a new follow relationship
        follow = Follow.objects.create(follower=follower, following=following)
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnfollowUserView(generics.DestroyAPIView):
    """
    View to unfollow a user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        follower = request.user
        following_id = self.kwargs.get('pk')  # Assuming you pass following user ID in URL

        try:
            following = CustomUser.objects.get(pk=following_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if already following
        follow = Follow.objects.filter(follower=follower, following=following)
        if not follow.exists():
            return Response({'error': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowersListAPIView(generics.ListAPIView):
    """
    List all followers of a user.
    """
    serializer_class = ProfileSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  
        user_id = self.kwargs.get('pk')
        request_user = self.request.user
        try:
            user = CustomUser.objects.get(pk=user_id)
            # Get list of followers' user IDs
            followers = user.followers.all().values_list('follower', flat=True)
            blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
            # Filter out blocked users from followers list
            followers = [follower for follower in followers if follower not in blocked_users]
            # Return profiles of all followers
            return Profile.objects.filter(user__in=followers)
        except CustomUser.DoesNotExist:
            return Profile.objects.none()
     

class FollowingListAPIView(generics.ListAPIView):
    """
    List all users a user is following.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):  
        user_id = self.kwargs.get('pk')
        request_user = self.request.user
        try:
            user = CustomUser.objects.get(pk=user_id)
            # Get list of following user IDs
            followings = user.following.all().values_list('following', flat=True)
            # Get list of blocked user IDs
            blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
            # Filter out blocked users from followings list
            followings = [following for following in followings if following not in blocked_users]
            # Return profiles of all users being followed
            return Profile.objects.filter(user__in=followings)
        except CustomUser.DoesNotExist:
            return Profile.objects.none()
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context    


# class UserVlogsListView(generics.ListAPIView):
#     serializer_class = VideoSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPageNumberPagination

#     def get_queryset(self):
#         profile_id = self.kwargs['profile_id']
#         profile = Profile.objects.get(id=profile_id)
#         return Video.objects.filter(author=profile.user).order_by('-created_at')