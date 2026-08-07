from django.urls import path
from . import views

urlpatterns = [
    path('posts/naive', views.posts_naive, name='posts-naive'),
    path('posts/optimized', views.posts_optimized, name='posts-optimized'),
    path('posts/advanced', views.posts_advanced, name='posts-advanced'),
]
