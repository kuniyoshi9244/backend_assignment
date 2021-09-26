# Generated by Django 3.1 on 2021-09-23 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterUniqueTogether(
            name='followrelation',
            unique_together=set(),
        ),
    ]