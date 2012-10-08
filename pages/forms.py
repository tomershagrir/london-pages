from london import forms
from london.apps.admin.modules import BaseModuleForm
from london.apps.sites.models import Site
from london.apps.admin.app_settings import CURRENT_SITE_FILTER

from pages.models import Page
from pages import signals 


__author__ = 'jpablo'

class PageForm(BaseModuleForm):

    class Meta:
        model = Page
        exclude = ('text',)
        readonly = ('last_update', 'text')
        
    def get_initial(self, initial=None):
        initial = initial or super(PageForm, self).get_initial(initial)
        
        page_query = Page.query()
        if self.request.session[CURRENT_SITE_FILTER] != '':
            site = Site.query().get(pk = self.request.session[CURRENT_SITE_FILTER])
            page_query = page_query.filter(site=site)
        
        if self.instance['pk']: #exclude self page from the list of similar ones
            page_query = page_query.exclude(pk = self.instance['pk']).order_by('name')

        self.fields['parent_page'].queryset = page_query
        signals.page_form_initialize.send(sender=self, initial=initial)
        return initial

    def initialize(self):
        self.fields['keywords'].widget = forms.ListByCommasTextInput()
        self.fields['slug'].required = False

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        slug = cleaned_data['slug']
        
#        site = Site.query().get(pk = self.request.session[CURRENT_SITE_FILTER])
        all_pages = cleaned_data['site']['pages']
        pages = all_pages.filter(slug=slug)

        # Validation excludes current page
        if self.instance['pk']:
            pages = pages.exclude(pk=self.instance['pk'])

        # Validating duplicated slug
        if pages.count() > 0:
            raise forms.ValidationError('Another page with slug "%s" already exists for this site.' % slug,
                    field_name='slug')

        if 'is_home' in cleaned_data and cleaned_data['is_home']:
            try:
                home = all_pages.home('name')
                home = (home, cleaned_data['name'])[home is None]
            except:
                home = None
            if cleaned_data['name'] != home:
                raise forms.ValidationError('Page "%s" is already marked as home.' % cleaned_data['name'],
                        field_name='is_home')

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