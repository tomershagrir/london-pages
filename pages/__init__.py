import os 

from london.apps.themes.registration import register_template
register_template("page_view", mirroring="pages/page_view.html")
register_template("page_list", mirroring="pages/page_list.html")

REQUIRED_PACKAGES = ['markdown2']

