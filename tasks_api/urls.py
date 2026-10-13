from django.urls import path
from tasks_api.views import *

app_name = 'tasks'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
]
