from django.test import TestCase, Client
from django.urls import reverse


class TestAboutURLs(TestCase):
    def setUp(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_urls_guest(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200, (
            ' Ошибка доступа к странице об авторе '
        ))

        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200, (
            ' Ошбика доступа к странице о технологиях '
        ))

    def test_urls_use_correct_template(self):
        template_url = 'about/about.html'
        reversed_urls = ['about:author', 'about:tech']

        for url in reversed_urls:
            response = self.guest_client.get(reverse(url))
            self.assertTemplateUsed(response, template_url)
