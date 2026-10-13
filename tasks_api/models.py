from django.db import models

# Create your models here.

class Module(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=64)
    module = models.ForeignKey(to=Module, on_delete=models.CASCADE, related_name='lessons')

    def __str__(self):
        return f'{self.title} --- {self.module.title}'


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    lesson = models.ForeignKey(to=Lesson, on_delete=models.CASCADE, default=1, related_name='tasks')

    def __str__(self):
        return f'{self.title}  ---> {self.lesson.title}'

class Example(models.Model):
    input = models.CharField(max_length=255)
    output = models.CharField(max_length=255)
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE, related_name='examples')



