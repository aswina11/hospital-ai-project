import markdown
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PatientHistory

# 1. Setup the AI with your secret key
genai.configure(api_key="AIzaSyCy3XQFU5VEnXhRz82Ci2o7SCotldeGHO4")

@login_required
def upload_scan(request):
    if request.method == 'POST' and request.FILES.get('scan_image'):
        scan_file = request.FILES['scan_image']
        scan_type = request.POST.get('scan_type')
        
        # 2. Initialize Gemini 1.5 Flash (Fast and good for images)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. Process the image for the AI
        image_data = scan_file.read()
        
        # 4. Create the prompt for the medical analysis
        prompt = (
            f"You are a professional Radiologist AI. Analyze this {scan_type} image. "
            "Identify key findings and provide a brief preliminary observation. "
            "End with: 'Disclaimer: This is an AI-generated demo!. A Doctor consultation is highly recomended ASAP'"
        )
        
        try:
            # Send to Google's Servers
            response = model.generate_content([
                prompt, 
                {'mime_type': 'image/jpeg', 'data': image_data}
            ])
            analysis_text = response.text
        except Exception as e:
            analysis_text = f"AI Error: {str(e)}"
        
        # 5. Reset the file pointer and save to RDBMS
        # This is critical so Django can save the file after the AI read it
        scan_file.seek(0) 
        
        PatientHistory.objects.create(
            patient=request.user,
            scan_type=scan_type,
            image=scan_file,
            ai_analysis=analysis_text
        )
        return redirect('dashboard')
        
    return render(request, 'upload_scan.html')

from django.shortcuts import get_object_or_404

@login_required
def report_detail(request, pk):
    report = get_object_or_404(PatientHistory, pk=pk, patient=request.user)
    report_html = markdown.markdown(report.ai_analysis)
    
    return render(request, 'report_detail.html', {
        'report': report,
        'report_html': report_html
    })
from django.http import JsonResponse
import json
import google.generativeai as genai

def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            # Get history from frontend
            history = data.get('history', [])

            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Start a chat session with the actual history provided
            # We filter history to ensure it's in the format Gemini expects
            chat = model.start_chat(history=history[:-1]) # send everything except the last msg
            
            response = chat.send_message(user_message)
            
            return JsonResponse({'reply': response.text})
        except Exception as e:
            print(f"Chat Error: {e}")
            return JsonResponse({'reply': "I'm having trouble connecting to my brain. Try again!"}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)