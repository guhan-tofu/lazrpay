from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

# this is the sender model for users
class Sender(models.Model):
    sender_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    wallet_address = models.CharField(max_length=44, unique=True, null=True, blank=True)
    def __str__(self):
        if self.user:
            return f"{self.user.username} (ID: {self.sender_id})"
        return f"Sender (ID: {self.sender_id})"

# this runs when user signs up with social login
@receiver(user_signed_up)
def create_sender_for_social_login(request, user, **kwargs):
    Sender.objects.get_or_create(user=user, defaults={'wallet_address': None})

# this is the recipient model for emails
class Recipient(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

# this is the transaction model for transfers
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('failed', 'failed'),
        ('completed', 'completed'),
        ('processing', 'processing'),
    ]
    tx_id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(Sender, on_delete=models.CASCADE, related_name='sent_transactions')
    to_receiver = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='received_transactions')
    tx_hash = models.CharField(max_length=500, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=9, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    moonpay_transaction_id = models.CharField(max_length=64, null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
