from django.db import migrations, models
# this migration alters tx_hash field
class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0001_initial"),
    ]
    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="tx_hash",
            field=models.CharField(max_length=500, unique=True),
        ),
    ]
