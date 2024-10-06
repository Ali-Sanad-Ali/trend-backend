from rest_framework import serializers
from .models import Profile, Follow
from post.models import Post
from rest_framework.pagination import PageNumberPagination
from authentication.pagination import CustomPageNumberPagination
from post.models import HiddenPost


class SmallPageNumberPagination(PageNumberPagination):
    page_size = 2


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'content', 'created_at', 'updated_at', 'image')


class ProfileSerializer(serializers.ModelSerializer):
    user_posts = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    vlogs_count = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    def get_user_posts(self, profile):
        user = self.context['request'].user
        posts = Post.objects.filter(user=profile.user).order_by('-created_at')
        if user.is_authenticated:
            hidden_post_ids = HiddenPost.objects.filter(user=user).values_list('post_id', flat=True)
            posts = posts.exclude(id__in=hidden_post_ids)
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(posts, self.context['request'])
        post_serializer = PostSerializer(page, many=True, context=self.context)
        return paginator.get_paginated_response(post_serializer.data).data

    def get_posts_count(self, profile):
        return Post.objects.filter(user=profile.user).count()

    def get_followers_count(self, profile):
        if profile.user:
            return profile.user.followers.count()
        return 0

    def get_following_count(self, profile):
        if profile.user:
            return profile.user.following.count()
        return 0
    
    def get_vlogs_count(self, profile):
        if profile.user:
            return profile.vlog_count()

    def get_is_following(self, profile):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=profile.user).exists()
        return False
  
    def update(self, instance, validated_data):
        avatar_data = None
        request = self.context.get('request')

        # Check if the 'avatar' field is present in the request data
        if request and request.data.get('avatar'):
            avatar_data = request.data.get('avatar')

        if avatar_data:
            instance.avatar = avatar_data

        # Update other fields
        instance.bio = validated_data.get('bio', instance.bio)
        instance.background_pic = validated_data.get('background_pic', instance.background_pic)

        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = ('id', 'username', 'bio', 'avatar', 'background_pic', 'created_at', 'updated_at', 'posts_count', 'following_count', 'followers_count', 'is_following', 'user_posts', 'hide_avatar', 'vlogs_count')


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(source='follower.username', read_only=True)
    following = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
