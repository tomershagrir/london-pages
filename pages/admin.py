from london.apps import admin

from models import Page

class ModulePage(admin.CrudModule):
    model = Page
    list_display = ('slug', 'last_update', 'name', 'text')
    readonly_fields = ('last_update', 'text')

class AppBlog(admin.AdminApplication):
    title = 'Page'
    modules = (ModulePage,)

