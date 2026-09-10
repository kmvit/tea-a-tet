from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_order_podramnik_bridges'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='packages_data',
            field=models.TextField(
                'Упаковки (список)', blank=True, null=True,
                help_text='JSON-список id упаковок заказа. В поле «Упаковка» хранится первая (совместимость).',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='package_quantity',
            field=models.PositiveIntegerField(
                'Количество упаковки', default=1, blank=True, null=True,
                help_text='Не используется: упаковок может быть несколько, список в packages_data.',
            ),
        ),
    ]
