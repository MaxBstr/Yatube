# Generated by Django 2.2.9 on 2021-01-07 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20210107_1752'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Post', 'verbose_name_plural': 'Posts'},
        ),
    ]
