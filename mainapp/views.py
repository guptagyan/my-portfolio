import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from portfolio import settings
from .forms import ProfileForm, ProjectForm
from .models import Project, Resume
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

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