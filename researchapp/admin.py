from django.contrib import admin
from .models import ResearchCategory, Paper, User, Role, University, Groups
# Register your models here.
  
admin.site.register(ResearchCategory)
admin.site.register(Paper)
admin.site.register(User)
admin.site.register(Groups)
admin.site.register(University)
admin.site.register(Role)