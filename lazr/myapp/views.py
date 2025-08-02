from django.shortcuts import render, redirect
from rest_framework import generics
from .models import Sender
from .serializers import SenderSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import Recipient, Transaction, Sender
from .serializers import RecipientSerializer, TransactionSerializer, SenderSerializer, SenderIdOnlySerializer
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
import hmac
import hashlib
import json
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction
import time

# Solana imports for actual SOL transfers
from solana.rpc.api import Client
from solana.transaction import Transaction as SolanaTransaction
from solana.system_program import transfer, TransferParams
from solana.publickey import PublicKey
from solana.keypair import Keypair
import base58
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Use the existing keypair setup
PRIVATE_KEY_BASE58 = os.getenv("PRIVATE_KEY_BASE58")  # Replace with your actual private key

# Decode the base64 string to get the raw private key bytes
private_key_bytes = base58.b58decode(PRIVATE_KEY_BASE58)

# Create a Keypair from the private key bytes
keypair = Keypair.from_secret_key(private_key_bytes)
print("Keypair : ", keypair.public_key)


# Create your views here.
def my_view(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def real_home(request):
    return render(request, 'real_home.html')

def my_receive_view(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    tx_hash = request.GET.get('tx_hash')
    if not tx_hash:
        return render(request, 'receive.html', {'error': 'No transaction specified.'})
    
    try:
        transaction = Transaction.objects.get(tx_hash=tx_hash)
    except Transaction.DoesNotExist:
        return render(request, 'receive.html', {'error': 'Transaction not found.'})
    
    # Check that the transaction was sent to the logged-in user's email
    if transaction.to_receiver.email != request.user.email:
        raise PermissionDenied("You do not have permission to claim this transaction.")
    
    return render(request, 'receive.html', {'transaction': transaction})

def my_receive_main_view(request):
    return render(request, 'receive_main.html')

def transak_claim_view(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    tx_hash = request.GET.get('tx_hash')
    if not tx_hash:
        return render(request, 'moonpay_claim.html', {'error': 'No transaction specified.'})
    
    try:
        transaction = Transaction.objects.get(tx_hash=tx_hash)
    except Transaction.DoesNotExist:
        return render(request, 'moonpay_claim.html', {'error': 'Transaction not found.'})
    
    # Check that the transaction was sent to the logged-in user's email
    if transaction.to_receiver.email != request.user.email:
        raise PermissionDenied("You do not have permission to claim this transaction.")
    
    return render(request, 'moonpay_claim.html', {'transaction': transaction})

def claim_success_view(request):
    return render(request, 'claim_success.html')

def deposit_success_view(request):
    """
    View for the deposit success page after successful SOL transfer to MoonPay
    """
    if not request.user.is_authenticated:
        return redirect('home')
    
    # Get transaction details from query parameters
    tx_hash = request.GET.get('tx_hash')
    solana_tx_id = request.GET.get('solana_tx_id')
    moonpay_wallet = request.GET.get('moonpay_wallet')
    
    print(f"Deposit success view - tx_hash: {tx_hash}, solana_tx_id: {solana_tx_id}, moonpay_wallet: {moonpay_wallet}")
    
    transaction = None
    if tx_hash:
        try:
            transaction = Transaction.objects.get(tx_hash=tx_hash)
            print(f"Found transaction: {transaction.amount} SOL to {transaction.to_receiver.email}")
        except Transaction.DoesNotExist:
            print(f"Transaction not found for tx_hash: {tx_hash}")
            # Try to find by the fallback transaction ID
            try:
                transaction = Transaction.objects.filter(status='deposit_initiated').first()
                if transaction:
                    print(f"Using fallback transaction: {transaction.amount} SOL to {transaction.to_receiver.email}")
            except:
                print("No fallback transaction found")
    
    context = {
        'transaction': transaction,
        'solana_tx_id': solana_tx_id,
        'moonpay_wallet': moonpay_wallet
    }
    
    return render(request, 'deposit_success.html', context)

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


# Decode the base64 string to get the raw private key bytes
private_key_bytes = base58.b58decode(PRIVATE_KEY_BASE58)

# Create a Keypair from the private key bytes
keypair = Keypair.from_secret_key(private_key_bytes)
print("Keypair : ", keypair.public_key)


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

#@method_decorator(csrf_exempt, name='dispatch')
class CreateRecipientView(generics.CreateAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [AllowAny]

class RecipientListView(generics.ListAPIView):
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [AllowAny] 

#@method_decorator(csrf_exempt, name='dispatch')
class CreateTransactionView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]  


class TransactionByEmailListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        email = self.kwargs['to_receiver_email']
        return Transaction.objects.filter(to_receiver__email=email, status="pending")


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
@method_decorator(csrf_exempt, name='dispatch')
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

class SenderIdView(generics.RetrieveAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderIdOnlySerializer
    permission_classes = [AllowAny]
    lookup_field = 'user'

@csrf_exempt
def moonpay_webhook(request):
    """
    Handle MoonPay webhook when they confirm receipt of SOL
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"MoonPay webhook received: {data}")
        
        # Check if this is a deposit confirmation
        if data.get('type') == 'transaction_updated' and data.get('status') == 'completed':
            deposit_id = data.get('depositId')
            
            if deposit_id:
                # Find transaction by deposit ID
                try:
                    transaction = Transaction.objects.get(tx_hash=deposit_id)
                    transaction.status = "completed"
                    transaction.save()
                    print(f"Transaction {deposit_id} marked as completed")
                except Transaction.DoesNotExist:
                    print(f"Transaction not found for deposit ID: {deposit_id}")
        
        return JsonResponse({"status": "ok"})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def test_moonpay_webhook(request):
    # For local testing only! No auth, no signature check.
    tx_hash = request.GET.get('tx_hash')
    if not tx_hash:
        return HttpResponse("Missing tx_hash", status=400)
    try:
        txn = Transaction.objects.get(tx_hash=tx_hash)
        txn.status = "claimed"
        txn.save()
        return HttpResponse(f"Transaction {tx_hash} marked as claimed (test mode).")
    except Transaction.DoesNotExist:
        return HttpResponse("Transaction not found", status=404)

@csrf_exempt
def simulate_moonpay_deposit(request):
    """
    Send SOL to MoonPay and wait for confirmation
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        moonpay_wallet_address = data.get('moonpayWalletAddress')
        deposit_id = data.get('moonpayDepositId')
        crypto_amount = data.get('cryptoAmount')
        external_transaction_id = data.get('externalTransactionId')
        
        print(f"Received MoonPay wallet: {moonpay_wallet_address}")
        print(f"Received deposit ID: {deposit_id}")
        print(f"Received crypto amount: {crypto_amount}")
        print(f"Received external transaction ID: {external_transaction_id}")
        
        if not moonpay_wallet_address:
            return JsonResponse({"error": "Missing MoonPay wallet address"}, status=400)
        
        # Find the SPECIFIC transaction by tx_hash, not just any pending transaction
        if external_transaction_id:
            try:
                transaction = Transaction.objects.get(tx_hash=external_transaction_id)
                print(f"Found specific transaction: {transaction.tx_hash} with status: {transaction.status}")
            except Transaction.DoesNotExist:
                return JsonResponse({"error": f"Transaction {external_transaction_id} not found"}, status=404)
        else:
            # Fallback to first pending transaction (for backward compatibility)
            transaction = Transaction.objects.filter(status='pending').first()
            if not transaction:
                return JsonResponse({"error": "No pending transactions found"}, status=404)
            print(f"Using fallback transaction: {transaction.tx_hash}")
        
        # Check if transaction has already been claimed
        if transaction.status != 'pending':
            return JsonResponse({"error": f"Transaction {transaction.tx_hash} has already been claimed (status: {transaction.status})"}, status=400)
        
        # Use the amount from MoonPay if provided, otherwise use transaction amount
        if crypto_amount:
            sol_amount = float(crypto_amount)
        else:
            sol_amount = float(transaction.amount)
            
        print(f"Using transaction: {sol_amount} SOL from transaction {transaction.tx_hash}")
        
        # Send SOL to MoonPay's provided wallet address
        lamports = int(sol_amount * 1_000_000_000)
        
        connection = Client("https://api.devnet.solana.com")
        moonpay_pubkey = PublicKey(moonpay_wallet_address)
        
        txn = SolanaTransaction()
        txn.add(
            transfer(
                TransferParams(
                    from_pubkey=keypair.public_key,
                    to_pubkey=moonpay_pubkey,
                    lamports=lamports
                )
            )
        )
        
        resp = connection.send_transaction(txn, keypair)
        print(f"SOL sent to MoonPay wallet {moonpay_wallet_address}: {resp.value}")
        
        # Update transaction status to completed so it won't show in pending
        transaction.status = "completed"
        transaction.save()
        
        print("=== SOL TRANSFER COMPLETE ===");
        print("✅ SOL sent to MoonPay wallet:", moonpay_wallet_address);
        print("✅ Solana transaction ID:", str(resp.value));
        print("✅ Transaction amount:", sol_amount, "SOL");
        print("✅ Transaction ID:", transaction.tx_hash);
        print("✅ Transaction status updated to 'completed'");
        print("✅ MoonPay should detect this automatically");
        print("=============================");
        
        return JsonResponse({
            "success": True,
            "message": "SOL sent to MoonPay successfully! MoonPay should detect this automatically.",
            "solana_tx_id": str(resp.value),
            "moonpay_wallet": moonpay_wallet_address
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def test_moonpay_notification(request):
    """
    Test endpoint to manually trigger MoonPay notification
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('externalTransactionId')
        moonpay_wallet_address = data.get('moonpayWalletAddress')
        solana_tx_id = data.get('solanaTxId')
        
        print(f"Testing MoonPay notification:")
        print(f"Transaction ID: {transaction_id}")
        print(f"MoonPay wallet: {moonpay_wallet_address}")
        print(f"Solana TX ID: {solana_tx_id}")
        
        # MoonPay sandbox simulation endpoint
        simulation_url = "https://api.moonpay.com/v3/simulate/sell_transaction"
        
        # Your MoonPay secret key for API calls
        secret_key = "sk_test_bSuZag7HAnqGTJwEh4473JdxVMYpLoI0"
        
        # Prepare the simulation request
        simulation_data = {
            "externalTransactionId": transaction_id,
            "cryptoAmount": "0.1",  # Default amount for testing
            "cryptoCurrencyCode": "sol",
            "walletAddress": moonpay_wallet_address,
            "transactionId": solana_tx_id
        }
        
        # Make the API call to MoonPay
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        print(f"Making API call to MoonPay...")
        response = requests.post(simulation_url, json=simulation_data, headers=headers, timeout=30)
        
        print(f"MoonPay API Response: {response.status_code} - {response.text}")
        
        return JsonResponse({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "request_data": simulation_data
        })
        
    except Exception as e:
        print(f"Error in test notification: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)