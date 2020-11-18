from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('jobs', views.job_list, name='job_list'),
    path('job/<int:uid>/', views.JobUpdateView.as_view(), name='job_detail'),
]
