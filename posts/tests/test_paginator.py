from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="TestUser")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(15):
            Post.objects.create(
                text=f'{i} запись',
                author=cls.user,
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page'].object_list), 10)

    def test_second_page_contains_five_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page'].object_list), 5)

    def test_first_page_in_group_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page'].object_list), 10)

    def test_second_page_in_group_contains_five_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group', kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page'].object_list), 5)
