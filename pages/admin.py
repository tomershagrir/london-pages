from london.apps import admin

from models import Page
from forms import PageForm

class ModulePage(admin.CrudModule):
    model = Page
    list_display = ('slug', 'last_update', 'name')
    readonly_fields = ('last_update', 'text')
    exclude = ('text', 'site')
    form = PageForm

class AppBlog(admin.AdminApplication):
    title = 'Page'
    modules = (ModulePage,)

