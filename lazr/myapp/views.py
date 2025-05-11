from django.shortcuts import render, redirect
from rest_framework import generics
from .models import Sender
from .serializers import SenderSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import Recipient, Transaction, Sender
from .serializers import RecipientSerializer, TransactionSerializer, SenderSerializer
from django.contrib.auth import logout

# Create your views here.
def my_view(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def my_receive_view(request):
    return render(request, 'receive.html')

def logout_view(request):
    logout(request)
    return redirect("/")

from django.http import HttpResponse
from .utils import send_email

@csrf_exempt
def send_welcome_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse({"error": "Email required"}, status=400)
            success = send_email(email)
            if success:
                return JsonResponse({"status": "Email sent"})
            else:
                return JsonResponse({"error": "Email sending failed"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from solana.rpc.api import Client
from solana.transaction import Transaction as SolanaTransaction
from solana.system_program import transfer, TransferParams
from solana.publickey import PublicKey
from solana.keypair import Keypair
from base58 import b58decode

# Base58-encoded private key from Phantom Wallet
PRIVATE_KEY_BASE58 = "3CtQZJ3UGZSdnfkKWN4SH6yAYnNfwfhddFbQkLnrSfLYe22KqZS2MNvLVGqMweXgQBpsnpA8C4US67wWbdp2u9fc"  # Replace with your actual private key

# Decode the base64 string to get the raw private key bytes
private_key_bytes = b58decode(PRIVATE_KEY_BASE58)

# Create a Keypair from the private key bytes
keypair = Keypair.from_secret_key(private_key_bytes)
print("Keypair : ", keypair.public_key)

#DESTINATION = "4RjJu4S761irqRYKGydVNf3rfTjQa9mJiTPT8vsUxjJW"  # Receiver wallet

@csrf_exempt
def send_sol(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        print("Request received...")
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        recipient_address = data.get('recipient', '')
        tx_hash = data.get('tx_hash', '')

        print(f"Amount: {amount}, Recipient: {recipient_address}, Tx Hash: {tx_hash}")

        
        lamports = int(amount * 1_000_000_000)
        print(f"Lamports: {lamports}")
        
        connection = Client("https://api.devnet.solana.com")
        to_pubkey = PublicKey(recipient_address)
        
        txn = SolanaTransaction()
        txn.add(
            transfer(
                TransferParams(
                    from_pubkey=keypair.public_key,
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )
        )

        print("Sending transaction...")
        resp = connection.send_transaction(txn, keypair)
        print("Response:", resp)

        return JsonResponse({'txid': str(resp.value)})
    
    except Exception as e:
        print("Error occurred:", e)
        return JsonResponse({'error': str(e)}, status=500)



class CreateSenderView(generics.CreateAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = [AllowAny] # Adjust for auth needs

class SenderListView(generics.ListAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = [AllowAny] 


class CreateRecipientView(generics.CreateAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [AllowAny]

class RecipientListView(generics.ListAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [AllowAny] 

class CreateTransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]  



# Get Sender by Wallet Address
class SenderByWalletView(generics.RetrieveAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = [AllowAny]
    lookup_field = 'wallet_address'

# Get Recipient by Email
class RecipientByEmailView(generics.RetrieveAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [AllowAny]
    lookup_field = 'email'

class TransactionByIdView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
    lookup_field = 'tx_hash'  # Need to use tx_id later 


# Update Status of Transaction
class UpdateTransactionStatusView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
    lookup_field = 'tx_hash'  # Assuming tx_hash is unique

class UpdateWalletAddressView(generics.UpdateAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = [AllowAny]
    lookup_field = 'sender_id' 