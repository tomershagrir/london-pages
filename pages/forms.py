from london import forms
from london.apps.admin.modules import BaseModuleForm
from london.utils.slugs import slugify
from pages import signals
from pages.models import Page


__author__ = 'jpablo'

class PageForm(BaseModuleForm):

    class Meta:
        model = Page
        exclude = ('text',)
        readonly = ('last_update', 'text')
        
    def get_initial(self, initial=None):
        initial = initial or super(PageForm, self).get_initial(initial)
        
        # Filter author users if user hasn't permissions to view them all
        if not self.request.user.has_perm('auth.edit_user', self.request.site):
            self.fields['author'].queryset = self.fields['author'].queryset(self).filter(pk = self.request.user['pk'])
        
        if not self.instance['pk']:
            # setting initial author for new page
            initial['author'] = str(self.request.user['pk'])

        signals.page_form_initialize.send(sender=self, initial=initial, publish_field_name='is_published')
        return initial

    def initialize(self):
        self.fields['keywords'].widget = forms.ListByCommasTextInput()
        self.fields['slug'].required = False

    def clean(self):
        cleaned_data = super(PageForm, self).clean()
        cleaned_data['slug'] = cleaned_data['slug'] or slugify(cleaned_data['name'])
        
        all_pages = cleaned_data['site']['pages']
        pages = all_pages.filter(slug=cleaned_data['slug'])

        # Validation excludes current page
        if self.instance['pk']:
            pages = pages.exclude(pk=self.instance['pk'])

        # Validating duplicated slug
        if pages.count() > 0:
            raise forms.ValidationError('Another page with slug "%s" already exists for this site.' % cleaned_data['slug'],
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
#        obj['real_slug'] = obj.get_url().strip('/')
        obj.save()
        return obj

    def default_context(self, *args, **kwargs):
        context = super(PageForm, self).default_context(*args, **kwargs)
        
        context['object_verbose_name'] = self._meta.model._meta.verbose_name
        context['object_verbose_name_plural'] = self._meta.model._meta.verbose_name_plural
        return context