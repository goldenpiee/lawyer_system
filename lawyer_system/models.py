from django.db import models

class Appointment(models.Model):
    # Existing fields
    confirmed = models.BooleanField(default=False)