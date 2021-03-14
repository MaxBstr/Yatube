from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Введите заголовок группы')
    slug = models.SlugField(
        unique=True,
        null=True,
        verbose_name='Тег',
        help_text='Введите осознаный тег группы')
    description = models.TextField(
        verbose_name='Описание',
        help_text='Напишите описание группы')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Пост',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации',
        help_text='Время публикации генерируется автоматически',
        db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Ваше имя')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        blank=True,
        null=True,
        help_text='Выберите группу',
        related_name='posts')
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите комментарий к посту')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        blank=True,
        null=True,
        help_text='Укажите пост для комментирования',
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
        help_text='Ваше имя')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания комментария',
        help_text='Время комментирования генерируется автоматически')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created']


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Имя автора')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Имя подписчика')

    def __str__(self):
        return f'{self.user.username}->@{self.author.username}'

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscriber'
            )
        ]
        ordering = ['-user']
