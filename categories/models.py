from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(
        max_length=150, unique=True, db_index=True, verbose_name='نام دسته‌بندی'
    )
    slug = models.SlugField(
        max_length=160, unique=True, db_index=True, blank=True, verbose_name='شناسه متنی'
    )
    description = models.TextField(blank=True, default='', verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ آخرین بروزرسانی')

    class Meta:
        ordering = ['name']
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base = slugify(self.name) or 'category'
            slug = base
            n = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)
