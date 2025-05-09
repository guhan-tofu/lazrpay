from django.shortcuts import render
from rest_framework import generics
from .models import Sender
from .serializers import SenderSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import Recipient, Transaction, Sender
from .serializers import RecipientSerializer, TransactionSerializer, SenderSerializer

# Create your views here.
def my_view(request):
    return render(request, 'index.html')

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