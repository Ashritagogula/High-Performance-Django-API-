import os

def create_file(path, content):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

# requirements.txt
create_file("requirements.txt", """Django>=4.2,<5.0
psycopg2-binary>=2.9
Faker>=19.0
requests>=2.31.0
gunicorn>=21.0.0
""")

# Dockerfile
create_file("Dockerfile", """FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "blog_project.wsgi:application"]
""")

# docker-compose.yml
create_file("docker-compose.yml", """version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: blog
      POSTGRES_USER: bloguser
      POSTGRES_PASSWORD: blogpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bloguser -d blog"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: >
      sh -c "python manage.py makemigrations api &&
             python manage.py migrate &&
             python manage.py seed_db &&
             python manage.py runserver 0.0.0.0:8000"
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=blog
      - DB_USER=bloguser
      - DB_PASS=blogpassword
      - DEBUG=1
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
""")

# .env.example
create_file(".env.example", """DB_HOST=db
DB_NAME=blog
DB_USER=bloguser
DB_PASS=blogpassword
DEBUG=1
""")

# manage.py
create_file("manage.py", """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""")

# blog_project/settings.py
create_file("blog_project/settings.py", """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-test-key'
DEBUG = os.environ.get('DEBUG', '0') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
]

MIDDLEWARE = [
    'api.middleware.QueryCountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'blog'),
        'USER': os.environ.get('DB_USER', 'bloguser'),
        'PASSWORD': os.environ.get('DB_PASS', 'blogpassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""")

# blog_project/urls.py
create_file("blog_project/urls.py", """from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', health_check),
]
""")

# blog_project/wsgi.py
create_file("blog_project/wsgi.py", """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
application = get_wsgi_application()
""")

# api/apps.py
create_file("api/apps.py", """from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
""")

# api/models.py
create_file("api/models.py", """from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author_name} on {self.post}'
""")

# api/urls.py
create_file("api/urls.py", """from django.urls import path
from . import views

urlpatterns = [
    path('posts/naive', views.posts_naive, name='posts-naive'),
    path('posts/optimized', views.posts_optimized, name='posts-optimized'),
    path('posts/advanced', views.posts_advanced, name='posts-advanced'),
]
""")

# api/middleware.py
create_file("api/middleware.py", """from django.db import connection
from django.conf import settings

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            response['X-Query-Count'] = str(len(connection.queries))
        return response
""")

# api/management/commands/seed_db.py
create_file("api/management/commands/seed_db.py", """from django.core.management.base import BaseCommand
from api.models import Author, Post, Comment
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seeds the database with Authors, Posts, and Comments for benchmarking'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write('Deleting old data...')
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Author.objects.all().delete()

        self.stdout.write('Creating new data...')
        
        authors = []
        for _ in range(20):
            authors.append(Author(name=fake.name(), bio=fake.text()))
        Author.objects.bulk_create(authors)
        authors = list(Author.objects.all())

        posts = []
        for author in authors:
            for _ in range(10):
                posts.append(Post(
                    author=author,
                    title=fake.sentence(),
                    content=fake.text(),
                    views=random.randint(0, 1000)
                ))
        Post.objects.bulk_create(posts)
        posts = list(Post.objects.all())

        comments = []
        for post in posts:
            for _ in range(10):
                comments.append(Comment(
                    post=post,
                    author_name=fake.name(),
                    body=fake.sentence()
                ))
        # Batch create comments as it might be large
        Comment.objects.bulk_create(comments, batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded: 20 Authors, 200 Posts, 2000 Comments.'))
""")

# api/views.py
create_file("api/views.py", """from django.http import JsonResponse
from .models import Post, Author
from django.db.models import Count, Sum, F, Window
import json

def posts_naive(request):
    posts = Post.objects.all()
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comments.count()
        })
    return JsonResponse(data, safe=False)

def posts_optimized(request):
    posts = Post.objects.select_related('author').annotate(comment_count=Count('comments'))
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comment_count
        })
    return JsonResponse(data, safe=False)

def posts_advanced(request):
    # We want total_author_views which is the sum of views of all posts by the same author.
    # We use a Window function with Sum('views') partitioned by 'author_id'.
    # Since we are querying Post, the partition_by will be the author_id of the Post.
    
    # Wait, the prompt says: 
    # Window(expression=Sum('author__posts__views'), partition_by=[F('author_id')])
    # Actually if we query Post, Sum('views') partitioned by author_id sums the views of the posts in the current table over the partition.
    
    # Wait, if we use annotate(total_author_views=Window(expression=Sum('views'), partition_by=[F('author_id')])),
    # does that interfere with Count('comments')? Let's check. Window functions and Group By (used by Count) can sometimes clash.
    # To be safe from grouping issues, we can use a Subquery.
    # The prompt allows either: "using a window function or subquery".
    # Subquery is usually simpler to get right in Django without GROUP BY conflicts.
    
    from django.db.models import Subquery, OuterRef
    
    # Using Subquery:
    author_views_sq = Post.objects.filter(author_id=OuterRef('author_id')).values('author_id').annotate(total_views=Sum('views')).values('total_views')
    
    posts = Post.objects.select_related('author').annotate(
        comment_count=Count('comments'),
        total_author_views=Subquery(author_views_sq)
    )
    
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comment_count,
            "total_author_views": post.total_author_views or 0
        })
    return JsonResponse(data, safe=False)
""")

# Create necessary __init__.py files
create_file("blog_project/__init__.py", "")
create_file("api/__init__.py", "")
create_file("api/management/__init__.py", "")
create_file("api/management/commands/__init__.py", "")

# README.md
create_file("README.md", """# N+1 Queries Optimization with Django REST API

This project demonstrates how to identify and resolve N+1 queries in Django.

## Instructions
1. Run `docker-compose up --build`
2. Wait for the DB to initialize, migrations to run, and the database to seed.
3. Access API endpoints: `/api/posts/naive`, `/api/posts/optimized`, `/api/posts/advanced`.
4. Run `python benchmark.py http://localhost:8000/api/posts/naive` to see the results.
""")
