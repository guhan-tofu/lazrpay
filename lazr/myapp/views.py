from django.shortcuts import render, redirect
from django.contrib.auth import logout

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import never_cache

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Sender, Recipient, Transaction
from .serializers import (
    SenderSerializer,
    RecipientSerializer,
    TransactionSerializer,
    SenderIdOnlySerializer,
)

import os
import json
import base58
import requests
from dotenv import load_dotenv
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import timedelta

# Solana imports for actual SOL transfers
from solana.rpc.api import Client
from solana.transaction import Transaction as SolanaTransaction
from solana.system_program import transfer, TransferParams
from solana.publickey import PublicKey
from solana.keypair import Keypair


load_dotenv()

def render_forbidden(request, message="Access forbidden"):
    """
    Render forbidden.html with proper security headers and HTTP 403 status
    """
    response = render(request, 'forbidden.html')
    response.status_code = 403
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'
    response['X-XSS-Protection'] = '1; mode=block'
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

# Use the existing keypair setup
PRIVATE_KEY_BASE58 = os.getenv("PRIVATE_KEY_BASE58")  # Replace with your actual private key

# Decode the base64 string to get the raw private key bytes
private_key_bytes = base58.b58decode(PRIVATE_KEY_BASE58)

# Create a Keypair from the private key bytes
keypair = Keypair.from_secret_key(private_key_bytes)

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
        return render_forbidden(request)

    return render(request, 'receive.html', {'transaction': transaction})


def my_receive_main_view(request):
    return render(request, 'receive_main.html')


def transak_claim_view(request):
    if not request.user.is_authenticated:
        return redirect('home')

    tx_hash = request.GET.get('tx_hash')
    if not tx_hash:
        return render(request, 'moonpay_claim.html', {'error': 'No transaction specified.', 'MOONPAY_API_KEY': os.getenv('MOONPAY_API_KEY', '')})

    try:
        transaction = Transaction.objects.get(tx_hash=tx_hash)
    except Transaction.DoesNotExist:
        return render(request, 'moonpay_claim.html', {'error': 'Transaction not found.', 'MOONPAY_API_KEY': os.getenv('MOONPAY_API_KEY', '')})

    # Check that the transaction was sent to the logged-in user's email
    if transaction.to_receiver.email != request.user.email:
        return render_forbidden(request)

    # Auto-reset stale processing sessions (e.g., user closed/refresh mid-flow)
    if transaction.status == 'processing' and transaction.processing_started_at:
        ttl_minutes = int(os.getenv('CLAIM_PROCESSING_TTL_MINUTES', '10'))
        if timezone.now() - transaction.processing_started_at > timedelta(minutes=ttl_minutes):
            transaction.status = 'pending'
            transaction.processing_started_at = None
            transaction.save(update_fields=['status', 'processing_started_at'])

    # Check if transaction is already completed
    if transaction.status == 'completed':
        # Redirect to a success page or show message that transaction is already completed
        return redirect(f'/deposit-success/?tx_hash={tx_hash}&already_completed=true')

    return render(request, 'moonpay_claim.html', {'transaction': transaction, 'MOONPAY_API_KEY': os.getenv('MOONPAY_API_KEY', '')})


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
    already_completed = request.GET.get('already_completed', 'false').lower() == 'true'

    transaction = None
    if tx_hash:
        try:
            transaction = Transaction.objects.get(tx_hash=tx_hash)
        except Transaction.DoesNotExist:
            # Try to find by the fallback transaction ID
            try:
                transaction = Transaction.objects.filter(status='deposit_initiated').first()
            except:
                pass

    context = {
        'transaction': transaction,
        'solana_tx_id': solana_tx_id,
        'moonpay_wallet': moonpay_wallet,
        'already_completed': already_completed
    }

    return render(request, 'deposit_success.html', context)


def claim_error_view(request):
    tx_hash = request.GET.get('tx_hash')
    message = request.GET.get('message', 'An error occurred during your claim.')
    expected = request.GET.get('expected')
    context = { 'tx_hash': tx_hash, 'message': message, 'expected': expected }
    return render(request, 'claim_error.html', context)


def logout_view(request):
    logout(request)
    return redirect("/")


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


@csrf_exempt
def send_sol(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        # Require strong authorization; disable in production by default
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not getattr(request.user, 'is_staff', False):
            return JsonResponse({'error': 'Forbidden'}, status=403)
        if os.getenv('ENABLE_SEND_SOL', 'false').lower() != 'true':
            return JsonResponse({'error': 'Endpoint disabled'}, status=403)

        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        recipient_address = data.get('recipient', '')
        tx_hash = data.get('tx_hash', '')

        lamports = int(amount * 1_000_000_000)

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

        resp = connection.send_transaction(txn, keypair)

        return JsonResponse({'txid': str(resp.value)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class CreateSenderView(generics.CreateAPIView):
    queryset = Sender.objects.all()
    serializer_class = SenderSerializer
    permission_classes = [AllowAny]  # Adjust for auth needs


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


# Add: Full transaction history by recipient email (non-breaking new endpoint)
class TransactionHistoryByEmailView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        email = self.kwargs['email']
        return Transaction.objects.filter(to_receiver__email=email).order_by('-tx_id')


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

        # Check if this is a deposit confirmation
        if data.get('type') == 'transaction_updated' and data.get('status') == 'completed':
            deposit_id = data.get('depositId')

            if deposit_id:
                # Find transaction by deposit ID
                try:
                    transaction = Transaction.objects.get(tx_hash=deposit_id)
                    transaction.status = "completed"
                    transaction.save()
                except Transaction.DoesNotExist:
                    pass

        return JsonResponse({"status": "ok"})

    except Exception as e:
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
        # Enforce authenticated recipient only
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        data = json.loads(request.body)
        moonpay_wallet_address = data.get('moonpayWalletAddress')
        deposit_id = data.get('moonpayDepositId')
        # Client-provided amount is validated against server-side value
        client_crypto_amount_raw = data.get('cryptoAmount')
        external_transaction_id = data.get('externalTransactionId')

        if not moonpay_wallet_address:
            return JsonResponse({"error": "Missing MoonPay wallet address"}, status=400)

        # Find the SPECIFIC transaction by tx_hash and lock it for idempotency
        if not external_transaction_id:
            return JsonResponse({"error": "Missing external transaction id"}, status=400)

        # Atomic lock to enforce single processing
        with db_transaction.atomic():
            try:
                transaction = (
                    Transaction.objects.select_for_update().get(tx_hash=external_transaction_id)
                )
            except Transaction.DoesNotExist:
                return JsonResponse({"error": f"Transaction {external_transaction_id} not found"}, status=404)

            # Ensure the requestor is the intended recipient
            if transaction.to_receiver.email != request.user.email:
                return render_forbidden(request)

            # Enforce state machine: only pending can proceed; processing is a lock
            if transaction.status == 'completed':
                return JsonResponse({"error": "Transaction already completed"}, status=400)
            if transaction.status == 'processing':
                return JsonResponse({"error": "Transaction is already being processed"}, status=409)
            if transaction.status != 'pending':
                return JsonResponse({"error": f"Invalid transaction state: {transaction.status}"}, status=400)

            # Validate client-reported amount matches server-side amount within tolerance
            try:
                # Some SDKs pass strings; convert carefully
                client_crypto_amount = float(str(client_crypto_amount_raw)) if client_crypto_amount_raw is not None else None
            except (ValueError, TypeError):
                client_crypto_amount = None

            expected_amount = float(transaction.amount)
            if client_crypto_amount is None:
                return JsonResponse({"error": "Missing or invalid amount from provider"}, status=400)
            # Allow tiny float variance (1e-9 SOL)
            if abs(client_crypto_amount - expected_amount) > 1e-9:
                return JsonResponse({
                    "error": "Amount mismatch. Please use the provided claim flow for the exact received amount.",
                    "expected_amount": expected_amount,
                    "error_code": "AMOUNT_MISMATCH"
                }, status=400)

            # Set to processing to lock further attempts
            transaction.status = 'processing'
            transaction.processing_started_at = timezone.now()
            transaction.save(update_fields=['status', 'processing_started_at'])

        # Always use the server-side transaction amount
        sol_amount = float(transaction.amount)

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

        # Mark completed after successful transfer
        transaction.status = "completed"
        transaction.save(update_fields=["status"])

        return JsonResponse({
            "success": True,
            "message": "SOL sent to MoonPay successfully! MoonPay should detect this automatically.",
            "solana_tx_id": str(resp.value),
            "moonpay_wallet": moonpay_wallet_address
        })

    except Exception as e:
        # Best-effort: if we set status to processing earlier but failed later,
        # revert to pending to allow retry. We avoid broad DB scans here; only adjust
        # if we can resolve the transaction id from the request body.
        try:
            data = json.loads(request.body or '{}')
            external_transaction_id = data.get('externalTransactionId')
            if external_transaction_id:
                txn = Transaction.objects.filter(tx_hash=external_transaction_id, status='processing').first()
                if txn:
                    txn.status = 'pending'
                    txn.save(update_fields=['status'])
        except Exception:
            pass
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

        # MoonPay sandbox simulation endpoint
        simulation_url = "https://api.moonpay.com/v3/simulate/sell_transaction"

        # Use env-based MoonPay secret key
        secret_key = os.getenv("MOONPAY_SECRET_KEY", "")

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

        response = requests.post(simulation_url, json=simulation_data, headers=headers, timeout=30)

        return JsonResponse({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text,
            "request_data": simulation_data
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_POST
@csrf_exempt
def abandon_processing(request):
    try:
        data = json.loads(request.body or '{}')
        external_id = data.get('externalTransactionId') or request.GET.get('tx_hash')
        if not external_id:
            return JsonResponse({"success": False, "error": "Missing transaction id"}, status=400)
        try:
            txn = Transaction.objects.get(tx_hash=external_id)
        except Transaction.DoesNotExist:
            return JsonResponse({"success": False, "error": "Transaction not found"}, status=404)
        # Only intended recipient can abandon
        if request.user.is_authenticated and txn.to_receiver.email != request.user.email:
            return render_forbidden(request)
        if txn.status == 'processing':
            txn.status = 'pending'
            txn.processing_started_at = None
            txn.save(update_fields=['status', 'processing_started_at'])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_POST
@csrf_exempt
def map_moonpay_transaction(request):
    try:
        data = json.loads(request.body or '{}')
        external_id = data.get('externalTransactionId')
        moonpay_tx_id = data.get('moonpayTransactionId')
        if not external_id or not moonpay_tx_id:
            return JsonResponse({"success": False, "error": "Missing parameters"}, status=400)
        try:
            txn = Transaction.objects.get(tx_hash=external_id)
        except Transaction.DoesNotExist:
            return JsonResponse({"success": False, "error": "Transaction not found"}, status=404)
        # Optional: Only allow mapping for the authenticated recipient
        if request.user.is_authenticated and txn.to_receiver.email != request.user.email:
            return render_forbidden(request)
        txn.moonpay_transaction_id = moonpay_tx_id
        txn.save(update_fields=["moonpay_transaction_id"])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def moonpay_receipt(request, external_id: str):
    """
    Resolve MoonPay receipt URL from our external transaction id (tx_hash).
    Returns { "receipt_url": str | null }
    """
    try:
        # 1) Prefer stored mapping if present
        try:
            txn = Transaction.objects.get(tx_hash=external_id)
            if txn.moonpay_transaction_id:
                return JsonResponse({
                    "receipt_url": f"https://buy.moonpay.com/transaction_receipt?transactionId={txn.moonpay_transaction_id}"
                })
        except Transaction.DoesNotExist:
            txn = None

        secret_key = os.getenv("MOONPAY_SECRET_KEY", "")
        mp_id = None
        if secret_key:
            headers = {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json"
            }
            # Try documented external identifier endpoint
            try:
                primary_url = f"https://api.moonpay.com/v3/sell_transactions/external_transaction_id/{external_id}"
                resp = requests.get(primary_url, headers=headers, timeout=20)
                if resp.status_code == 200:
                    data = resp.json() or {}
                    mp_id = data.get("id") or data.get("transactionId")
            except Exception:
                pass

            # Fallback to list with query param
            if not mp_id:
                try:
                    fallback_url = "https://api.moonpay.com/v3/sell_transactions"
                    params = {"externalTransactionId": external_id}
                    resp2 = requests.get(fallback_url, headers=headers, params=params, timeout=20)
                    if resp2.status_code == 200:
                        data2 = resp2.json()
                        # Some tenants return list, some return object with 'data'
                        if isinstance(data2, list):
                            first = data2[0] if data2 else None
                        else:
                            first = (data2 or {}).get('data', [{}])[0] if (data2 or {}).get('data') else None
                        if first:
                            mp_id = first.get("id") or first.get("transactionId")
                except Exception:
                    pass

            # Extra fallback to v1 path if needed
            if not mp_id:
                try:
                    v1_url = "https://api.moonpay.com/v1/sell_transactions"
                    params = {"externalTransactionId": external_id}
                    resp3 = requests.get(v1_url, headers=headers, params=params, timeout=20)
                    if resp3.status_code == 200:
                        data3 = resp3.json()
                        if isinstance(data3, list) and data3:
                            first = data3[0]
                            mp_id = first.get("id") or first.get("transactionId")
                except Exception:
                    pass

        if mp_id:
            # Persist mapping for future direct linking
            if txn and not txn.moonpay_transaction_id:
                txn.moonpay_transaction_id = mp_id
                txn.save(update_fields=["moonpay_transaction_id"])
            return JsonResponse({
                "receipt_url": f"https://buy.moonpay.com/transaction_receipt?transactionId={mp_id}"
            })

        return JsonResponse({"receipt_url": None})
    except Exception as e:
        return JsonResponse({"receipt_url": None, "error": str(e)}, status=200)