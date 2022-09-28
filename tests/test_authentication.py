from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth import get_user_model
from researchapp.models import Role, Group, University,StudentRole, Paper, PaperType
from django.core.files.uploadedfile import SimpleUploadedFile
User = get_user_model()


class BaseTest(TestCase):
    def setUp(self):
        
        self.login_url=reverse('loggedin')
        self.createStu_url=reverse('createStuUser')
        self.logout_url=reverse('loggedout')
        self.upload_url= reverse('upload')
        self.user={
            'email':'testemail@gmail.com',
            'username':'username',
            'password':'password',
            'psw':'password',
            'studentRole':'phd',
            'GroupCat': 'AR',
            'First':'fullname',
            'Last': 'fullname',

        }
     
        self.user_unmatching_password={

            'email':'testemail@gmail.com',
            'username':'username',
            'password':'teslatt',
            'password2':'teslatto',
            'name':'fullname'
        }

       
        return super().setUp()

class LoginTest(BaseTest):

    def test_login_success(self):
       
        user=User(username="username", password=make_password("password"))
        user.is_active=True
        user.save()

        response= self.client.post(self.login_url,self.user)
        
        self.assertRedirects(response, '/dashboard/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)
    
    def test_login_fail(self):
        user=User(username="username", password=make_password("password"))
        user.is_active=True
        user.save()

        response= self.client.post(self.login_url,self.user_unmatching_password)
        
        self.assertRedirects(response, '/signin/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)

class createStudentTest(BaseTest):

    def test_createStudent(self):
        role = Role(RoleType="student")
        role.save()
        university=University(name='uct')
        university.save()
        studentRole = StudentRole(name="phd")
        studentRole.save()
        group =Group(name="AR",university=university)
        group.save()
        self.client.post(self.createStu_url,self.user)

        self.assertAlmostEquals(User.objects.get(id=1).role.RoleType,'student')
        

class LogoutTest(BaseTest):

    def test_logout(self):
        user=User(username="username", password=make_password("password"))
        user.is_active=True
        user.save()

        self.client.post(self.login_url,self.user)
        response= self.client.post(self.logout_url,self.user)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)


class UplpoadTest(BaseTest):
    
    def test_uploadPaper(self):
        role = Role(RoleType="student")
        role.save()
        university=University(name='uct')
        university.save()
        studentRole = StudentRole(name="phd")
        studentRole.save()
        papertype=PaperType(name="generalPaper")
        papertype.save()
        group =Group(name="AR",university=university)
        group.save()
        self.client.post(self.createStu_url,self.user)
        self.client.post(self.login_url,self.user)
        with open('/home/mo/Documents/cbib_capstone_projectbackend/researchapp/tests/Rammbuda_Thifhidzi_Resume.pdf', 'rb') as pdf:

            response = self.client.post(self.upload_url, {'author':"manualvarado22", 'co_author': 'lucifer', 'title': "Super Important Test", 'description':"This is really important.",'category':PaperType.objects.get(id=1) ,'group':Group.objects.get(id=1),'publication':pdf, 'peerReview':pdf, 'published_by': User.objects.get(id=1)})
            
            
             
        self.assertEquals(response.status_code,200 )
