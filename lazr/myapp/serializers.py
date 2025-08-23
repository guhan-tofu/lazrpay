from rest_framework import serializers
from .models import Sender, Recipient, Transaction
from django.contrib.auth.models import User
# this is for user info
class UserInfoSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
# this is for sender model
class SenderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Sender
        fields = ['sender_id', 'username', 'email', 'wallet_address']
class SenderIdOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = ['sender_id']
class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ['recipient_id', 'email']
# this is for transaction model
class TransactionSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(source='from_user.id', read_only=True)
    to_receiver_email = serializers.EmailField(source='to_receiver.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.user.email', read_only=True)
    class Meta:
        model = Transaction
        fields = [
            'tx_id',
            'from_user',
            'from_user_id',
            'from_user_email',
            'to_receiver',
            'to_receiver_email',
            'tx_hash',
            'amount',
            'status',
            'moonpay_transaction_id',
        ]
        read_only_fields = ['tx_id']

