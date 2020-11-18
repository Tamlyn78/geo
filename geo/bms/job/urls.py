from django.urls import path
from . import views


app_name = 'job'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('new/', views.JobCreateView.as_view(), name='job_new'),
    path('<int:uid>/', views.JobUpdateView.as_view(), name='job_detail'),
]
