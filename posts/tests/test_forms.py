from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse

import shutil
import tempfile

from posts.models import Post, Group


User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group = Group.objects.create(
            slug='test-slug',
            title='TestGroup',
            description='test-desc'
        )
        cls.post = Post.objects.create(
            text='TestPost',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_record_in_db_after_form(self):
        """ Тест на добавление записи """
        count_before = Post.objects.count()
        form_data = {
            'text': 'NewPost',
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )

        self.assertEqual(count_before, 1)
        self.assertEqual(count_before + 1, Post.objects.count(), (
            ' Пост не был создан '
        ))

        # Посты отсортированы от самых новых
        new_post = response.context['page'][0]
        self.assertEqual(new_post.text, form_data['text'], (
            ' Текст нового поста не соответствует данным формы '
        ))
        self.assertEqual(new_post.group, self.group, (
            ' Группа нового поста не соответствует данным формы '
        ))

    def test_changes_in_db_after_editing(self):
        """ Тест на изменения поста после редактирования """
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            data={'text': 'новый текст'},
            follow=True
        )

        edited_post = response.context['post']
        self.post.refresh_from_db()
        self.assertEqual(self.post, edited_post, (
            ' Редактирование поста провалено '
        ))

    def test_record_with_image_in_db_after_form(self):
        """ Тестируем создание поста с картинкой после отправки формы """
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
        count_before = Post.objects.count()
        form_data = {
            'text': 'Test',
            'image': uploaded,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )

        # Самый новый пост
        new_post = response.context['page'][0]
        self.assertEqual(count_before + 1, Post.objects.count(), (
            ' Пост с картинкой не был создан '
        ))
        new_post.refresh_from_db()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group, self.group)

    def test_authorized_can_comment(self):
        """ Только авторизованный пользователь может комментировать """
        form_data = {
            'text': 'Test-text',
            'author': self.user,
            'post': self.post
        }

        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )
        new_comment = response.context['comments']
        count_before = len(new_comment)
        self.assertEqual(new_comment[0].text, form_data['text'], (
            ' Комментарий авторизованного пользователя не создан '
        ))

        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )

        self.assertEqual(count_before, self.post.comments.count(), (
            ' Неавторизованный пользователь добавил комментарий '
        ))
