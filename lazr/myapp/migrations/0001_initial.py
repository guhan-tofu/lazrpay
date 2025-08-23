import django.db.models.deletion
from django.db import migrations, models
# this is the initial migration
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Recipient",
            fields=[
                ("recipient_id", models.AutoField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Sender",
            fields=[
                ("sender_id", models.AutoField(primary_key=True, serialize=False)),
                ("wallet_address", models.CharField(max_length=44, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("tx_id", models.AutoField(primary_key=True, serialize=False)),
                ("tx_hash", models.CharField(max_length=100, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("confirmed", "confirmed"),
                            ("failed", "failed"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                (
                    "from_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_transactions",
                        to="myapp.sender",
                    ),
                ),
                (
                    "to_receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_transactions",
                        to="myapp.recipient",
                    ),
                ),
            ],
        ),
    ]
