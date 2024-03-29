# coding: utf-8
from london.shortcuts import get_object_or_404
from london.templates import render_to_response, get_context
from london.apps.ajax.tags import redirect_to
from london.apps.collections.models import Collection
from london.http import Http404
try:
    from images.render import ImagesRender
    image_compiler = ImagesRender()
except ImportError:
    image_compiler = None
try:
    from london.apps.collections.render import CollectionsRender
    collection_compiler = CollectionsRender()
except ImportError:
    collection_compiler = None
try:
    from londonforms.render import FormsRender
    form_compiler = FormsRender()
except ImportError:
    form_compiler = None
    
try:
    from routes import register_for_routes
except ImportError:
    def register_for_routes(path):
        def _inner(view):
            return view
        return _inner

from pages.models import Page


def _render_page(request, page, template):
    
    template = page['template_name'] or template
    
    if image_compiler:
        page['text'] = image_compiler.render(page['text'])
    
    if collection_compiler:
        try:
            page['text'] = collection_compiler.render(request.site, getattr(request, 'theme', None), get_context(request), page['text'])
        except TypeError:
            page['text'] = collection_compiler.render(site=request.site, theme=getattr(request, 'theme', None), source=page['text'])
        
    if form_compiler:
        redirect_url, page['text'] = form_compiler.render(request, page['text'])
    else:
        redirect_url = None
        
    parent_page = page['parent_page']
    breadcrumbs = []
    while parent_page:
        breadcrumbs.append((parent_page.get_title(), parent_page.get_url()))
        parent_page = parent_page['parent_page']
    breadcrumbs.reverse()
    breadcrumbs.append((page.get_title(), page.get_url()))
    request.breadcrumbs(breadcrumbs)
    
    if redirect_url:
        return redirect_to(request, redirect_url)
    else:
        return render_to_response(request, template, {'page': page})
    
def _get_page_by_slug(request, slug):
    page = get_object_or_404(request.site['pages'], slug=slug, is_published=True)
    return page

@register_for_routes('pages.views.list')
def list(request, template='page_list', **kwargs):
    site = getattr(request, 'site', None)
    
    pages = Page.query()
    if site:
        pages = site['pages']
    
    collections = Collection.query()
    if 'slug2' in kwargs:
        items = []
        for item in Collection.query().filter(site=site, slug=kwargs['slug2']):
            items.extend(item['items'])
        collections = collections.filter(pk__in=items)
    if 'slug1' in kwargs:
        collection = get_object_or_404(collections, slug=kwargs['slug1'])
        pages = pages.filter(pk__in=collection['items'])
        
    return render_to_response(request, template, {'pages':pages})

@register_for_routes('pages.views.view')
def view(request, slug, template="page_view", **kwargs):
    try:
        if slug == Page.query().published().filter(is_home=True).get().get_url():
            return redirect_to(request, '/')
    except:
        pass
    
    if not getattr(request, 'site', None):
        raise Http404
    
    page = _get_page_by_slug(request, slug)
    
#    don't show page if it belongs to collection with a slug
    collections = Collection.query().filter(site=request.site, slug__notequal='', items__contains=page['pk'])
    if collections.count():
        raise Http404
    return _render_page(request, page, template)

@register_for_routes('pages.views.category_view')
def category_view(request, slug, template="page_view", **kwargs):
    collections = Collection.query().filter(site=request.site)
    pages = Page.query().published()
    breadcrumbs = []
    if 'slug1' in kwargs:
        items = []
        category = None
        for item in collections.filter(slug=kwargs['slug1']):
            category = item
            items.extend(item['items'])
        if category:
            breadcrumbs.append((category['title'] or category['name'], category.get_url()))
        pages = pages.filter(site=request.site, pk__in=items)
    page = get_object_or_404(pages, slug=slug)
    request.breadcrumbs(breadcrumbs)
    return _render_page(request, page, template)

@register_for_routes('pages.views.view_404')
def view_404(request, **kwargs):
    raise Http404

def view_home(request, template="page_view"):
    page = Page.query().published().filter(is_home=True).get()
    return _render_page(request, page, page['template_name'] or template)
