from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django import forms

import shutil
import tempfile

from posts.models import Group, Post, Follow


User = get_user_model()


class CommonViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test-desc'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_correct_templates_used(self):
        """ Тест корректного использования шаблонов """
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group', kwargs={
                'slug': self.group.slug}),
            'new.html': reverse('posts:new_post')
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_shows_correct_context(self):
        """ Тест шаблона index.html с context """
        response = self.authorized_client.get(reverse('posts:index'))

        post_on_index = response.context['page'].object_list[0]
        self.assertEqual(post_on_index, self.post, (
            ' Context главной страницы не прошел проверку '
        ))

    def test_group_shows_correct_context(self):
        """ Тест шаблона group.html с context """
        response = self.authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': self.group.slug}
        ))

        self.assertEqual(response.context['group'], self.group, (
            'Тестирование context страницы группы прошло неудачно'
        ))

    def test_new_post_shows_correct_context(self):
        """ Тест шаблона new.html с context """
        response = self.authorized_client.get(reverse('posts:new_post'))

        form_text_field = response.context['form'].fields['text']
        self.assertIsInstance(form_text_field, forms.fields.CharField)

    def test_post_exists_on_main_page(self):
        """ Тест на появление поста на главной страницы после создания """
        # Первый запрос
        response = self.authorized_client.get(reverse('posts:index'))
        count_before = len(response.context['page'])

        # Создаем новую запись в бд
        created_post = Post.objects.create(
            text='текст',
            author=self.user,
            group=self.group
        )

        # Второй запрос
        response = self.authorized_client.get(reverse('posts:index'))
        count_after = len(response.context['page'])
        new_post = response.context['page'].object_list[0]

        # Тестируем!
        self.assertEqual(count_before + 1, count_after, (
            ' Пост не добавился на главную страницу '
        ))
        self.assertEqual(created_post, new_post, (
            ' Созданный пост не соответствует посту на главной странице '
        ))

    def test_post_exists_on_related_group_page(self):
        """ Тест на появление поста на странице группы после создания """
        response = self.authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': self.group.slug}
        ))

        test_post = response.context['page'].object_list[0]
        self.assertEqual(self.post, test_post, (
            "Пост не добавился на страницу группы"
        ))

    def test_post_not_belongs_to_alien_group(self):
        """ Тест на непринадлежность к чужой группе """
        # Создаем 'чужую' группу
        alien_group = Group.objects.create(
            title='alien',
            slug='alien-slug',
            description='alien-desc'
        )

        # Делаем запрос к новой группе
        response = self.authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': alien_group.slug}
        ))

        # Делаем вид, что существуют посты в 'чужой' группе
        alien_posts = response.context['page']

        # Проверяем, что наш пост не оказался в списке постов 'чужой' группы
        self.assertNotIn(self.post, alien_posts, (
            ' Пост принадлежит чужой группе '
        ))

    def test_profile_shows_correct_context(self):
        """ Тест на корректный context на странице пользователя """
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))

        test_author = response.context['author']
        self.assertEqual(test_author, self.user, (
            ' Указан неверный автор '
        ))

        posts = response.context['page']
        self.assertIn(self.post, posts, (
            ' Пост автора не отображается на странице автора '
        ))

    def test_post_page_shows_correct_context(self):
        """ Тест на корректный context на странице поста """
        response = self.authorized_client.get(reverse(
            'posts:post',
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        ))

        test_author = response.context['author']
        self.assertEqual(test_author, self.user, (
            ' На странице поста указан неверный автор '
        ))

        cur_post = response.context['post']
        self.assertEqual(cur_post, self.post, (
            ' На странице поста отображается другой пост или его нет '
        ))

    def test_post_edit_shows_correct_context(self):
        """ Тест на корректный context при редактировании поста"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        ))

        cur_post = response.context['post']
        self.assertEqual(cur_post, self.post, (
            ' На странице редактирования поста \
            отображается другой пост или его нет '
        ))

        test_author = response.context['author']
        self.assertEqual(test_author, self.user, (
            ' На странице редактирования поста указан неверный автор '
        ))

        form_text_field = response.context['form'].fields['text']
        self.assertIsInstance(form_text_field, forms.fields.CharField)

    def test_index_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на index.html """
        response = self.authorized_client.get(reverse('posts:index'))

        test_image = response.context['page'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на главной странице неверно отображается '
        ))

    def test_profile_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на profile.html """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))

        test_image = response.context['page'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице профиля неверно отображается '
        ))

    def test_post_with_image_context_correct(self):
        """ Тестирование картинки в context на отдельном посте """
        response = self.authorized_client.get(reverse(
            'posts:post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        ))
        test_image = response.context['post'].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице поста неверно отображается '
        ))

    def test_group_post_with_image_context_correct(self):
        """ Тестирование картинки в context поста на group.html """
        response = self.authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': self.group.slug}))

        test_image = response.context['page'].object_list[0].image
        self.assertEqual(test_image, self.post.image, (
            ' Картинка поста на странице группы неверно отображается '
        ))

    def test_cache(self):
        """ Тестирование работы кэша"""
        # Делаем запрос до создания поста
        response_before = self.authorized_client.get(reverse('posts:index'))

        # Создаем пост
        post = Post.objects.create(text='test', author=self.user)
        response_after = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=post.id).delete()

        # Удалили пост из бд, но на странице должен еще быть
        response_after_delete = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(response_after.content, response_after_delete.content)

        # Пост должен быть удален с главной страницы
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index'))
        # До создания был 1 пост из setUp
        self.assertEqual(
            response_after_clear.context['paginator'].count,
            response_before.context['paginator'].count)

    def test_authorized_user_follow(self):
        """ Тестирование подписки авторизованным пользователем """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        follow_obj = Follow.objects.get(author=self.user, user=new_user)
        self.assertIsNotNone(follow_obj, (
            ' Пользователь не смог подписаться на пользователя '))

    def test_authorized_user_unfollow(self):
        """ Тестирование отписки авторизованным пользователем """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        # Follow (works previous test)
        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        # Unfollow
        new_authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        ))

        self.assertEqual(Follow.objects.count(), 0, (
            'Пользователь не смог отписаться от пользователя'))

    def test_following_posts_showing_to_followers(self):
        """ Тестирование отображения постов отслеживаемых авторов """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        response = new_authorized_client.get(reverse('posts:follow_index'))
        following_post = response.context['page'].object_list[0]
        self.assertEqual(following_post, self.post, (
            'Посты отслеживаемого автора не отображаются на странице избранных'
        ))

        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['paginator'].count, 0, (
            'Посты неотслеживаемого автора появляются на странице избранных'
        ))
