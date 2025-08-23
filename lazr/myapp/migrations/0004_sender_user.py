import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
# this migration adds user to sender
class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_transaction_amount"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="sender",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
