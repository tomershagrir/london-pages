from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime

try:
    import markdown2
except ImportError:
    markdown2 = None

class Page(models.Model):
    RENDER_TYPE_RAW = 'raw'
    RENDER_TYPE_MARKDOWN = 'markdown'
    RENDER_TYPE_CHOICES = (
            (RENDER_TYPE_RAW, 'Raw HTML'),
            (RENDER_TYPE_MARKDOWN, 'Markdown'),
            )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=False, null=False)
    text = models.TextField()
    source = models.TextField()
    last_update = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='pages')
    template_name = models.CharField(max_length=100, blank=True)
    markup = models.CharField(max_length=20, blank=True, choices=RENDER_TYPE_CHOICES, default=RENDER_TYPE_RAW)
 
    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        # TODO: slug field should be unique with site/blog
        # default values for slug and date
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        self['last_update'] = datetime.now()

        source = self.get('source',  None)
        if self['markup'] == self.RENDER_TYPE_MARKDOWN:
            self['text'] = markdown2.markdown(source or '')
        else:
            self['text'] = source or ''
        return super(Page, self).save(**kwargs)

    def get_url(self):
        return reverse("page_view", kwargs={'slug': self['slug']})

    def get_content(self):
        return mark_safe(self['text'])
