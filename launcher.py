"""Настольный запуск PY/LAB: локальный сервер + приглашение в консоли.

Сервер работает в том же процессе, что и окно консоли, поэтому при закрытии
окна (или Ctrl+C) он останавливается вместе с ним и порт освобождается.
"""
import os
import signal
import socket
import subprocess
import sys
from socketserver import ThreadingMixIn

# macOS: PyLab.app, запущенный из Finder, не получает окна Терминала — тогда открываем себя в нём,
# иначе приглашение со ссылкой никто не увидит
if sys.platform == 'darwin' and getattr(sys, 'frozen', False) and not (sys.stdin and sys.stdin.isatty()):
    subprocess.Popen(['open', '-a', 'Terminal', sys.executable])
    sys.exit(0)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course.settings')
os.environ['COURSE_DESKTOP'] = '1'

import django  # noqa: E402

django.setup()

from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.servers.basehttp import WSGIRequestHandler, WSGIServer  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

HOST = '127.0.0.1'
PORTS = range(8000, 8100)

BANNER = r"""
    ______  __   ____    ___    ____
   / __ \ \/ / _/_/ /   /   |  / __ )
  / /_/ /\  /_/_// /   / /| | / __  |
 / ____/ / //_/ / /___/ ___ |/ /_/ /
/_/     /_/_/  /_____/_/  |_/_____/
"""

RESET, BOLD, DIM = '\033[0m', '\033[1m', '\033[2m'
YELLOW, CYAN, GREEN, GRAY = '\033[38;5;220m', '\033[38;5;87m', '\033[38;5;114m', '\033[38;5;245m'


def enable_ansi():
    """Включает цвета ANSI в консоли Windows."""
    if os.name != 'nt':
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        kernel32.SetConsoleTitleW('PY/LAB')
    except Exception:
        pass
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except Exception:
            pass


class QuietHandler(WSGIRequestHandler):
    """Не засоряем консоль логом каждого запроса."""

    def log_message(self, format, *args):
        pass


class Server(ThreadingMixIn, WSGIServer):
    daemon_threads = True

    def server_bind(self):
        # Порт не должен делиться с другим процессом (на Windows SO_REUSEADDR это разрешает)
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def make_server():
    for port in PORTS:
        try:
            # На Windows SO_REUSEADDR позволил бы занять чужой порт, поэтому там он выключен;
            # на macOS/Linux он безопасен и нужен, чтобы после перезапуска сразу снова взять тот же порт
            server = Server((HOST, port), QuietHandler, allow_reuse_address=os.name != 'nt')
        except OSError:
            continue
        server.set_app(StaticFilesHandler(get_wsgi_application()))
        return server, port
    raise SystemExit(f'Не удалось найти свободный порт в диапазоне {PORTS.start}–{PORTS.stop - 1}')


def print_welcome(url):
    print(f'{YELLOW}{BOLD}{BANNER}{RESET}')
    print(f'{GRAY}  Каталог заданий по Python{RESET}\n')
    print(f'  {GREEN}●{RESET} Сервер запущен\n')
    print(f'  {BOLD}Откройте в браузере:{RESET}  {CYAN}{BOLD}{url}{RESET}\n')
    print(f'{DIM}  Чтобы остановить сервер, закройте это окно или нажмите Ctrl+C{RESET}\n')


def stop(signum, frame):
    raise KeyboardInterrupt


def main():
    sys.stdout.reconfigure(line_buffering=True)
    enable_ansi()
    # Закрытие окна Терминала (SIGHUP) и kill (SIGTERM) завершают сервер так же, как Ctrl+C
    for name in ('SIGHUP', 'SIGTERM'):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), stop)
    server, port = make_server()
    print_welcome(f'http://localhost:{port}/')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f'\n  {YELLOW}●{RESET} Сервер остановлен, порт {port} свободен.\n')


if __name__ == '__main__':
    main()
