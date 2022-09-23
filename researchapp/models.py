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
    
    def __str__(self):
        return self.name


'''
A model for the research papers such as paper title, author etc
'''



class Role(models.Model):
    RoleType = models.CharField(max_length=100)
    def __str__(self):
        return self.RoleType

class University(models.Model):
    Uniname = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images',default=None, blank=True ,null=True)
    def __str__(self):
        return self.Uniname


class Groups(models.Model):
    Gname = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    uni = models.ForeignKey(University, on_delete=models.CASCADE, default=None, null=TRUE)
    def __str__(self):
        return self.Gname

class User(AbstractUser):
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    uni = models.ForeignKey(University, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    grp = models.ForeignKey(Groups, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    bio = models.CharField(max_length=100, blank=True , null=TRUE)
    def __str__(self):
        return self.username

class Paper(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    co_author = models.CharField(max_length=50)
    description =  models.TextField()
    category  = models.ForeignKey(ResearchCategory, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    pdf = models.FileField(upload_to='pdf/publications')
    peerReview = models.FileField(upload_to='pdf/peerReview', blank=True , null=TRUE)
    created = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.title
