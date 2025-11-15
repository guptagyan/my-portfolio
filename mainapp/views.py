import base64
import io
import json
import os
import random

from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
import numpy as np
from mainapp import anpr_core
from portfolio import settings
from PIL import Image
from .forms import ProfileForm, ProjectForm
from .models import Project, Resume
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import base64

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Get 3 related projects (excluding current one)
    related_projects = Project.objects.exclude(id=project.id).order_by('-created_at')[:3]
    
    # Split technologies and features for template rendering
    technologies = project.technologies.split(',') if project.technologies else []
    features = project.features.split('\n') if project.features else []
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'technologies': [tech.strip() for tech in technologies if tech.strip()],
        'features': [feature.strip() for feature in features if feature.strip()],
        'page_title': f"{project.title} | Project Details",
        'meta_description': project.description[:160],
    }
    
    return render(request, 'project_detail.html', context)

def projects_view(request):
    try:
        projects_list = Project.objects.all().order_by('-created_at')
        paginator = Paginator(projects_list, 6)
        page_number = request.GET.get('page', 1)
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            
        context = {
            'page_obj': page_obj,
            'projects': page_obj.object_list,  # Both variables for flexibility
            'page_title': 'My Projects',
        }
        return render(request, 'projects.html', context)
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Check console for errors
        return render(request, 'projects.html', {'error': str(e)})

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        
        try:
            send_mail(
                subject=f"New Contact Query from {name}",
                message=full_message,
                from_email=email,  # The sender's email
                recipient_list=["gyanbabu193@gmail.com"],  # Replace with your email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, "Failed to send your message. Please try again later.")

        return redirect("contact")  # Redirect to the contact page after submission

    return render(request, "contact.html")

def resume(request):
    try:
        # Get the latest resume or return 404 if none exists
        resume_entry = get_object_or_404(Resume.objects.order_by('-uploaded_at'))
        
        # Check if file exists in storage
        if not os.path.exists(resume_entry.resume_file.path):
            raise Http404("Resume file not found")
        
        # For direct download link in template
        context = {
            'resume_entry': resume_entry,
            'file_url': resume_entry.resume_file.url,
            'file_name': os.path.basename(resume_entry.resume_file.name)
        }
        return render(request, 'resume.html', context)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error accessing resume: {str(e)}")
        raise Http404("Resume could not be loaded")
    

def download_resume(request, id):
    resume = get_object_or_404(Resume, pk=id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(resume.resume_file))
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{resume.name or "resume"}_{resume.uploaded_at.date()}.pdf"'
        return response
    raise Http404("File not found")

def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your resume has been uploaded successfully!')
            return redirect('resume')
        else:
            messages.error(request, 'Error uploading resume. Please check the details.')
    else:
        form = ProfileForm()

    return render(request, 'profile.html', {'form': form})

@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects')  # Redirect to project list
    else:
        form = ProjectForm()

    return render(request, 'create_project.html', {'form': form})


@login_required(login_url='/login/')  # Force login before accessing edit page
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if the user is the owner of the project
    if request.user != project.owner:
        messages.warning(request, "🚫 You are not authorized to edit this project!")
        return redirect('/admin/')  # Redirect unauthorized users to admin

    if request.method == "POST":
        project.title = request.POST.get("title")
        project.description = request.POST.get("description")
        project.github_link = request.POST.get("github_link")
        project.save()
        messages.success(request, "✅ Project updated successfully!")
        return redirect("projects")  # ✅ Corrected redirection


    return render(request, "edit_project.html", {"project": project})


@csrf_exempt
@require_POST
def chatbot(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        
        # Enhanced response logic for portfolio website
        greetings = ['hi', 'hello', 'hey', 'greetings', 'namaste', 'hola']
        farewells = ['bye', 'goodbye', 'see you', 'later', 'tata', 'exit']
        thanks = ['thanks', 'thank you', 'appreciate it', 'धन्यवाद', 'शुक्रिया']
        skills = ['skill', 'technology', 'tech stack', 'expertise', 'knowledge']
        experience = ['experience', 'background', 'work history', 'career']
        education = ['education', 'degree', 'qualification', 'college', 'university']
        hire = ['hire', 'recruit', 'job', 'opportunity', 'position', 'vacancy']
        services = ['service', 'offer', 'provide', 'what do you do']
        resume = ['resume', 'cv', 'download']
        social = ['social', 'linkedin', 'github', 'twitter', 'instagram', 'contact']
        
        if any(word in user_message for word in greetings):
            responses = [
                "Hello! I'm Gyan's AI assistant. How can I help you today?",
                "Namaste! Welcome to Gyan's portfolio. What would you like to know?",
                "Hi there! I can tell you about Gyan's skills, projects, and experience. What interests you?",
                "Greetings! I'm here to provide information about Gyan's professional portfolio."
            ]
        elif any(word in user_message for word in farewells):
            responses = [
                "Goodbye! Feel free to return if you have more questions about Gyan's work.",
                "See you later! Don't hesitate to reach out if you need more information.",
                "Bye! You can always contact Gyan directly through the contact page.",
                "Have a great day! Check out Gyan's projects when you get a chance."
            ]
        elif any(word in user_message for word in thanks):
            responses = [
                "You're welcome! Is there anything else you'd like to know about Gyan's portfolio?",
                "My pleasure! Gyan would be happy to connect if you have more questions.",
                "Happy to help! Would you like to see Gyan's latest projects?",
                "No problem! Let me know if you need information about skills or experience."
            ]
        elif any(word in user_message for word in skills):
            responses = [
                "Gyan specializes in Python, Django, JavaScript, and modern web development technologies.",
                "The tech stack includes Django, React, PostgreSQL, and various cloud technologies.",
                "Key skills: Full-stack development, AI integration, database design, and API development.",
                "Technical expertise spans web development, machine learning, and cloud deployment."
            ]
        elif any(word in user_message for word in experience):
            responses = [
                "Gyan has X years of professional experience in software development and AI solutions.",
                "Work history includes positions at [Company A] and [Company B], focusing on web technologies.",
                "Professional background combines software engineering with innovative problem-solving.",
                "Experience ranges from startup environments to enterprise-level applications."
            ]
        elif any(word in user_message for word in education):
            responses = [
                "Gyan holds a [Degree] in [Field] from [University].",
                "Educational background includes specialized training in [Specific Technology/Field].",
                "Formal education in computer science complemented by numerous certifications.",
                "Degree from [University] with focus on practical software development."
            ]
        elif any(word in user_message for word in hire):
            responses = [
                "Gyan is available for freelance projects and full-time opportunities. Please check the contact page.",
                "For hiring inquiries, you can reach out directly through the contact form or LinkedIn.",
                "Gyan is open to new opportunities. The resume is available for download in the resume section.",
                "Interested in working together? Let's connect through the contact information provided."
            ]
        elif any(word in user_message for word in services):
            responses = [
                "Services include custom web development, AI solutions, and technical consulting.",
                "Gyan offers full-stack development services from concept to deployment.",
                "Available for project-based work including API development, database design, and more.",
                "Services tailored to client needs with focus on quality and innovative solutions."
            ]
        elif any(word in user_message for word in resume):
            responses = [
                "You can download Gyan's resume from the Resume section of this website.",
                "The resume is available for download - check the navigation menu for the Resume page.",
                "CV download option is provided in the resume section with detailed experience.",
                "Resume PDF is available with complete professional history and skills."
            ]
        elif any(word in user_message for word in social):
            responses = [
                "Social media links are available in the website footer. Connect with Gyan on LinkedIn for professional updates.",
                "You can find all social media profiles at the bottom of each page. GitHub has project code samples.",
                "Social links are in the footer section - including GitHub, LinkedIn, and others.",
                "Connect with Gyan through various platforms - links are at the bottom of the page."
            ]
        elif 'project' in user_message:
            responses = [
                "Recent projects include [Project A], [Project B], and [Project C]. Full details in Projects section.",
                "Portfolio showcases various web applications and AI projects. Visit the Projects page for case studies.",
                "Projects demonstrate skills in Django, React, and machine learning. Each has detailed documentation.",
                "You'll find project examples with descriptions, technologies used, and live demos in the Projects section."
            ]
        elif 'contact' in user_message:
            responses = [
                "Contact information is available on the Contact page. You can also use the form to send a direct message.",
                "You can reach Gyan through email or the contact form. Social media links are also provided.",
                "For professional inquiries, please use the contact form or LinkedIn profile.",
                "Multiple contact options are available - choose your preferred method from the Contact page."
            ]
        elif 'about' in user_message:
            responses = [
                "The About page contains Gyan's professional story, skills, and approach to development.",
                "You'll find a comprehensive professional bio in the About section.",
                "About section highlights Gyan's background, philosophy, and technical capabilities.",
                "Personal and professional details are available in the About page narrative."
            ]
        else:
            responses = [
                "I'm Gyan's portfolio assistant. Could you ask about skills, projects, or experience?",
                "I specialize in answering questions about Gyan's professional background. Try asking about specific skills or projects.",
                "For best results, ask about Gyan's technical skills, work experience, or portfolio projects.",
                "I can tell you about Gyan's qualifications. Try questions like 'What technologies do you know?' or 'Tell me about your experience'."
            ]
        
        return JsonResponse({
            'response': random.choice(responses),
            'suggestions': [
                "Ask about skills",
                "See projects",
                "Request experience details",
                "How to contact"
            ]
        })
    
    except Exception as e:
        return JsonResponse({
            'response': "Apologies, I'm having trouble processing your request. Please try again later.",
            'error': str(e)
        }, status=500)
    

def anpr(request):
    return render(request, 'anpr.html', {
        'plate_result': '---',
        'status_message': 'Ready to upload',
        'status_class': 'success',
        'image_base64': None
    })
    

def process_anpr(request):
    """Handles image upload (file or camera data) and runs the ANPR process."""
    plate_result = "---"
    status_message = "Ready to upload"
    status_class = "success"
    img_bytes = None
    uploaded_file = None
    
    # 1. Image Source Detection and Reading
    try:
        if request.method == 'POST':
            if 'vehicle_image' in request.FILES:
                # Case 1: File Upload (Browse Image)
                uploaded_file = request.FILES['vehicle_image']
                img_bytes = uploaded_file.read()

            elif 'vehicle_image_data' in request.POST:
                # Case 2: Camera Capture (Base64 Data)
                base64_data = request.POST['vehicle_image_data']
                # Clean the Base64 header (e.g., "data:image/jpeg;base64,")
                if ';base64,' in base64_data:
                    _, base64_str = base64_data.split(';base64,')
                else:
                    base64_str = base64_data
                    
                img_bytes = base64.b64decode(base64_str)
            
            # --- Continue Processing if image bytes exist ---
            if img_bytes:
                # Base64 encoding for HTML preview persistence
                image_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # 2. Convert bytes to PIL Image
                img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                
                # 3. Convert to BGR numpy array for ANPR Core
                frame = np.array(img)
                frame = frame[:, :, ::-1] # RGB to BGR conversion
                
                # 4. Run the ANPR core logic
                final_plate = anpr_core.run_anpr(frame)
                
                # 5. Handle Results and Status
                plate_result = final_plate if final_plate and "ERROR" not in final_plate else "NO PLATE DETECTED / CORE ERROR"
                
                if "ERROR" in final_plate:
                     status_message = final_plate
                     status_class = "error"
                elif final_plate:
                    status_message = f"Recognition successful: {final_plate}"
                    status_class = "success"
                else:
                    status_message = "Image processed, but no plate was recognized."
                    status_class = "error"
                
            else:
                # Should not happen if forms are validated, but good for safety
                image_base64 = None
                status_message = "No image data received."
                status_class = "error"

    except Exception as e:
        plate_result = "FATAL ERROR"
        status_message = f"Critical Error in ANPR Core: {type(e).__name__} - {str(e)}"
        status_class = "error"
        print(f"--- ANPR CRITICAL ERROR ---: {e}")
        image_base64 = base64.b64encode(img_bytes).decode('utf-8') if 'img_bytes' in locals() and img_bytes else None

    # Render the page with results and image persistence
    return render(request, 'anpr.html', {
        'plate_result': plate_result,
        'status_message': status_message,
        'status_class': status_class,
        'image_base64': image_base64, 
    })