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

# Solana imports for actual SOL transfers
from solana.rpc.api import Client
from solana.transaction import Transaction as SolanaTransaction
from solana.system_program import transfer, TransferParams
from solana.publickey import PublicKey
from solana.keypair import Keypair
import base58
import os
from dotenv import load_dotenv

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
    
    transaction = None
    if tx_hash:
        try:
            transaction = Transaction.objects.get(tx_hash=tx_hash)
        except Transaction.DoesNotExist:
            pass
    
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
    webhook_secret = "wk_test_wi418cZi42L1XErSspSiIuWnQSfutga8"
    signature = request.headers.get("Moonpay-Signature", "")
    body = request.body

    # Verify signature
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return HttpResponseForbidden("Invalid signature")

    data = json.loads(body)
    # Log the payload for debugging
    print("MoonPay Webhook Payload:", data)

    # Example: data['externalCustomerId'] should match your user/email
    # Example: data['status'] == 'completed' for successful payout
    if data.get("status") == "completed":
        # Try to find the transaction by tx_hash or email
        tx_hash = data.get("externalTransactionId")
        if tx_hash:
            try:
                txn = Transaction.objects.get(tx_hash=tx_hash)
                txn.status = "claimed"
                txn.save()
            except Transaction.DoesNotExist:
                pass  # Optionally log this
    return HttpResponse("OK")

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
    Simulate a crypto deposit to MoonPay for sandbox testing.
    This endpoint is called by the MoonPay widget's onInitiateDeposit handler.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('externalTransactionId')
        
        if not transaction_id:
            return JsonResponse({"error": "Missing externalTransactionId"}, status=400)
        
        # Find the transaction in our database
        try:
            transaction = Transaction.objects.get(tx_hash=transaction_id)
        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
        
        # Check if we should use local simulation mode (for testing)
        use_local_simulation = request.GET.get('local', 'false').lower() == 'true'
        
        if use_local_simulation:
            # Local simulation mode - no API call needed
            transaction.status = "deposit_initiated"
            transaction.save()
            
            return JsonResponse({
                "success": True,
                "message": "Deposit simulation successful (local mode)",
                "transaction_id": transaction_id,
                "note": "Local simulation mode - no MoonPay API call made"
            })
        
        # ACTUAL SOL TRANSFER TO MOONPAY WALLET
        # This is where we actually send the SOL to MoonPay's wallet
        try:
            # Get the MoonPay wallet address from the frontend request
            moonpay_wallet_address = data.get('moonpayWalletAddress')
            
            if not moonpay_wallet_address:
                return JsonResponse({
                    "error": "Missing MoonPay wallet address",
                    "details": "Please provide the current MoonPay wallet address"
                }, status=400)
            
            print(f"Using MoonPay wallet address from frontend: {moonpay_wallet_address}")
            
            # Get the amount to transfer
            sol_amount = float(transaction.amount)
            lamports = int(sol_amount * 1_000_000_000)
            
            print(f"Transferring {sol_amount} SOL ({lamports} lamports) to MoonPay wallet: {moonpay_wallet_address}")
            
            # Setup Solana connection
            connection = Client("https://api.devnet.solana.com")
            
            # Use the existing keypair (your system wallet that holds the SOL)
            # The keypair is already set up at the top of the file
            
            # MoonPay's wallet public key
            moonpay_pubkey = PublicKey(moonpay_wallet_address)
            
            # Create and send the transaction
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
            
            print("Sending SOL to MoonPay wallet...")
            resp = connection.send_transaction(txn, keypair)
            print(f"SOL transfer successful! Transaction ID: {resp.value}")
            
            # Update transaction status
            transaction.status = "deposit_initiated"
            transaction.save()
            
            # Now call MoonPay's API to notify them of the deposit
            import requests
            
            # MoonPay sandbox simulation endpoint
            simulation_url = "https://api.moonpay.com/v3/simulate/sell_transaction"
            
            # Your MoonPay secret key for API calls
            secret_key = "sk_test_bSuZag7HAnqGTJwEh4473JdxVMYpLoI0"
            
            # Prepare the simulation request
            simulation_data = {
                "externalTransactionId": transaction_id,
                "cryptoAmount": str(transaction.amount),
                "cryptoCurrencyCode": "sol",
                "walletAddress": moonpay_wallet_address,
                "transactionId": str(resp.value)  # The actual Solana transaction ID
            }
            
            # Make the API call to MoonPay
            headers = {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json"
            }
            
            try:
                print(f"Notifying MoonPay of deposit...")
                response = requests.post(simulation_url, json=simulation_data, headers=headers, timeout=30)
                
                print(f"MoonPay API Response: {response.status_code} - {response.text}")
                
                if response.status_code == 200:
                    return JsonResponse({
                        "success": True,
                        "message": "SOL transferred to MoonPay successfully!",
                        "transaction_id": transaction_id,
                        "solana_tx_id": str(resp.value),
                        "moonpay_wallet": moonpay_wallet_address,
                        "moonpay_response": response.json()
                    })
                else:
                    # SOL was transferred but MoonPay API failed
                    return JsonResponse({
                        "success": True,
                        "message": "SOL transferred to MoonPay, but notification failed",
                        "transaction_id": transaction_id,
                        "solana_tx_id": str(resp.value),
                        "moonpay_wallet": moonpay_wallet_address,
                        "moonpay_error": response.text
                    })
                    
            except requests.exceptions.RequestException as e:
                # SOL was transferred but MoonPay API call failed
                return JsonResponse({
                    "success": True,
                    "message": "SOL transferred to MoonPay, but notification failed",
                    "transaction_id": transaction_id,
                    "solana_tx_id": str(resp.value),
                    "moonpay_wallet": moonpay_wallet_address,
                    "moonpay_error": str(e)
                })
                
        except Exception as e:
            print(f"Error transferring SOL to MoonPay: {e}")
            return JsonResponse({
                "error": "Failed to transfer SOL to MoonPay",
                "details": str(e)
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"Unexpected error in simulate_moonpay_deposit: {e}")
        return JsonResponse({"error": str(e)}, status=500)