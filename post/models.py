from django.db import models
from authentication.models import CustomUser
from profile_app.models import Profile
from django.db.models import Count


class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts', null=True)
    image = models.ImageField(upload_to='images/', blank=False, null=False)
    content = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.content} "

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.all().count()

    like_count.short_description = 'Like Count'
    comment_count.short_description = 'Comment Count'

    def top_reactions(self, top_n=3):
        """
        Retrieves the top N most used reactions for the post.
        """
        top_reactions = self.post_reactions.values('reaction_type').annotate(
            count=Count('reaction_type')
        ).order_by('-count')[:top_n]
        return top_reactions

    def top_reactions_display(self, top_n=3):
        """
        Formats the top reactions into a readable string with icons and counts.
        """
        top_reactions = self.top_reactions(top_n)
        reaction_icons = dict(Reaction.REACTION_CHOICES)
        formatted_reactions = [
            f"{reaction_icons.get(r['reaction_type'], r['reaction_type'])} ({r['count']})"
            for r in top_reactions
        ]
        return ", ".join(formatted_reactions) if formatted_reactions else "No Reactions"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.content[:20]}..."


class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"

    @classmethod
    def toggle_like(cls, post, user):
        try:
            like = cls.objects.get(post=post, user=user)
            like.delete()
            return False
        except cls.DoesNotExist:
            cls.objects.create(post=post, user=user)
            return True


class LikeCounter(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)


class CommentCounter(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)


class HiddenPost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hidden_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='hidden_by')

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} hidden post {self.post.id}"


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('love', '❤️ Love'),
        ('like', '👍 Like'),
        ('haha', '😂 Haha'),
        ('wow', '😮 Wow'),
        ('crying', '😭 Crying'),
        ('disgusting', '🤮 Disgusting'),
        ('liar', '🤥 Liar'),
        ('angry', '😡 Angry'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_reaction_per_user_per_post')
        ]

    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to post {self.post.id}"

    @classmethod
    def toggle_reaction(cls, post, user, reaction_type):
        """
        Toggles a user's reaction on a post. Removes the reaction if it's the same type; otherwise, updates it.
        """
        try:
            reaction = cls.objects.get(post=post, user=user)
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return False
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                return True
        except cls.DoesNotExist:
            cls.objects.create(post=post, user=user, reaction_type=reaction_type)
            return True
