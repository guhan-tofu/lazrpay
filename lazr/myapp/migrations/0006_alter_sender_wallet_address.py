from django.db import migrations, models
# this migration alters sender wallet address again
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0005_alter_sender_wallet_address'),
    ]
    operations = [
        migrations.AlterField(
            model_name='sender',
            name='wallet_address',
            field=models.CharField(blank=True, max_length=44, null=True, unique=True),
        ),
    ]
