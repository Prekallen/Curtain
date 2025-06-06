# Generated by Django 5.1.5 on 2025-04-13 09:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='기본키')),
                ('customer', models.CharField(blank=True, max_length=100, null=True, verbose_name='고객명')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='전화번호')),
                ('address', models.TextField(verbose_name='주소')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=18, verbose_name='총액')),
                ('down_pay', models.DecimalField(decimal_places=2, default=0, max_digits=18, verbose_name='계약금')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=18, verbose_name='잔금')),
                ('writer', models.CharField(blank=True, max_length=100, null=True, verbose_name='작성자')),
                ('writer_phone', models.CharField(max_length=20, verbose_name='작성자_전화번호')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='주문 일자')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='마지막 수정일')),
                ('const_date', models.DateTimeField(blank=True, null=True, verbose_name='시공일')),
                ('const_preferred_time', models.CharField(blank=True, choices=[('morning', '오전 (09:00 ~ 12:00)'), ('afternoon', '오후 (13:00 ~ 18:00)'), ('evening', '저녁 (19:00 이후)'), ('specific', '특정 시간')], max_length=10, null=True, verbose_name='시공 희망 시간대')),
                ('specific_const_time', models.TimeField(blank=True, null=True, verbose_name='특정 시공 시간')),
                ('complete', models.BooleanField(default=False, verbose_name='완료 여부')),
                ('custom_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='customer.customer')),
                ('manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.manager', verbose_name='작성 담당자')),
            ],
            options={
                'verbose_name': '계약',
                'verbose_name_plural': '계약',
                'db_table': 'contract',
            },
        ),
        migrations.CreateModel(
            name='Blind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='속 커튼 이름')),
                ('size', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='치수')),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='폭')),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='높이')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='단가')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='총 가격')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blinds', to='contract.contract')),
            ],
            options={
                'unique_together': {('contract', 'name', 'size')},
            },
        ),
        migrations.CreateModel(
            name='Etc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='속 커튼 이름')),
                ('size', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='치수')),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='폭')),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='높이')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='단가')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='총 가격')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='etc', to='contract.contract')),
            ],
            options={
                'unique_together': {('contract', 'name', 'size')},
            },
        ),
        migrations.CreateModel(
            name='InnerCurtain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='속 커튼 이름')),
                ('size', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='치수')),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='폭')),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='높이')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='단가')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='총 가격')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inner_curtains', to='contract.contract')),
            ],
            options={
                'unique_together': {('contract', 'name', 'size')},
            },
        ),
        migrations.CreateModel(
            name='OuterCurtain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='속 커튼 이름')),
                ('size', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='치수')),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='폭')),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='높이')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='단가')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='총 가격')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outer_curtains', to='contract.contract')),
            ],
            options={
                'unique_together': {('contract', 'name', 'size')},
            },
        ),
    ]
