from django.db import migrations, models
# this migration alters sender wallet address
class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0004_sender_user"),
    ]
    operations = [
        migrations.AlterField(
            model_name="sender",
            name="wallet_address",
            field=models.CharField(blank=True, default="", max_length=44, unique=True),
        ),
    ]
