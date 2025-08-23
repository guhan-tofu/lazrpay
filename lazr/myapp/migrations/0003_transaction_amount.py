from django.db import migrations, models
# this migration adds amount field
class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0002_alter_transaction_tx_hash"),
    ]
    operations = [
        migrations.AddField(
            model_name="transaction",
            name="amount",
            field=models.DecimalField(decimal_places=9, default=0, max_digits=18),
        ),
    ]
