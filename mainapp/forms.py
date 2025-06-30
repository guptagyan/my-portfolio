from django import forms
from .models import Project, Resume
from django.core.validators import FileExtensionValidator

class ProfileForm(forms.ModelForm):
    # Remove 'name' field since it doesn't exist in your Resume model
    class Meta:
        model = Resume
        fields = ['resume_file']  # Only include fields that exist in the model
        widgets = {
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx'  # Restrict file types
            }),
        }
    
    def clean_resume_file(self):
        file = self.cleaned_data.get('resume_file')
        if file:
            if not file.name.lower().endswith(('.pdf', '.docx')):
                raise forms.ValidationError("Only PDF and DOCX files are allowed.")
            if file.size > 5*1024*1024:  # 5MB limit
                raise forms.ValidationError("File size must be less than 5MB")
        return file

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'github_link', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Project Description'
            }),
            'github_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/your-project'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_thumbnail(self):
        image = self.cleaned_data.get('thumbnail')
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise forms.ValidationError("Only image files are allowed")
        return image