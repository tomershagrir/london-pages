from london import forms

__author__ = 'jpablo'


class PageForm(forms.Form):
    name = forms.CharField(max_length=255)
    slug = forms.CharField(max_length=255)
    text = forms.TextField()