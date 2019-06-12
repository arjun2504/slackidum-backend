# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create your models here.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class ContactBook(models.Model):
	id = models.AutoField(primary_key=True)
	book_owner = models.ForeignKey(User, blank=False, null=False, related_name="book_owner", on_delete=models.CASCADE)
	user_id = models.ForeignKey(User, blank=False, null=False, related_name="user_id", on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

