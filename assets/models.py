from django.db import models

NULLABLE = {'blank': True, 'null': True}

class UnityAsset(models.Model):
    title = models.CharField(max_length=255, verbose_name='наименование')
    rating = models.CharField(max_length=50, **NULLABLE, verbose_name='рейтинг')
    rating_count = models.CharField(max_length=50, **NULLABLE, verbose_name='количество оценок')
    publisher = models.CharField(max_length=255, verbose_name='автор публикации')
    link = models.URLField(unique=True, verbose_name='ссылка')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'объект'
        verbose_name_plural = 'объекты'
        ordering = ('pk',)
