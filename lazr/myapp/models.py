from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# 1. First, let's update the Sender model to include email
# models.py
from django.dispatch import receiver
from allauth.account.signals import user_signed_up


class Sender(models.Model):
    sender_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    wallet_address = models.CharField(max_length=44, unique=True, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} (ID: {self.sender_id})"
        return f"Sender (ID: {self.sender_id})"
    

@receiver(user_signed_up)
def create_sender_for_social_login(request, user, **kwargs):
    """
    Create a Sender instance when a user signs up via social auth
    """
    # Create the sender without a wallet address initially
    # The wallet address will be assigned later when the user connects their wallet
    Sender.objects.get_or_create(user=user, defaults={'wallet_address': None})

class Recipient(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('failed', 'failed'),
    ]

    tx_id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(Sender, on_delete=models.CASCADE, related_name='sent_transactions')
    to_receiver = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='received_transactions')
    tx_hash = models.CharField(max_length=500, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=9, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    #network = models.CharField(max_length=10, default='devnet')
    #initiated_at = models.DateTimeField(auto_now_add=True)
    #confirmed_at = models.DateTimeField(null=True, blank=True)
