from london import forms
from pages.models import Page
from pages import signals

__author__ = 'jpablo'



class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('text',)
        readonly = ('last_update', 'text')

    def initialize(self):
        self.fields['keywords'].widget = forms.ListByCommasTextInput()
        signals.page_form_initialize.send(sender=self)

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

        signals.page_form_clean.send(sender=self, cleaned_data=cleaned_data)
        return cleaned_data

    def save(self, commit=True, force_new=False):
        signals.page_form_pre_save.send(sender=self, instance=self.instance)
        obj = super(PageForm, self).save(commit, force_new)
        signals.page_form_post_save.send(sender=self, instance=obj)
        return obj

