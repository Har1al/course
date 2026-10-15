# Сборка настольного приложения: .venv\Scripts\pyinstaller pylab.spec
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Данные Django (шаблоны и статика админки); из переводов оставляем только ru и en
django_datas = [
    (src, dst) for src, dst in collect_data_files('django')
    if '\\locale\\' not in src and '/locale/' not in src
    or any(f'{sep}locale{sep}{lang}{sep}' in src for lang in ('ru', 'en') for sep in ('\\', '/'))
]

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    datas=[
        ('db.sqlite3', '.'),
        ('static', 'static'),
        ('tasks_api/templates', 'tasks_api/templates'),
        *django_datas,
    ],
    hiddenimports=[
        'course.settings',
        'course.urls',
        *collect_submodules('tasks_api'),
        *collect_submodules('django.contrib.admin'),
        *collect_submodules('django.contrib.auth'),
        *collect_submodules('django.contrib.contenttypes'),
        *collect_submodules('django.contrib.sessions'),
        *collect_submodules('django.contrib.messages'),
        *collect_submodules('django.contrib.staticfiles'),
        *collect_submodules('django.db.backends.sqlite3'),
        *collect_submodules('django.template'),
        *collect_submodules('django.templatetags'),
    ],
    excludes=['PyQt6', 'flask', 'jinja2', 'werkzeug', 'tkinter', 'PyInstaller'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PyLab',
    console=True,
    upx=False,
)
