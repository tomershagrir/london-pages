# coding: utf-8

from london.shortcuts import get_object_or_404
from london.templates import render_to_response
from london.apps.ajax.tags import redirect_to
from london.http import Http404

from pages.models import Page

def _return_view(request, slug, template):
    if not getattr(request, 'site', None):
        raise Http404

    page = get_object_or_404(request.site['pages'], slug=slug)
    template = page['template_name'] or template
    return render_to_response(request, template,
        {'page': page})

def view(request, slug, template="page_view"):
    try:
        if slug == Page.query().filter(is_home=True).get()['slug']:
            return redirect_to(request, '/')
    except:
        pass

    return _return_view(request, slug, template)

def view_home(request, template="page_view"):
    slug = Page.query().filter(is_home=True).get()['slug']
    return _return_view(request, slug, template)
