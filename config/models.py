from django.urls import reverse

from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.cache import cache


class Category(MPTTModel):
    name = models.CharField('Имя', max_length=50, unique=True)
    """категории объявлений"""
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родитель"
    )
    slug = models.SlugField('url', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
        verbose_name = "Категория"




class FilterAdvert(models.Model):
    """"Фильтры"""
    name = models.CharField('Имя', max_length=50, unique=True)
    slug = models.SlugField('url', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Фильтр'
        verbose_name_plural = 'Фильтры'
        ordering = ["id"]


class DateAdvert(models.Model):
    """"Срок для объявления"""
    name = models.CharField('Имя', max_length=50, unique=True)
    slug = models.SlugField('url', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Срок'
        verbose_name_plural = 'Сроки'
        ordering = ["id"]



class Advert(models.Model):
    """Объявления"""
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    filters = models.ForeignKey(FilterAdvert, verbose_name='Фильтр', on_delete=models.CASCADE)
    date = models.ForeignKey(DateAdvert, verbose_name='Срок', on_delete=models.CASCADE)
    subject = models.CharField('Тема', max_length=200)
    description = models.TextField("Объявление", max_length=10000)
    images = models.ForeignKey('gallery.Gallery', verbose_name='Изображения', blank=True, null=True, on_delete=models.SET_NULL)
    file = models.FileField("Файл", upload_to='board/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=20, decimal_places=2)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    moderation = models.BooleanField('Модерация', default=False)
    # TODO: для slug генерить путь (user, subject)
    slug = models.SlugField('url', max_length=200, unique=True)
    rating = models.SmallIntegerField("Лайки", default=0)


    def __str__(self):
        return self.subject


    """Добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с объявлениями"""
    #def get_absolute_url(self):
        #return f'/advert/{self.id}'

    #def save(self, *args, **kwargs):
      #  super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
       # cache.delete(f'advert-{self.id}')  # затем удаляем его из кэша, чтобы сбросить его

    # def get_absolute_url(self):
    #     return reverse("advert-detail", kwargs={"category": self.category.slug, "slug": self.slug})

    def get_absolute_url(self):
       return reverse('advert-detail', kwargs={'pk': self.pk})

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.description[0:124] + '...'


    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class Comment(models.Model):
    commentAdvert = models.ForeignKey(Advert, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField("Объявление", max_length=10000)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    rating = models.SmallIntegerField("Комментарий", default=0)


    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class Reviews(models.Model):
    """Отзывы"""
    email = models.EmailField()
    user = models.CharField("Пользователь", max_length=100)
    text = models.TextField("Отзыв", max_length=5000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    advert = models.ForeignKey(Advert, verbose_name="Объявление", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.advert}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = 'Отзывы'



class Subscription(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )