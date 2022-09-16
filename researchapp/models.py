from audioop import maxpp
from pickle import TRUE
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your models here.

'''
A model for the research paper categories.
'''
class ResearchCategory(models.Model):
    name = models.CharField("Type of paper", max_length = 50)
    slug = models.SlugField(max_length = 50)

    def __str__(self):
        return self.name


'''
A model for the research papers such as paper title, author etc
'''
class Paper(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    author = models.CharField(max_length=50)
    co_author = models.CharField(max_length=50)
    description =  models.TextField()
    category  = models.ManyToManyField(ResearchCategory, related_name = 'papers')
    pdf = models.FileField(upload_to='pdf')
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

'''
A model for the user login details
'''
class Login(models.Model):
    name = models.CharField("Type usernname", max_length = 50)
    slug = models.SlugField(max_length=100)
    pwd = models.CharField("Type password", max_length = 50)

    def __str__(self):
        return self.name


class Role(models.Model):
    RoleType = models.CharField(max_length=100)
    def __str__(self):
        return self.RoleType

class University(models.Model):
    University = models.CharField(max_length=100)
    def __str__(self):
        return self.University


class Groups(models.Model):
    group_name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE, default=None, null=TRUE)
    def __str__(self):
        return self.Gname

class User(AbstractUser):
    
    is_reseacher = models.BooleanField(default=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=None, null=TRUE)
    uni = models.ForeignKey(University, on_delete=models.CASCADE, default=None, null=TRUE)
    grp = models.ForeignKey(Groups, on_delete=models.CASCADE, default=None, null=TRUE)
    def __str__(self):
        return self.username