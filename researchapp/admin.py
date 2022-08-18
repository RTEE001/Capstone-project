from django.contrib import admin
from .models import ResearchCategory, Paper
# Register your models here.


class ResearchCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class PaperAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(ResearchCategory, ResearchCategoryAdmin)
admin.site.register(Paper,PaperAdmin)

