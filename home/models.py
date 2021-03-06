from django.db import models

# Create your models here.

from django.db import models
from users.models import User
import sys
from django.dispatch import receiver
from home.notifications import send_push_message

class Category(models.Model):

    # Fields
    title = models.CharField(max_length=255)
    description = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created',)

    def __str__(self):
        return str(self.title)


class Item(models.Model):
    STATUS_CHOICES = (
        ("A", "Active"),
        ("L", "Lost"),
        ("S", "Stolen"))

    title = models.CharField(max_length=255)
    key = models.CharField(max_length=255, blank=False, null=False)
    user = models.ForeignKey(User, related_name="item_user", on_delete=models.PROTECT)
    category = models.ForeignKey(Category, related_name="item_category", on_delete=models.PROTECT)
    desc = models.TextField(default="", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="A")
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Items'
        ordering = ('-created',)

    def __str__(self):
        return self.title


class OTP(models.Model):
    otp = models.CharField(max_length=4, default="")
    phone_number = models.CharField(max_length=25, blank=False, null=False, default="")
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'OTP'
        ordering = ('-created',)

    def __str__(self):
        return str(self.otp)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="user_sender", on_delete=models.PROTECT)
    receiver = models.ForeignKey(User, related_name="user_receiver", on_delete=models.PROTECT)
    content = models.TextField(default="")
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name_plural = 'Messages'
        ordering = ('-created',)

    def __str__(self):
        return str(self.pk)


@receiver(models.signals.post_save, sender=Message)
def message_notify(sender, instance, *args, **kwargs):
    title = "{} send you a message".format(instance.sender.first_name)
    devices = DeviceInfo.objects.filter(user=instance.receiver, is_active=True)
    for device in devices:
        if device.push_token:
            send_push_message(device.push_token, title)


class DeviceInfo(models.Model):
    user = models.ForeignKey(User, related_name="device_user", on_delete=models.PROTECT)
    device_id = models.CharField(max_length=128, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)
    push_token = models.CharField(max_length=256, null=True, default=None)

    class Meta:
        verbose_name_plural = 'Devices'
        ordering = ('-created',)

    def __str__(self):
        return str(self.pk)

