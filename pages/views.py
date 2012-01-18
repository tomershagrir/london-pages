# coding: utf-8

from london.shortcuts import get_object_or_404
from london.templates import render_to_response

def view(request, slug, template="page_view"):
    page = get_object_or_404(request.site['pages'], slug=slug)
    template = page['template_name'] or template
    return render_to_response(request, template,
        {'page': page})
