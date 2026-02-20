# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_passepartout_order_passepartout_length_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='frames_data',
            field=models.TextField(blank=True, null=True, verbose_name='Данные всех рамок'),
        ),
    ]
