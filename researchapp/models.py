from pickle import TRUE
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class PaperType(models.Model):
    name = models.CharField("Type of paper", max_length = 50)
    
    def __str__(self):
        return self.name

class Role(models.Model):
    RoleType = models.CharField(max_length=100)
    def __str__(self):
        return self.RoleType

class University(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images',default=None, blank=True ,null=True)
    created = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE, default=None, null=TRUE)
    created = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class StudentRole(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name

class User(AbstractUser):
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    university = models.ForeignKey(University, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    bio = models.CharField(max_length=100, blank=True , null=TRUE)
    student_role = models.ForeignKey(StudentRole, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    image = models.ImageField(upload_to = 'images/profilePic',blank=True , null=TRUE)
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
        
    def __str__(self):
        return self.username


class Paper(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    
    co_author = models.CharField(max_length=50)
    
    description =  models.TextField()
    category  = models.ForeignKey(PaperType, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    publication = models.FileField(upload_to='pdf/publications')
    peerReview = models.FileField(upload_to='pdf/peerReview', blank=True , null=TRUE)
    created = models.DateField(auto_now_add=True)
    published_by=models.ForeignKey(User, on_delete=models.CASCADE, default=None,blank=True , null=TRUE)
    
    
    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.CharField(max_length=250)
    date_posted = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.message
