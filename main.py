import os
import subprocess
import sys
import threading
from flask import Flask, send_from_directory

# Пути к файлам
frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
backend_file = os.path.join(os.path.dirname(__file__), 'app.py')

def run_backend():
    """Запуск Flask сервера"""
    os.environ['FLASK_ENV'] = 'production'
    subprocess.Popen([sys.executable, backend_file])

def run_frontend():
    """Запуск React приложения"""
    os.chdir(frontend_dir)
    subprocess.Popen(['npm', 'start'])

if __name__ == '__main__':
    # Запускаем оба процесса в отдельных потоках
    threading.Thread(target=run_backend, daemon=True).start()
    threading.Thread(target=run_frontend, daemon=True).start()
    
    # Держим программу активной
    input("Нажмите Enter для выхода...\n")