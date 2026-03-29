from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    """
    This table stores the master list of all doctors in YOUR HOSPITAL.
    You can add 1, 10, or 100 doctors here via the Admin Panel.
    """
    name = models.CharField(max_length=100) # e.g., "Dr. Aswin S."
    specialization = models.CharField(max_length=100) # e.g., "Radiologist"
    bio = models.TextField(blank=True, help_text="Short description of the doctor")
    
    def __str__(self):
        return f"{self.name} ({self.specialization})"

class Appointment(models.Model):
    """
    This table stores the bookings. It 'points' to a Patient and a Doctor.
    """
    # Links to the User who is logged in (Patient)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    
    # Links to the specific Doctor from the Doctor table above
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    
    date = models.DateField()
    time_slot = models.CharField(max_length=50)
    symptoms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    report_image = models.ImageField(upload_to='patient_reports/', blank=True, null=True)
    prescription_notes = models.TextField(blank=True, null=True)
    class Meta:
        unique_together = ('doctor', 'date', 'time_slot')
    # Useful for history tracking: check if appointment is in the past
    def __str__(self):
        return f"{self.patient.username} with {self.doctor.name} on {self.date}"