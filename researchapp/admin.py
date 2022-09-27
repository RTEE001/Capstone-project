from django.contrib import admin
from .models import PaperType, Paper, User, Role, University, Group, StudentRole, Contact
# Register your models here.
  
admin.site.register(PaperType)
admin.site.register(Paper)
admin.site.register(StudentRole)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(University)
admin.site.register(Role)
admin.site.register(Contact)
