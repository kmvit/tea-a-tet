# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0002_rename_work_to_podramnik_and_add_material'),
        ('orders', '0001_initial'),
    ]

    operations = [
        # Переименование поля work в podramnik
        migrations.RenameField(
            model_name='order',
            old_name='work',
            new_name='podramnik',
        ),
        # Обновление verbose_name для поля podramnik
        migrations.AlterField(
            model_name='order',
            name='podramnik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='frames.podramnik', verbose_name='Подрамник'),
        ),
    ]
