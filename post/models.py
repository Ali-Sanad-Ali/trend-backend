from django.db import models
from authentication.models import CustomUser
from profile_app.models import Profile


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
        # Count the number of likes related to this post
        return self.likes.count()

    def comment_count(self):
        # Count the number of comments related to this post
        return self.comments.all().count()

    like_count.short_description = 'Like Count'
    comment_count.short_description = 'Comment Count'


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
        ('crying', '😭 crying'),
        ('disgusting', '🤮 disgusting'),
        # Add more or remove reactions as needed
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to post {self.post.id}"

    @classmethod
    def toggle_reaction(cls, post, user, reaction_type):
        """
        Toggle a reaction. If the reaction exists, remove it. Otherwise, create it.
        """
        try:
            reaction = cls.objects.get(post=post, user=user, reaction_type=reaction_type)
            reaction.delete()
            return False
        except cls.DoesNotExist:
            cls.objects.create(post=post, user=user, reaction_type=reaction_type)
            return True

    @property
    def reaction_count(self):
        """
        Property to count the total number of reactions for this post.
        """
        return Reaction.objects.filter(post=self.post).count()