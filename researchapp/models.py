from audioop import maxpp
from django.db import models
from django.contrib.auth.models import AbstractUser, User
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

    def __str__(self):
        return self.title

