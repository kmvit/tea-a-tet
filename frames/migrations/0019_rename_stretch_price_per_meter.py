from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0018_delete_work_delete_workpricesettings'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stretch',
            old_name='price_per_sqm',
            new_name='price_per_meter',
        ),
        migrations.AlterField(
            model_name='stretch',
            name='price_per_meter',
            field=models.DecimalField('Цена за метр (руб)', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='stretch',
            name='stock_quantity',
            field=models.DecimalField(
                'Количество на складе (кв.м)',
                max_digits=12,
                decimal_places=2,
                default=0,
                help_text='Не используется: натяжка — работа мастера, материал приносит клиент, со склада не списывается.',
            ),
        ),
    ]
