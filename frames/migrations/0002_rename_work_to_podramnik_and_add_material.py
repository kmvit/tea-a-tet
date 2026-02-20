# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0001_initial'),
    ]

    operations = [
        # Переименование модели Work в Podramnik
        migrations.RenameModel(
            old_name='Work',
            new_name='Podramnik',
        ),
        # Изменение verbose_name для Podramnik
        migrations.AlterModelOptions(
            name='podramnik',
            options={'ordering': ['name'], 'verbose_name': 'Подрамник', 'verbose_name_plural': 'Подрамники'},
        ),
        # Создание новой модели Material
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена (руб)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Материал',
                'verbose_name_plural': 'Материалы',
                'ordering': ['name'],
            },
        ),
    ]
