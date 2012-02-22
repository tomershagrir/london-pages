from london import forms
from pages.models import Page

__author__ = 'jpablo'

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('text',)
        readonly = ('last_update', 'text')

    def initialize(self):
        self.fields['keywords'].widget = forms.ListByCommasTextInput()

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        slug = cleaned_data['slug']
        pages = cleaned_data['site']['pages'].filter(slug=slug)

        # Validation excludes current page
        if self.instance['pk']:
            pages = pages.exclude(pk=self.instance['pk'])

        # Validating duplicated slug
        if pages.count() > 0:
            raise forms.ValidationError('Another page with slug "%s" already exists for this site.'%slug, field_name='slug')

        return cleaned_data

    """
    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        slug = cleaned_data['slug']
        pages = cleaned_data['site']['pages']
        if pages.filter(slug=slug).count() > 0:
            self._errors['slug'] = ErrorList('slug',['duplicated slug'])
            del cleaned_data['slug']

        return cleaned_data
    """

