import re
from datetime import datetime
try:
    import markdown2
except ImportError:
    markdown2 = None

from london.db import models
from london.apps.sites.models import Site
from london.apps.collections.models import Collection
from london.utils.safestring import mark_safe
from london.urls import reverse

from signals import page_model_save, page_get_name, page_get_title, page_get_content


class PageQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True).order_by('name')

    def home(self, field='slug'):
        try:
            return self.filter(is_home=True).get()[field]
        except:
            return None


class Page(models.Model):

    class Meta:
        query = 'pages.models.PageQuerySet'
        ordering = ('-last_update', )

    RENDER_TYPE_RAW = 'raw'
    RENDER_TYPE_MARKDOWN = 'markdown'
    RENDER_TYPE_CHOICES = (
            (RENDER_TYPE_RAW, 'Raw HTML'),
            (RENDER_TYPE_MARKDOWN, 'Markdown'),
            )

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', blank=False, null=False, related_name='pages')
    slug = models.SlugField(max_length=255, blank=True, null=False, allow_slashes=True)
#    real_slug = models.SlugField(max_length=255, blank=True, null=False, allow_slashes=True)
    title = models.CharField(max_length=255)
#    position = models.SmallIntegerField(blank=True, null=False,
#            help_text='Menu position (for ranking of menu items)')
    text = models.TextField()
    source = models.TextField()
    last_update = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='pages')
    template_name = models.CharField(max_length=100, blank=True)
    markup = models.CharField(max_length=20, blank=True, choices=RENDER_TYPE_CHOICES, default=RENDER_TYPE_RAW)
    keywords = models.ListField(null=True, blank=True)
    is_published = models.BooleanField(default=True, db_index=True, blank=True)
    is_home = models.BooleanField(default=False, blank=True)
#    parent_page = models.ForeignKey("self", blank=True, related_name='other_pages')
#    use_parent_page_in_url = models.BooleanField(default=False, blank=True, verbose_name="Show middle pages in url")
    
    def __unicode__(self):
        return self['name']
    
    def _save_text_from_source(self, source_field_name, text_field_name):
        source = self.get(source_field_name,  None)
        if self['markup'] == self.RENDER_TYPE_MARKDOWN:
            self[text_field_name] = markdown2.markdown(source or '')
        else:
            self[text_field_name] = source or ''

    def save(self, **kwargs):
        self['last_update'] = datetime.now()
        self._save_text_from_source('source', 'text')
        page_model_save.send(instance=self)
        
        return super(Page, self).save(**kwargs)
    
    def publish(self):
        self['is_published'] = True
        self.save()

    def get_name(self, lang='default'):
        name = page_get_name.send(instance=self, lang=lang)
        if not len(name) or not name[0]:
            name = self['name'] 
        else:
            name = name[0] 
        return name

    def get_title(self, lang='default'):
        title = page_get_title.send(instance=self, lang=lang)
        if not len(title) or not title[0]:
            title = self['title'] 
        else:
            title = title[0] 
        return title 
    
    def get_url(self):
        kwargs = {}
        collections = Collection.query().filter(site=self['site'], items__contains=str(self['pk']))
        if collections.count():
            kwargs = collections[0].get_slugs() # TODO: what to do if page belongs to more than 1 collection?
        kwargs['slug'] = self['slug']
        
        try:
            from routes import dynamic_url_patterns
            url_patterns = dynamic_url_patterns[self['site']['name']] if self['site']['name'] in dynamic_url_patterns else []
        except ImportError:
            url_patterns = []
        
        try:
            return reverse('pages_views_category_view', kwargs=kwargs, dynamic_url_patterns=url_patterns)
        except:
            return '/%s/' % self['slug']

#    def get_url(self):
#        if self['is_home']:
#            return reverse("page_view_home")
#        
#        parent = self['parent_page']
#        slug = self['slug']
#        while parent and self['use_parent_page_in_url']:
#            slug = "%s/%s" % (parent['slug'], slug)
#            parent = parent['parent_page']
#        return reverse("page_view", kwargs={'slug': slug})
    
    def get_content(self, lang='default'):
        regex = re.compile("\{(IMAGE|COLLECTION|ALL|FORM):(.*?)\}")
        content = page_get_content.send(instance=self, lang=lang, regex=regex)
        if not len(content) or not content[0]:
            content = mark_safe(regex.sub('', self['text']))
        else:
            content = content[0] 
        return content