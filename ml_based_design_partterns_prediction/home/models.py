from django.db import models

# Create your models here.
class Register(models.Model):
    username =models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=50)
    email =models.EmailField(max_length=50)

    def __str__(self):
        return self.username