from london import forms
from pages.models import Page
from pages import signals 
from london.apps.admin.modules import BaseModuleForm

from images import add_image_field_to_sender_form

signals.page_form_initialize.connect(add_image_field_to_sender_form)

__author__ = 'jpablo'

class PageForm(BaseModuleForm):

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

    def default_context(self, *args, **kwargs):
        return {
            'object_verbose_name': self._meta.model._meta.verbose_name,
            'object_verbose_name_plural': self._meta.model._meta.verbose_name_plural
        }

