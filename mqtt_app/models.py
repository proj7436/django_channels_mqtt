from django.db import models

# Create your models here.


class DataModels(models.Model):
    device_name = models.CharField(max_length=220)
    data_response = models.CharField(max_length=500)
    time_response = models.CharField(max_length=40)

    def  __str__(self) -> str:
        return self.device_name