from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0020_mount_operations'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='no_master_work',
            field=models.BooleanField(
                'Без работы столяра', default=False,
                help_text='Отметьте для пакетов: упаковка идёт бесплатно, работа столяру не начисляется.',
            ),
        ),
    ]
