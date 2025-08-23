from django.db import migrations, models
# this migration adds moonpay_transaction_id and alters status
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0006_alter_sender_wallet_address'),
    ]
    operations = [
        migrations.AddField(
            model_name='transaction',
            name='moonpay_transaction_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('confirmed', 'confirmed'), ('failed', 'failed'), ('completed', 'completed'), ('processing', 'processing')], default='pending', max_length=10),
        ),
    ]
