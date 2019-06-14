# Generated by Django 2.2.2 on 2019-06-13 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_contactchat'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactchat',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contactchat',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
