from django.core.management.base import BaseCommand
import json
from tasks_api.models import Module, Lesson, Task, Example

class Command(BaseCommand):
    help = 'Load demo data из JSON в БД'

def add_arguments(self, parser):
    parser.add_argument('json_path', type=str, help='Путь к файлу JSON с данными')

def handle(self, *args, **options):
    json_path = options['json_path']
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Пробегаемся по структуре JSON
    for mod in data.get('modules', []):
        mod_title = mod.get('title')
        module, _ = Module.objects.get_or_create(title=mod_title)

        for les in mod.get('lessons', []):
            les_title = les.get('title')
            lesson, _ = Lesson.objects.get_or_create(title=les_title, module=module)

            for tsk in les.get('tasks', []):
                task_title = tsk.get('title')
                description = tsk.get('statement', '')
                task_defaults = {'description': description}
                task, created = Task.objects.get_or_create(title=task_title, lesson=lesson, defaults=task_defaults)
                if not created:
                    # Обновим описание, если оно поменялось
                    if task.description != description:
                        task.description = description
                        task.save()

                for ex in tsk.get('examples', []):
                    input_text = ex.get('input', '')
                    output_text = ex.get('output', '')
                    Example.objects.get_or_create(input=input_text, output=output_text, task=task)

    self.stdout.write(self.style.SUCCESS('Demo data загружены успешно'))