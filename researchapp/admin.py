from django.contrib import admin
from .models import ResearchCategory, Paper, Login, User, Role, University, Groups
# Register your models here.


class ResearchCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class PaperAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class LoginAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class Login1Admin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


    
admin.site.register(ResearchCategory, ResearchCategoryAdmin)
admin.site.register(Paper,PaperAdmin)
admin.site.register(Login,LoginAdmin)
admin.site.register(User)
admin.site.register(Groups)
admin.site.register(University)
admin.site.register(Role)