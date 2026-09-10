from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_order_podramnik2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='podramnik_bridges',
            field=models.DecimalField(
                'Перемычки: метры',
                max_digits=8, decimal_places=2, blank=True, null=True,
                help_text='Метраж перемычек. Стоимость = цена выбранной записи × метры.',
            ),
        ),
    ]
