from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_order_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='package_quantity',
            field=models.PositiveIntegerField('Количество упаковки', default=1, blank=True, null=True),
        ),
    ]
