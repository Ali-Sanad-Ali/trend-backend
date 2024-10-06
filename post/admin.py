from django.contrib import admin
from .models import Post, Comment, LikePost, HiddenPost
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'content')
    search_fields = ('user__username', 'post__user__username', 'content')
    list_filter = ('created_at',)

@admin.register(LikePost)
class LikePostAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'like_counter', 'comment_counter')
    search_fields = ('user__username', 'post__user__username')
    list_filter = ('created_at',)

    def like_counter(self, obj):
        if obj.post.likes.all():  # Check if there are any likes associated with the post
            return obj.post.likes.count()  # Get the count of likes for the post
        return 0  # Return 0 if there are no likes

    like_counter.short_description = 'Like Count'
    
    def comment_counter(self, obj):
        if obj.post.comments.all():
            return obj.post.comments.count()
        return 0
    

@admin.register(HiddenPost)
class HiddenPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    search_fields = ('user__username', 'post__id')
    list_filter = ('user', 'post')