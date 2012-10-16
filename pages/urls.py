# coding: utf-8

from london.urls.defining import patterns
from pages.models import Page

url_patterns = patterns('pages.views',
        (r'^(?P<slug>[\w/-]+)/$', 'view', {}, "page_view"), # added slash as a permitted symbol of a slug
)

if Page.query().published().filter(is_home=True):
    url_patterns += patterns('pages.views',
        (r'^$', 'view_home', {}, "page_view_home"),
    )
