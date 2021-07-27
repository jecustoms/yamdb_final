from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import year_validator


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', _('user')
        MODERATOR = 'moderator', _('moderator')
        ADMIN = 'admin', _('admin')

    bio = models.TextField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Информация о пользователе'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email адрес'
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Имя пользователя'
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Пользовательская роль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Genre(models.Model):
    name = models.CharField(
        max_length=25,
        verbose_name='Название жанра'
    )
    slug = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название категории')
    slug = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        db_index=True,
        max_length=100,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        blank=True,
        verbose_name='Год',
        validators=[year_validator]
    )
    description = models.TextField(verbose_name='Описание произведения')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5,
        verbose_name='Рейтинг'
    )
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
