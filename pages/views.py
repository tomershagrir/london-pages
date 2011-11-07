# coding: utf-8

from london.shortcuts import get_object_or_404
from london.templates import render_to_response

def view(request, slug, template="page_view"):
    return render_to_response(request, template,
        {'page': get_object_or_404(request.site['pages'], 
        slug=slug)})
