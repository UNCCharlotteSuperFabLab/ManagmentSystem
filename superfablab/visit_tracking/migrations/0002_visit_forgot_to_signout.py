# Generated by Django 5.1.4 on 2025-01-14 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visit_tracking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='forgot_to_signout',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
