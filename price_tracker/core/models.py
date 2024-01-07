from django.db import models


class BaseModel(models.Model):
    name = models.CharField(verbose_name='Name', max_length=200, unique=True)
    description = models.CharField(verbose_name='Description', max_length=500, blank=True)
    enabled = models.BooleanField(verbose_name='Enabled', default=True, help_text='Default: True')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last Updated')

    class Meta:
        abstract = True