from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
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
            group=cls.group
        )

    def test_urls_guest(self):
        """ Тесты для гостя """
        urls = {
            '/': 200,
            f'/group/{StaticURLTests.group.slug}/': 200,
            '/new/': 302
        }

        for url, expected_status in urls.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_authorized(self):
        """ Тесты для авторизованного пользователя """
        urls = {
            '/': 200,
            f'/group/{StaticURLTests.group.slug}/': 200,
            '/new/': 200
        }

        for url, expected_status in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_urls_uses_correct_template(self):
        """ URL-адрес использует соответствующий шаблон. """
        templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{StaticURLTests.group.slug}/',
            'new.html': '/new/',
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_profile(self):
        """ Тест на доступ к профилю анонимного пользователя """
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username})
        )

        self.assertEqual(response.status_code, 200, (
            ' Ошибка при тестировании страницы пользователя '
        ))

    def test_urls_edit_post_for_clients(self):
        """ Тест на ограничение доступа к редактированию поста """
        alien_user = User.objects.create(username='Alien')
        authorized_alien_client = Client()
        authorized_alien_client.force_login(alien_user)

        params = {
            'username': self.user.username,
            'post_id': self.post.id
        }

        # Тестируем анонимного пользователя
        response = self.guest_client.get(reverse(
            'posts:post_edit',
            kwargs=params))
        self.assertNotEqual(response.status_code, 200, (
            ' Страница редактирования доступна анонимному пользователю '
        ))

        # Тестируем автора поста
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs=params))
        self.assertEqual(response.status_code, 200, (
            ' Страница редактирования не доступна автору поста '
        ))

        # Тестируем авторизованного чужого пользователя
        response = authorized_alien_client.get(reverse(
            'posts:post_edit',
            kwargs=params))
        self.assertNotEqual(response.status_code, 200, (
            ' Страница редактирования доступна чужому пользователю '
        ))

    def test_post_edit_use_correct_template(self):
        """ Тест на корректный шаблон в редактировании поста """
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': 1
            })
        )
        self.assertTemplateUsed(response, 'new.html', (
            ' Неправильный шаблон в редактировании поста '
        ))

    def test_post_edit_not_author_redirect(self):
        """ Тест на редирект не авторов поста """
        # Для анонимного пользователя
        params = {
            'username': self.user.username,
            'post_id': self.post.id
        }
        response = self.guest_client.get(reverse(
            'posts:post_edit',
            kwargs=params),
            follow=True
        )
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/'
             f'{params["username"]}/{params["post_id"]}/edit/'),
            status_code=302)

        # Для авторизованого чужого пользователя
        alien_user = User.objects.create(username='Alien')
        authorized_alien_client = Client()
        authorized_alien_client.force_login(alien_user)

        response = authorized_alien_client.get(reverse(
            'posts:post_edit',
            kwargs=params),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post', kwargs=params),
            status_code=302)

        def test_url_404_error(self):
            """ Тест на код возврата 404 """
            response = self.guest_client.get('/test')
            self.assertEqual(response.status_code, 404)

        def test_url_404_error_uses_correct_template(self):
            """ Тест на кастомный шаблон при ошибке 404 """
            response = self.guest_client.get('/test')
            self.assertTemplateUsed(response, 'misc/404.html')
