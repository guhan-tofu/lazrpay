from django.db import models

# Create your models here.



class Sender(models.Model):
    sender_id = models.AutoField(primary_key=True)
    wallet_address = models.CharField(max_length=44, unique=True)

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
    #amount = models.DecimalField(max_digits=18, decimal_places=9)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    #network = models.CharField(max_length=10, default='devnet')
    #initiated_at = models.DateTimeField(auto_now_add=True)
    #confirmed_at = models.DateTimeField(null=True, blank=True)
