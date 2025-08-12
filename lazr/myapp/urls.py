from django.urls import path
from . import views

urlpatterns = [
    path("welcome", views.my_view, name="index"),
    path("real_home", views.real_home, name="real_home"),
    path("", views.home , name="home"),
    path("receive/", views.my_receive_view),
    path("receive_main/", views.my_receive_main_view, name="receive_main"),
    path('sender/create/', views.CreateSenderView.as_view(), name='create-sender'),
    path('senderid/<int:user>/', views.SenderIdView.as_view(), name='sender-id'),
    path('senders/', views.SenderListView.as_view(), name='list-sender-transactions'),
    path('recipients/', views.RecipientListView.as_view(), name='list-recipients'),
    path('recipient/create/', views.CreateRecipientView.as_view(), name='create-recipient'),
    path('transaction/create/', views.CreateTransactionView.as_view(), name='create-transaction'),
    path('transactions/', views.TransactionListView.as_view(), name='list-transactions'),
    path("sender/by_wallet/<str:wallet_address>/", views.SenderByWalletView.as_view(), name="get_sender_by_wallet"),
    path("recipient/by_email/<str:email>/", views.RecipientByEmailView.as_view(), name="get_recipient_by_email"),
    path("transaction/by_txid/<str:tx_hash>/", views.TransactionByIdView.as_view(), name="get_transaction_by_txid"),
    path("transaction/by_email/<str:to_receiver_email>/", views.TransactionByEmailListView.as_view(), name="get_transaction_by_email"),
    # New non-breaking history endpoint
    path("transactions/history/<str:email>/", views.TransactionHistoryByEmailView.as_view(), name="transactions_history_by_email"),
    # New utility endpoints
    path("moonpay/receipt/<str:external_id>/", views.moonpay_receipt, name="moonpay_receipt"),
    path("moonpay/map-transaction/", views.map_moonpay_transaction, name="map_moonpay_transaction"),
    path("update/status/<str:tx_hash>/", views.UpdateTransactionStatusView.as_view(), name="update_transaction_status"),
    path('sender/update-wallet/<str:sender_id>/', views.UpdateWalletAddressView.as_view(), name='update-wallet'),
    path("email/send/", views.send_welcome_email, name="send_welcome_email"),
    path("sol/send/", views.send_sol, name="send_sol"),
    path("moonpay-claim/", views.transak_claim_view, name="moonpay_claim"),
    path("claim-success/", views.claim_success_view, name="claim_success"),
    path("deposit-success/", views.deposit_success_view, name="deposit_success"),
    path("claim-error/", views.claim_error_view, name="claim_error"),
    path("logout", views.logout_view, name="logout"),
    path("moonpay/webhook/", views.moonpay_webhook, name="moonpay_webhook"),
    path("moonpay/test-webhook/", views.test_moonpay_webhook, name="test_moonpay_webhook"),
    path("moonpay/simulate-deposit/", views.simulate_moonpay_deposit, name="simulate_moonpay_deposit"),
    path("moonpay/test-notification/", views.test_moonpay_notification, name="test_moonpay_notification"),
    path("moonpay/abandon/", views.abandon_processing, name="abandon_processing"),
]

# Compare this snippet from lazr/lazr/urls.py:
# from django.contrib import admin