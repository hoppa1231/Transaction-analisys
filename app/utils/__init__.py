import os
import sys

# Определяем путь к корневой директории проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = BASE_DIR[:BASE_DIR.find('app')]
print('[INFO] BASE_DIR:', BASE_DIR)
# Добавляем корневую папку в sys.path
sys.path.append(BASE_DIR)