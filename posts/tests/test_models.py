from django.test import TestCase

from posts.models import Post, Group, User


class CommonModelsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            description="Test description"
        )
        cls.post = Post.objects.create(
            text='Начинаем тестировать проект!',
            author=User.objects.create(),
        )

    def test_verboses_post(self):
        post = CommonModelsTests.post
        field_verboses = {
            'text': 'Пост',
            'pub_date': 'Время публикации',
            'author': 'Автор',
            'group': 'Группа'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_verboses_group(self):
        group = CommonModelsTests.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Тег',
            'description': 'Описание'
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        post = CommonModelsTests.post
        field_help_text = {
            'text': 'Введите текст поста',
            'pub_date': 'Время публикации генерируется автоматически',
            'author': 'Ваше имя',
            'group': 'Выберите группу'
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_help_text_group(self):
        group = CommonModelsTests.group
        field_help_text = {
            'title': 'Введите заголовок группы',
            'slug': 'Введите осознаный тег группы',
            'description': 'Напишите описание группы'
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str_post(self):
        post = CommonModelsTests.post
        expected_str = post.text[:15]
        self.assertEquals(expected_str, str(post))

    def test_str_group(self):
        group = CommonModelsTests.group
        expected_str = group.title
        self.assertEquals(expected_str, str(group))
