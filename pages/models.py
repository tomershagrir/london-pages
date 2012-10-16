import re

from london.db import models
from london.apps.sites.models import Site
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime

try:
    import markdown2
except ImportError:
    markdown2 = None


class PageQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def home(self, field='slug'):
        try:
            return self.filter(is_home=True).get()[field]
        except:
            return None


class Page(models.Model):

    class Meta:
        query = 'pages.models.PageQuerySet'
#        ordering = ('position', )

    RENDER_TYPE_RAW = 'raw'
    RENDER_TYPE_MARKDOWN = 'markdown'
    RENDER_TYPE_CHOICES = (
            (RENDER_TYPE_RAW, 'Raw HTML'),
            (RENDER_TYPE_MARKDOWN, 'Markdown'),
            )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=False, allow_slashes=True)
    real_slug = models.SlugField(max_length=255, blank=True, null=False, allow_slashes=True)
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
    parent_page = models.ForeignKey("self", blank=True, related_name='other_pages')
    use_parent_page_in_url = models.BooleanField(default=False, blank=True, verbose_name="Show middle pages in url")
    
    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        self['last_update'] = datetime.now()
        
        source = self.get('source',  None)
        if self['markup'] == self.RENDER_TYPE_MARKDOWN:
            self['text'] = markdown2.markdown(source or '')
        else:
            self['text'] = source or ''
        
        self['real_slug'] = self.get_url().strip('/')
        
        return super(Page, self).save(**kwargs)

    def get_name(self):
        return self['name']

    def get_title(self):
        return self['title']

    def get_url(self):
        if self['is_home']:
            return reverse("page_view_home")
        
        parent = self['parent_page']
        slug = self['slug']
        while parent and self['use_parent_page_in_url']:
            slug = "%s/%s" % (parent['slug'], slug)
            parent = parent['parent_page']
        return reverse("page_view", kwargs={'slug': slug})
    
    def get_content(self):
        regex = re.compile("\{(IMAGE|COLLECTION|ALL|FORM):(.*?)\}")
        return mark_safe(regex.sub('', self['text']))
