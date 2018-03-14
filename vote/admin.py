from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import Competition, Participate


admin.site.register(Competition, PageAdmin)
admin.site.register(Participate, PageAdmin)
