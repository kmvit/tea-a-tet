import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0020_mount_operations'),
        ('orders', '0016_alter_order_package_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='foamboard',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='orders', to='frames.foamboard',
                verbose_name='Пенокартон (накатка)',
            ),
        ),
    ]
