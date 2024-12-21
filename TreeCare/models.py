from django.db import models

# Create your models here.


class Tree(models.Model):
    SoilMoisture = models.FloatField(null=True, blank=True)
    Temperature = models.FloatField(null=True, blank=True)
    SoilHumidity = models.FloatField(null=True, blank=True)
    Time = models.IntegerField(null=True, blank=True)
    AirTemperature = models.FloatField(null=True, blank=True)
    WindSpeed = models.FloatField(null=True, blank=True)
    Airhumidity = models.FloatField(null=True, blank=True)
    Windgust = models.FloatField(null=True, blank=True)
    Pressure = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    rainfall = models.FloatField(null=True, blank=True)
    N = models.IntegerField(null=True, blank=True)
    P = models.IntegerField(null=True, blank=True)
    K = models.IntegerField(null=True, blank=True)
    Status = models.CharField(max_length=255, null=True, blank=True)
    Cluster = models.CharField(max_length=255, null=True, blank=True)

class File(models.Model):
    file = models.FileField(upload_to='files')