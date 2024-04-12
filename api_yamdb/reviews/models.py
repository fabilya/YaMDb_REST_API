from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator)
from django.db import models
from django.db.models import CharField

from api_yamdb.settings import (
    DEFAULT_CONFIRMATION_CODE,
    CONFIRMATION_CODE_LENGTH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from .validators import username_validator, year_validator

NOTE_MAX_LENGTH = 30


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    username = CharField(
        'имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator],
    )
    bio = models.TextField(
        'о себе',
        blank=True,
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=max(
            CONFIRMATION_CODE_LENGTH,
            len(DEFAULT_CONFIRMATION_CODE),
        ),
        default=DEFAULT_CONFIRMATION_CODE,
    )
    email = models.EmailField(
        'адрес почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=USERNAME_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        'фамилия',
        max_length=USERNAME_MAX_LENGTH,
        blank=True,
    )
    role = models.CharField(
        'роль',
        choices=ROLES,
        max_length=max(len(role) for role, _ in ROLES),
        default=USER,
    )
    REQUIRED_FIELDS = ('email',)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff


class NameSlugModel(models.Model):
    name = models.CharField(
        'название',
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'идентификатор',
        max_length=SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Genre(NameSlugModel):
    class Meta(NameSlugModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=NAME_MAX_LENGTH,
    )
    year = models.PositiveIntegerField(
        'год',
        validators=(year_validator,)
    )
    description = models.TextField(
        'описание',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category',
        verbose_name='категория',
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='жанр'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} -> {self.title}'


class NoteModel(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    text = models.TextField('текст')
    pub_date = models.DateTimeField('дата создания', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.text[:NOTE_MAX_LENGTH]


class Review(NoteModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta(NoteModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review',
            )
        ]


class Comment(NoteModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )

    class Meta(NoteModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
