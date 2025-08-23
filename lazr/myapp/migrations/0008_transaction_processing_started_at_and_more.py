from django.db import migrations, models
# this migration adds processing_started_at and alters status
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0007_transaction_moonpay_transaction_id_and_more'),
    ]
    operations = [
        migrations.AddField(
            model_name='transaction',
            name='processing_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('confirmed', 'confirmed'), ('failed', 'failed'), ('completed', 'completed'), ('processing', 'processing')], default='pending', max_length=10),
        ),
    ]
