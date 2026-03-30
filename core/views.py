from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from datetime import date, datetime, timedelta
from .models import Appointment, Doctor, ContactMessage
from ai_services.models import PatientHistory
from django.contrib.admin.views.decorators import staff_member_required

# --- PUBLIC VIEWS ---

def home(request):
    return render(request, 'home.html')

def doctors(request):
    all_doctors = Doctor.objects.all()
    return render(request, 'doctors.html', {'doctors': all_doctors})

def contact(request):
    success = False
    if request.method == "POST" and request.user.is_authenticated:
        message_body = request.POST.get('message')
        
        # Saves the message to the database linked to the logged-in user
        ContactMessage.objects.create(user=request.user, message=message_body)
        success = True
        
    return render(request, 'contact.html', {'success': success})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login') 
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# --- PROTECTED PATIENT VIEWS ---

@login_required
def dashboard(request):
    history = PatientHistory.objects.filter(patient=request.user).order_by('-date_uploaded')
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
    
    # Fetch patient's own messages to show admin replies
    my_messages = ContactMessage.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'history': history,
        'appointments': appointments,
        'my_messages': my_messages,
        'today': date.today()
    }
    return render(request, 'dashboard.html', context)

@login_required
def book_appointment(request):
    all_doctors = Doctor.objects.all()
    
    # Generate 15-minute slots (10:00 AM to 04:00 PM)
    slots = []
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("16:00", "%H:%M")
    
    while start_time < end_time:
        slots.append(start_time.strftime("%I:%M %p"))
        start_time += timedelta(minutes=15)

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        selected_date_str = request.POST.get('date')
        time_slot = request.POST.get('time')
        msg = request.POST.get('symptoms')

        try:
            selected_date = date.fromisoformat(selected_date_str)

            if selected_date <= date.today():
                messages.error(request, "Appointments must be booked at least one day in advance!")
                return render(request, 'book_appointment.html', {'doctors': all_doctors, 'slots': slots})

            if Appointment.objects.filter(doctor_id=doctor_id, date=selected_date, time_slot=time_slot).exists():
                messages.error(request, f"This time slot ({time_slot}) is already booked for this doctor.")
                return render(request, 'book_appointment.html', {'doctors': all_doctors, 'slots': slots})

            doctor_obj = Doctor.objects.get(id=doctor_id)

            Appointment.objects.create(
                patient=request.user,
                doctor=doctor_obj,
                date=selected_date,
                time_slot=time_slot,
                symptoms=msg
            )
            
            messages.success(request, f"Appointment confirmed with {doctor_obj.name} on {selected_date_str} at {time_slot}")
            return redirect('dashboard')

        except (ValueError, Doctor.DoesNotExist):
            messages.error(request, "Invalid selection. Please try again.")

    return render(request, 'book_appointment.html', {'doctors': all_doctors, 'slots': slots})

# --- STAFF VIEWS ---

@staff_member_required
def admin_dashboard(request):
    all_appointments = Appointment.objects.all().order_by('-date')
    total_bookings = all_appointments.count()
    
    # Fetch all patient messages
    patient_messages = ContactMessage.objects.all().order_by('-created_at')
    
    context = {
        'all_appointments': all_appointments,
        'total_bookings': total_bookings,
        'patient_messages': patient_messages,
        'today': date.today()
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def complete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        report = request.FILES.get('report_image')
        notes = request.POST.get('notes')
        
        appointment.report_image = report
        appointment.prescription_notes = notes
        appointment.is_completed = True
        appointment.save()
        
        messages.success(request, f"Consultation for {appointment.patient.username} marked as finished.")
        # FIX: Updated to match name='staff_dashboard' in urls.py
        return redirect('staff_dashboard')

    return render(request, 'complete_appointment.html', {'appt': appointment})

@staff_member_required
def resolve_message(request, pk):
    """
    Handles admin replies to patient inquiries and marks them as resolved.
    """
    if request.method == "POST":
        message_obj = get_object_or_404(ContactMessage, pk=pk)
        reply_text = request.POST.get('admin_reply')
        
        # Update the database record
        message_obj.admin_reply = reply_text
        message_obj.is_resolved = True
        message_obj.save()
        
        messages.success(request, f"Reply sent to {message_obj.user.username} and inquiry resolved.")
    
    # FIX: Updated to match name='staff_dashboard' in urls.py
    return redirect('staff_dashboard')