from django.contrib import admin
from django.urls import path
from mainapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('anpr/', views.anpr, name='anpr'),
    path('process_anpr/', views.process_anpr, name='process_anpr'), 
    path('about/', views.about, name='about'),
    path('resume/', views.resume, name='resume'),
    path('projects/', views.projects_view, name='projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('resume/download/<int:id>/', views.download_resume, name='download_resume'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('chatbot/', views.chatbot, name='chatbot'),

    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='login'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
def health_check(request):
    return JsonResponse({"status": "ok"})