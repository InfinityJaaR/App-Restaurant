# Generated by Django 5.1.3 on 2024-11-25 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platillo',
            name='disponibilidad',
        ),
        migrations.AddField(
            model_name='platillo',
            name='cantidad_maxima',
            field=models.IntegerField(default=0),
        ),
    ]