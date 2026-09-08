from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_order_foamboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='podramnik_bridges',
            field=models.DecimalField(
                'Перемычки подрамника (м)',
                max_digits=8, decimal_places=2, blank=True, null=True,
                help_text='Метраж рейки на перемычки (по длине, по ширине, усиление углов). '
                          'Стоимость = метраж × цена выбранной рейки.',
            ),
        ),
    ]
