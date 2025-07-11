from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.utils.text import slugify
from pydantic import ValidationError

class Resume(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="User Account"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Full Name",
        help_text="Enter your full name"
    )
    resume_file = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'docx'])],
        verbose_name="Resume File",
        help_text="Upload PDF or DOCX file only"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Upload Date")

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        ordering = ['-uploaded_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Resume ({self.name})"
        return f"Resume of {self.name}"

    def get_absolute_url(self):
        return reverse('resume_detail', kwargs={'pk': self.pk})

    def clean(self):
        if not self.name:
            raise ValidationError("Name field cannot be empty")
        if self.resume_file and self.resume_file.size > 5*1024*1024:  # 5MB limit
            raise ValidationError("File size must be less than 5MB")

class Project(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Project Title"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Automatically generated from title"
    )
    description = models.TextField(
        verbose_name="Project Description"
    )
    github_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="GitHub Repository"
    )
    thumbnail = models.ImageField(
        upload_to='project_thumbs/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Thumbnail Image",
        help_text="Recommended size: 800x450px"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creation Date"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Project Owner"
    )
    technologies = models.TextField(
        blank=True,
        null=True,
        help_text="Comma separated list of technologies used"
    )

    features = models.TextField(
        blank=True,
        null=True,
        help_text="Key features (one per line)"
    )

    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('completed', 'Completed'), ('archived', 'Archived')],
        default='completed'
    )


    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if not self.title:
            raise ValidationError("Project title cannot be empty")
        if self.thumbnail and self.thumbnail.size > 10*1024*1024:  # 10MB limit
            raise ValidationError("Thumbnail size must be less than 10MB")