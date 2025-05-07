from django.urls import path
from . import views

urlpatterns = [
    path("", views.my_view),
    path('sender/create/', views.CreateSenderView.as_view(), name='create-sender'),
    path('senders/', views.SenderListView.as_view(), name='list-sender-transactions'),
    path('recipients/', views.RecipientListView.as_view(), name='list-recipients'),
    path('recipient/create/', views.CreateRecipientView.as_view(), name='create-recipient'),
    path('transaction/create/', views.CreateTransactionView.as_view(), name='create-transaction'),
    path('transactions/', views.TransactionListView.as_view(), name='list-transactions'),
    path("sender/by_wallet/<str:wallet_address>/", views.SenderByWalletView.as_view(), name="get_sender_by_wallet"),
    path("recipient/by_email/<str:email>/", views.RecipientByEmailView.as_view(), name="get_recipient_by_email"),
]

# Compare this snippet from lazr/lazr/urls.py:
# from django.contrib import admin