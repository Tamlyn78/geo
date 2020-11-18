from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # job views
    path('', views.job_list, name='job_list'),
    #path('', views.JobListView.as_view(), name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
]