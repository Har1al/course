from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch

from tasks_api.models import *


def get_modules_with_tasks():
    return Module.objects.order_by('id').prefetch_related(
        Prefetch(
            'lessons',
            queryset=Lesson.objects.order_by('id').prefetch_related(
                Prefetch(
                    'tasks',
                    queryset=Task.objects.order_by('id')
                )
            ),
        )
    )


class IndexListView(ListView):
    model = Module
    template_name = 'tasks_api/index.html'
    title = 'home'
    context_object_name = 'modules'

    def get_queryset(self):
        return get_modules_with_tasks()


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks_api/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.select_related('lesson__module').prefetch_related(
            Prefetch(
                'examples',
                queryset=Example.objects.order_by('id')
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object.lesson
        context['modules'] = get_modules_with_tasks()
        context['lesson'] = lesson
        context['lesson_tasks'] = lesson.tasks.order_by('id')
        return context
