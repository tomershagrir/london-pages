from london.db import models
from london.utils.slugs import slugify
from london.apps.sites.models import Site
from london.utils.safestring import mark_safe
from london.urls import reverse

from datetime import datetime

try:
    from images.render import ImagesRender
    image_compiler = ImagesRender()
except ImportError:
    image_compiler = None
    
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
        ordering = ('position', )

    RENDER_TYPE_RAW = 'raw'
    RENDER_TYPE_MARKDOWN = 'markdown'
    RENDER_TYPE_CHOICES = (
            (RENDER_TYPE_RAW, 'Raw HTML'),
            (RENDER_TYPE_MARKDOWN, 'Markdown'),
            )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=False)
    title = models.CharField(max_length=255)
    position = models.SmallIntegerField(blank=True, null=False,
            help_text='Menu position (for ranking of menu items)')
    text = models.TextField()
    source = models.TextField()
    last_update = models.DateTimeField(blank=False, null=False)
    site = models.ForeignKey(Site, related_name='pages')
    template_name = models.CharField(max_length=100, blank=True)
    markup = models.CharField(max_length=20, blank=True, choices=RENDER_TYPE_CHOICES, default=RENDER_TYPE_RAW)
    keywords = models.ListField(null=True, blank=True)
    is_published = models.BooleanField(default=True, db_index=True, blank=True)
    is_home = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        return self['name']

    def save(self, **kwargs):
        # TODO: slug field should be unique with site/blog
        # default values for slug and date
        if not self.get('slug', False):
            self['slug'] = slugify(self['name'])

        self['last_update'] = datetime.now()

        source = self.get('source',  None)
        source = image_compiler.render(source) or source
#        source = collection_compiler.render(source) or source
        if self['markup'] == self.RENDER_TYPE_MARKDOWN:
            self['text'] = markdown2.markdown(source or '')
        else:
            self['text'] = source or ''
        return super(Page, self).save(**kwargs)

    def get_name(self):
        return self['name']

    def get_title(self):
        return self['title']

    def get_url(self):
        if self['is_home']:
            return reverse("page_view_home")
        return reverse("page_view", kwargs={'slug': self['slug']})

    def get_content(self):
        regex = re.compile("\{(COLLECTION|ALL|FORM):(.*?)\}")
        return mark_safe(regex.sub('', self['text']))
