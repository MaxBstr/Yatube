from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Группа не выбрана"

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 30, 'rows': 5})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 30, 'rows': 5})
        }
