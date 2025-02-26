# Generated by Django 5.1.4 on 2025-01-30 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_keyholder_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='spaceuser',
            name='keyholder_priority',
            field=models.IntegerField(default=-10),
        ),
        migrations.AddField(
            model_name='spaceuser',
            name='space_level',
            field=models.IntegerField(choices=[(0, 'User'), (30, 'Volunteer'), (70, 'Keyholder'), (100, 'Staff')], default=0),
        ),
        migrations.DeleteModel(
            name='Keyholder',
        ),
    ]
