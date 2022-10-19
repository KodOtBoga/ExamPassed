from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Writers(models.Model):
    first_name = models.CharField(max_length=80, blank=False)
    last_name = models.CharField(max_length=80, blank=False)
    country = models.CharField(max_length=80, blank=False)

class Book(models.Model):
    title = models.CharField(max_length=77, blank=False, default='')
    description = models.CharField(max_length=300, blank=False, default='')
    author = models.ForeignKey('Writers', on_delete=models.PROTECT)
    rating = models.FloatField(blank=False)
    published_year = models.IntegerField(default=False)

    @property
    def book_coms(self):
        return self.comments_set.all()

class Page(models.Model):
    pageNumber = models.IntegerField()
    bookId = models.ForeignKey('Book', on_delete=models.PROTECT)
    image = models.CharField(null=True, max_length=255)

class Comments(models.Model):
    bookId = models.ForeignKey('Book', on_delete=models.PROTECT)
    userId = models.ForeignKey('User', on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=255)

    @property
    def comments_set(self):
        return self.comments_set.all()

class User(AbstractUser):
    first_name = models.CharField(max_length=80, blank=False)
    last_name = models.CharField(max_length=80, blank=False)
    email = models.CharField(max_length=90, blank=False, unique=True)
    username = models.CharField(max_length=90, blank=True, null=True, unique=True)
    password = models.CharField(max_length=90, blank=False)
    # username = None

    # USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
