# Generated by Django 5.1.3 on 2024-11-28 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_mascampos_carnet_alter_mascampos_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mascampos',
            name='direccion',
            field=models.CharField(blank=True, default='Sin dirección', max_length=255),
        ),
        migrations.AlterField(
            model_name='mascampos',
            name='telefono',
            field=models.CharField(default='000000000', max_length=9),
        ),
    ]