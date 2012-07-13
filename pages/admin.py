from london.apps import admin

from models import Page
from forms import PageForm

class ModulePage(admin.CrudModule):
    model = Page
    list_display = ('slug', 'last_update', 'name', 'is_home')
    readonly_fields = ('last_update', 'text')
    exclude = ('text',)
    form = PageForm
    search_fields = ("name",)

class AppBlog(admin.AdminApplication):
    title = 'Page'
    modules = (ModulePage,)

