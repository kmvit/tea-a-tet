from django.db import migrations, models


OPERATION_TYPES = [
    ('rama', 'Изготовление рамы'),
    ('rama2', 'Изготовление двойных рам'),
    ('rama3', 'Изготовление тройных рам'),
    ('passepartout', 'Паспарту'),
    ('passepartout2', 'Паспарту второе'),
    ('passepartout3', 'Паспарту третье'),
    ('backing', 'Резка подкладки'),
    ('backing2', 'Резка подкладки2'),
    ('glass', 'Резка стекла'),
    ('glass2', 'Резка стекла2'),
    ('podramnik', 'Подрамник'),
    ('foamboard', 'Накатка на пенокартон'),
    ('trosik_mount', 'Крепление тросика'),
    ('podveski_mount', 'Крепление подвесок'),
    ('stretch', 'Натяжка холста'),
    ('molding', 'Молдинг'),
    ('complexity_frame', 'Сложность рамы'),
    ('complexity_pp', 'Сложность паспарту'),
    ('complexity_mount', 'Крепление объекта'),
    ('package', 'Упаковка'),
]


def seed_mount_ops(apps, schema_editor):
    TechOperation = apps.get_model('frames', 'TechOperation')
    defaults = [
        ('trosik_mount', 'Крепление тросика', 100),
        ('podveski_mount', 'Крепление подвесок', 100),
    ]
    for op_type, name, rate in defaults:
        if not TechOperation.objects.filter(operation_type=op_type).exists():
            TechOperation.objects.create(
                operation_type=op_type, name=name,
                size_from=None, size_to=None, rate=rate,
            )


def unseed_mount_ops(apps, schema_editor):
    TechOperation = apps.get_model('frames', 'TechOperation')
    TechOperation.objects.filter(operation_type__in=['trosik_mount', 'podveski_mount']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('frames', '0019_rename_stretch_price_per_meter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='techoperation',
            name='operation_type',
            field=models.CharField('Вид операции', max_length=32, choices=OPERATION_TYPES, db_index=True),
        ),
        migrations.RunPython(seed_mount_ops, unseed_mount_ops),
    ]
