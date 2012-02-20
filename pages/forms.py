from london import forms
from london.forms.base import ErrorList
from pages.models import Page

__author__ = 'jpablo'

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('text',)
        readonly = ('last_update', 'text')

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        slug = cleaned_data['slug']
        pages = cleaned_data['site']['pages']
        if pages.filter(slug=slug).count() > 0:
            self._errors['slug'] = ErrorList('slug',['duplicated slug'])
            del cleaned_data['slug']

        return cleaned_data
