# Generated by Django 2.2.6 on 2021-03-14 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['-user']},
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='unique_subscriber'),
        ),
    ]
