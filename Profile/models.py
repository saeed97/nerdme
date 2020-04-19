
import random
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import  User


from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
# User = settings.AUTH_USER_MODEL

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_cu1lQmcg1OLffhLvYrSCp5XE")
stripe.api_key = STRIPE_SECRET_KEY

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    # print(instance)
    #print(filename)
    new_filename = random.randint(1,3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "Profiles/{new_filename}/{final_filename}".format(
            new_filename=new_filename, 
            final_filename=final_filename
            )

class ProfileQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) | 
                  Q(description__icontains=query) |
                  Q(price__icontains=query) |
                  Q(tag__title__icontains=query)
                  )
        # tshirt, t-shirt, t shirt, red, green, blue,
        return self.filter(lookups).distinct()



class ProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated():
            'logged in user checkout; remember payment stuff'
            obj, created = self.model.objects.get_or_create(
                            user=user, email=user.email)
        elif guest_email_id is not None:
            'guest user checkout; auto reloads payment stuff'
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                                            email=guest_email_obj.email)
        else:
            pass
        return obj, created
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self): #Profile.objects.featured() 
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # Profile.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Profile(models.Model):
    user        = models.OneToOneField(User, null=True, blank=True ,  on_delete=models.CASCADE,)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)
    STUDENT = 1
    TEACHER = 2
    SUPERVISOR = 3
    ROLE_CHOICES = (
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (SUPERVISOR, 'Supervisor'),
    )
    COMPUTERER = 1
    COMPUTERSC = 2
    SOFTWARER = 3
    ELECTRICALER = 4
    MAJORS = (
        (COMPUTERER, 'Computer Engineering'),
        (COMPUTERSC, 'Computer Science'),
        (SOFTWARER, 'Software Engineering'),
        (ELECTRICALER,'Electrical Engineering')
    )
    location = models.CharField(max_length=50, blank=True)
    GraduationDate = models.DateField(null=True, blank=True)
    aboutme     = models.TextField(max_length=300, blank=True)
    experience     = models.TextField(max_length=300, blank=True)
    preferences     = models.TextField(max_length=300, blank=True) 
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    major = models.PositiveSmallIntegerField(choices=MAJORS, null=True, blank=True)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_digital      = models.BooleanField(default=False) # User Library


    objects = ProfileManager()

    # def get_absolute_url(self):
    #     #return "/Profiles/{slug}/".format(slug=self.slug)
    #     return reverse("Profiles:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.email

    def __unicode__(self):
        return self.email

    @property
    def name(self):
        return self.email

    def get_downloads(self):
        qs = self.Profilefile_set.all()
        return qs

def Profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("ACTUAL API REQUEST Send to stripe/braintree")
        customer = stripe.Customer.create(
                email = instance.email
            )
        print(customer)
        instance.customer_id = customer.id

pre_save.connect(Profile_created_receiver, sender=Profile)

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        Profile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)


# def upload_Profile_file_loc(instance, filename):
#     slug = instance.Profile.slug
#     #id_ = 0
#     id_ = instance.id
#     if id_ is None:
#         Klass = instance.__class__
#         qs = Klass.objects.all().order_by('-pk')
#         if qs.exists():
#             id_ = qs.first().id + 1
#         else:
#             id_ = 0
#     if not slug:
#         slug = unique_slug_generator(instance.Profile)
#     location = "Profile/{slug}/{id}/".format(slug=slug, id=id_)
#     return location + filename #"path/to/filename.mp4"



class ProfileFile(models.Model):
    Profile         = models.ForeignKey(Profile,  on_delete=models.CASCADE,)
    pass
#     Profile         = models.ForeignKey(Profile)
#     name            = models.CharField(max_length=120, null=True, blank=True)
#     file            = models.FileField(
#                         upload_to=upload_Profile_file_loc, 
#                         storage=ProtectedS3Storage(), #FileSystemStorage(location=settings.PROTECTED_ROOT)
#                         ) # path
#     #filepath        = models.TextField() # '/protected/path/to/the/file/myfile.mp3'
#     free            = models.BooleanField(default=False) # purchase required
#     user_required   = models.BooleanField(default=False) # user doesn't matter


#     def __str__(self):
#         return str(self.file.name)

#     @property
#     def display_name(self):
#         og_name = get_filename(self.file.name)
#         if self.name:
#             return self.name
#         return og_name

#     def get_default_url(self):
#         return self.Profile.get_absolute_url()

#     def generate_download_url(self):
#         bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
#         region = getattr(settings, 'S3DIRECT_REGION')
#         access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
#         secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
#         if not secret_key or not access_key or not bucket or not region:
#             return "/Profile-not-found/"
#         PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME', 'protected')
#         path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME, file_path=str(self.file))
#         aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
#         file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
#         return file_url

#     def get_download_url(self): # detail view
#         return reverse("Profiles:download", 
#                     kwargs={"slug": self.Profile.slug, "pk": self.pk}
#                 )






