# Generated by Django 3.0.8 on 2020-07-26 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200726_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]