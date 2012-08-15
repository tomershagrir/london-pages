from london.dispatch import Signal
from images import add_image_field_to_sender_form
from london.apps.seo import add_meta_info_fields_to_sender_form, save_meta_info_from_sender_form
from london.apps.collections import add_collections_to_sender_form, save_collections_from_sender_form
try:
    from londonforms import add_forms_to_page_form
except:
    add_forms_to_page_form = None


page_form_initialize = Signal()
page_form_initialize.connect(add_meta_info_fields_to_sender_form)
page_form_initialize.connect(add_image_field_to_sender_form)
page_form_initialize.connect(add_collections_to_sender_form)
page_form_pre_save = Signal()
page_form_post_save = Signal()
page_form_post_save.connect(save_meta_info_from_sender_form)
page_form_post_save.connect(save_collections_from_sender_form)
page_form_clean = Signal()

if add_forms_to_page_form:
    page_form_initialize.connect(add_forms_to_page_form)