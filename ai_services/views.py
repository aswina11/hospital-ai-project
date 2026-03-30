import markdown
import google.generativeai as genai
import os  # <--- ADD THIS
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # <--- ADD THIS
from .models import PatientHistory

# 1. Setup the AI - Pulling from Environment for Render
# If on Render, it uses the Environment Variable. If local, it uses the string.
api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDzVFOIyuIxOGzLbjr5ZL5gaq46i0BMrVg")
genai.configure(api_key=api_key)

@login_required
def upload_scan(request):
    if request.method == 'POST' and request.FILES.get('scan_image'):
        scan_file = request.FILES['scan_image']
        scan_type = request.POST.get('scan_type')
        
        # Using 1.5-flash as it's the stable free tier model
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        image_data = scan_file.read()
        
        prompt = (
            f"You are a professional Radiologist AI. Analyze this {scan_type} image. "
            "Identify key findings and provide a brief preliminary observation. "
            "End with: 'Disclaimer: This is an AI-generated demo!. A Doctor consultation is highly recomended ASAP'"
        )
        
        try:
            response = model.generate_content([
                prompt, 
                {'mime_type': 'image/jpeg', 'data': image_data}
            ])
            analysis_text = response.text
        except Exception as e:
            analysis_text = f"AI Error: {str(e)}"
        
        scan_file.seek(0) 
        
        PatientHistory.objects.create(
            patient=request.user,
            scan_type=scan_type,
            image=scan_file,
            ai_analysis=analysis_text
        )
        return redirect('dashboard')
        
    return render(request, 'upload_scan.html')

@login_required
def report_detail(request, pk):
    report = get_object_or_404(PatientHistory, pk=pk, patient=request.user)
    report_html = markdown.markdown(report.ai_analysis)
    
    return render(request, 'report_detail.html', {
        'report': report,
        'report_html': report_html
    })

# --- CHATBOT FIX BELOW ---

@csrf_exempt  # <--- THIS IS THE FIX FOR THE LIVE LINK
def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            history = data.get('history', [])

            # Use 1.5-flash (2.5-flash doesn't exist yet, 1.5 is the fast one!)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Filtering history to keep Gemini happy
            chat = model.start_chat(history=history[:-1] if len(history) > 0 else [])
            
            response = chat.send_message(user_message)
            
            return JsonResponse({'reply': response.text})
        except Exception as e:
            print(f"Chat Error: {e}")
            return JsonResponse({'reply': "I'm having trouble connecting to my brain. Try again!"}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)