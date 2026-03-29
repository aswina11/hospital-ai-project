from django.db import models
from django.contrib.auth.models import User

class PatientHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_type = models.CharField(max_length=50) # e.g., X-ray, CT Scan
    image = models.ImageField(upload_to='scans/')
    ai_analysis = models.TextField()
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scan_type} - {self.patient.username}"