import django.core.validators
import django.db.models.deletion
import medals.related_models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedalImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=medals.related_models.medal_image_upload_to, verbose_name='تصویر')),
                ('image_type', models.CharField(choices=[('front', 'رو'), ('back', 'پشت'), ('edge', 'لبه'), ('packaging', 'بسته‌بندی'), ('certificate', 'گواهی'), ('invoice', 'فاکتور'), ('other', 'سایر')], default='other', max_length=20, verbose_name='نوع تصویر')),
                ('caption', models.CharField(blank=True, default='', max_length=255, verbose_name='عنوان')),
                ('ordering', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')),
                ('is_primary', models.BooleanField(db_index=True, default=False, verbose_name='تصویر اصلی')),
                ('original_filename', models.CharField(blank=True, default='', max_length=255, verbose_name='نام فایل اصلی')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='حجم فایل')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')),
                ('medal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='medals.medal', verbose_name='مدال')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_medal_images', to=settings.AUTH_USER_MODEL, verbose_name='آپلودکننده')),
            ],
            options={'verbose_name': 'تصویر مدال', 'verbose_name_plural': 'تصاویر مدال', 'ordering': ['ordering', 'id']},
        ),
        migrations.CreateModel(
            name='MedalFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=medals.related_models.medal_file_upload_to, verbose_name='فایل')),
                ('file_type', models.CharField(choices=[('certificate', 'گواهی'), ('invoice', 'فاکتور'), ('document', 'سند'), ('other', 'سایر')], default='other', max_length=20, verbose_name='نوع فایل')),
                ('original_filename', models.CharField(blank=True, default='', max_length=255, verbose_name='نام فایل اصلی')),
                ('content_type', models.CharField(blank=True, default='', max_length=100, verbose_name='نوع محتوا')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='حجم فایل')),
                ('notes', models.CharField(blank=True, default='', max_length=255, verbose_name='یادداشت')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')),
                ('medal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='medals.medal', verbose_name='مدال')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_medal_files', to=settings.AUTH_USER_MODEL, verbose_name='آپلودکننده')),
            ],
            options={'verbose_name': 'فایل مدال', 'verbose_name_plural': 'فایل‌های مدال', 'ordering': ['-uploaded_at']},
        ),
        migrations.CreateModel(
            name='MedalPurchaseRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name='تاریخ خرید')),
                ('location', models.CharField(blank=True, default='', max_length=255, verbose_name='محل خرید')),
                ('seller', models.CharField(blank=True, default='', max_length=150, verbose_name='فروشنده')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='قیمت')),
                ('currency', models.CharField(blank=True, choices=[('IRR', 'Iranian Rial'), ('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('TRY', 'Turkish Lira'), ('AED', 'UAE Dirham'), ('OTHER', 'Other')], default='', max_length=10, verbose_name='واحد پول')),
                ('notes', models.TextField(blank=True, default='', verbose_name='یادداشت')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_purchase_records', to=settings.AUTH_USER_MODEL, verbose_name='ایجادکننده')),
                ('medal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_records', to='medals.medal', verbose_name='مدال')),
            ],
            options={'verbose_name': 'سوابق خرید', 'verbose_name_plural': 'سوابق خرید', 'ordering': ['-purchase_date', '-id']},
        ),
        migrations.CreateModel(
            name='MedalValuationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(0)], verbose_name='ارزش')),
                ('currency', models.CharField(blank=True, choices=[('IRR', 'Iranian Rial'), ('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('TRY', 'Turkish Lira'), ('AED', 'UAE Dirham'), ('OTHER', 'Other')], default='', max_length=10, verbose_name='واحد پول')),
                ('valuation_date', models.DateField(verbose_name='تاریخ قیمت‌گذاری')),
                ('source', models.CharField(blank=True, default='', max_length=255, verbose_name='منبع')),
                ('notes', models.TextField(blank=True, default='', verbose_name='یادداشت')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_valuation_records', to=settings.AUTH_USER_MODEL, verbose_name='ایجادکننده')),
                ('medal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='valuation_records', to='medals.medal', verbose_name='مدال')),
            ],
            options={'verbose_name': 'سوابق قیمت‌گذاری', 'verbose_name_plural': 'سوابق قیمت‌گذاری', 'ordering': ['-valuation_date', '-id']},
        ),
    ]
