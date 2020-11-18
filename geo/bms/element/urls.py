from django.urls import path
from . import views


app_name = 'element'

urlpatterns = [
    path('', views.element_list, name='element_list'),
    #path('new/', views.ElementCreateView.as_view(), name='element_new'),
    #path('<int:uid>/', views.ElementUpdateView.as_view(), name='element_detail'),
]
