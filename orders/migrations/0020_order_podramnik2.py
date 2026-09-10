import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0020_mount_operations'),
        ('orders', '0019_order_packages_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='podramnik2',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='orders_as_bridges', to='frames.podramnik',
                verbose_name='Перемычки (из справочника подрамников)',
                help_text='Вторая позиция подрамника (перемычки). Считается по цене записи, фиксированно.',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='podramnik_bridges',
            field=models.DecimalField(
                'Перемычки подрамника (м) — не используется',
                max_digits=8, decimal_places=2, blank=True, null=True,
                help_text='Устаревшее: раньше вводился метраж. Теперь перемычки выбираются из справочника.',
            ),
        ),
    ]
