from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об авторе проекта'
        context['about'] = 'Об авторе'
        context['text'] = 'Полезный короткий текст'
        context['text_about'] = 'Текст страницы "Об авторе"'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О технологиях проекта'
        context['about'] = 'О технологиях'
        context['text'] = 'Полезный короткий текст'
        context['text_about'] = 'Текст страницы "О технологиях"'
        return context
