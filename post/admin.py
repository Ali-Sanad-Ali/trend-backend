from django.contrib import admin
from .models import Post, Comment, LikePost, HiddenPost, Reaction

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
        return obj.post.likes.count() if obj.post.likes.exists() else 0
    like_counter.short_description = 'Like Count'

    def comment_counter(self, obj):
        return obj.post.comments.count() if obj.post.comments.exists() else 0
    comment_counter.short_description = 'Comment Count'

@admin.register(HiddenPost)
class HiddenPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    search_fields = ('user__username', 'post__id')
    list_filter = ('user', 'post')

# Add the Reaction model to the admin site
@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'reaction_type', 'created_at')
    search_fields = ('user__username', 'post__content', 'reaction_type')
    list_filter = ('created_at', 'reaction_type')

