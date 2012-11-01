# coding: utf-8
from london.shortcuts import get_object_or_404
from london.templates import render_to_response, get_context
from london.apps.ajax.tags import redirect_to
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

from pages.models import Page


def _return_view(request, slug, template):
    if not getattr(request, 'site', None):
        raise Http404

    try:
        page = get_object_or_404(request.site['pages'], real_slug=slug, is_published=True)
    except Http404:
        page = get_object_or_404(request.site['pages'], slug=slug, real_slug=None, is_published=True)
    
    template = page['template_name'] or template
    
    if image_compiler:
        page['text'] = image_compiler.render(page['text'])
    
    if collection_compiler:
        page['text'] = collection_compiler.render(request.site, getattr(request, 'theme', None), get_context(request), page['text'])
        
    if form_compiler:
        redirect_url, page['text'] = form_compiler.render(request, page['text'])
    else:
        redirect_url = None
    
    if request.breadcrumbs:
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

def view(request, slug, template="page_view"):
    try:
#        if slug == Page.query().published().filter(is_home=True).get()['slug']:
        if slug == Page.query().published().filter(is_home=True).get().get_url():
            return redirect_to(request, '/')
    except:
        pass

    return _return_view(request, slug, template)

def view_home(request, template="page_view"):
#    slug = Page.query().published().filter(is_home=True).get()['slug']
    slug = Page.query().published().filter(is_home=True).get().get_url()
    return _return_view(request, slug, template)
