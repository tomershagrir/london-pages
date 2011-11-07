
from london.urls.defining import patterns

url_patterns = patterns('pages.views',
        (r'^(?P<slug>[\w-]+)/$', 'view', {}, "page_view"),
)
