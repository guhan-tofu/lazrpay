from rest_framework import serializers
from .models import Sender, Recipient, Transaction


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = ['sender_id', 'wallet_address']

class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ['recipient_id', 'email']

class TransactionSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(source='from_user.id', read_only=True)
    to_receiver_email = serializers.EmailField(source='to_receiver.email', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'tx_id',
            'from_user',
            'from_user_id',
            'to_receiver',
            'to_receiver_email',
            'tx_hash',
            'status',
        ]
        read_only_fields = ['tx_id']

