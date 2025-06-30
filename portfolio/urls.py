from django.contrib import admin
from django.urls import path, include  # include को import करें
from mainapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('resume/', views.resume, name='resume'),
    path('projects/', views.projects_view, name='projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('resume/download/<int:id>/', views.download_resume, name='download_resume'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    
    # Authentication URLs
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('oauth/', include('social_django.urls', namespace='social')),  # GitHub OAuth URLs
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)