from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
import hashlib
import numpy as np

class Game(models.Model):
    name = models.CharField(max_length=200)

    def averaage_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(all_ratings)

    def __unicode__(self):
        return self.name

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    game = models.ForeignKey(Game)
    pub_date = models.DateTimeField('date published')
    user_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=200)
    rating = models.IntegerField(choices=RATING_CHOICES)


class Message(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True, blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

    def gravatar_url(self):
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Recommendation(models.Model):
    game = models.ForeignKey(Game)
    recommended_by = models.ForeignKey(User, related_name = "recommended_by")
    recommended_to = models.ForeignKey(User, related_name= "recommended_to")

class Discussion(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)
    creation_date = models.DateField(auto_now_add=True)
    invited_user = models.ManyToManyField(User, related_name='invited')
    closed = models.BooleanField(default=False)
    question = models.CharField(max_length=500)

class DiscussionComment(models.Model):
    discussion = models.ForeignKey(Discussion)
    user = models.ForeignKey(User)
    comment = models.CharField(max_length=500)
