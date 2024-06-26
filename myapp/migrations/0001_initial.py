# Generated by Django 5.0.3 on 2024-05-14 02:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pekerjaan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_pekerjaan', models.CharField(max_length=255)),
                ('harga_total_pekerjaan', models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='SubPekerjaan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kuantiti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('satuan', models.CharField(max_length=50)),
                ('harga_satuan', models.DecimalField(decimal_places=2, max_digits=10)),
                ('harga_total', models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ('pekerjaan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.pekerjaan')),
            ],
        ),
    ]
