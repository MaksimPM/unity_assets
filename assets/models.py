from django.db import models

NULLABLE = {'blank': True, 'null': True}

class UnityAsset(models.Model):
    title = models.CharField(max_length=255, verbose_name='наименование')
    rating = models.CharField(max_length=50, **NULLABLE, verbose_name='рейтинг')
    rating_count = models.CharField(max_length=50, **NULLABLE, verbose_name='количество оценок')
    publisher = models.CharField(max_length=255, verbose_name='автор публикации')
    link = models.URLField(unique=True, verbose_name='ссылка')
    file_size = models.CharField(max_length=255, **NULLABLE, verbose_name='размер файла')
    price = models.CharField(max_length=255, **NULLABLE, verbose_name='цена')
    release_date = models.CharField(max_length=255, **NULLABLE, verbose_name='дата релиза')
    version = models.CharField(max_length=255, **NULLABLE, verbose_name='версия')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'объект'
        verbose_name_plural = 'объекты'
        ordering = ('pk',)
