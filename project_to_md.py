import os
from pathlib import Path
import fnmatch

def generate_simple_docs(root_dir=".", output_file="PROJECT.md", 
                        exclude_items=None, include_dirs=None, 
                        exclude_extensions=None):
    """
    Расширенный генератор документации проекта с гибкой настройкой
    
    Args:
        root_dir: Корневая директория проекта (относительно которой строятся пути)
        output_file: Имя выходного файла
        exclude_items: Список файлов, каталогов и паттернов для исключения 
                      (например, ['config.py', 'temp_dir', '*.log'])
        include_dirs: Список каталогов для включения в структуру (если None - все)
                     Пути указываются относительно root_dir
                     Например: ['src', 'tests', 'app/api/v1/documents']
        exclude_extensions: Список расширений файлов для исключения
                          (например, ['.pyc', '.log', '.tmp'])
    """
    
    # Преобразуем root_dir в абсолютный путь для надежности
    root_dir = os.path.abspath(root_dir)
    root_path = Path(root_dir)
    
    # Базовые исключения
    exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.idea', '.vscode', 'build', 'dist'}
    exclude_files = {'.DS_Store', '.env', '.gitignore'}
    exclude_patterns = []
    
    # Добавляем пользовательские исключения
    if exclude_items:
        for item in exclude_items:
            if '*' in item or '?' in item:
                exclude_patterns.append(item)
            elif os.path.isdir(os.path.join(root_dir, item)) or '/' in item or '\\' in item:
                exclude_dirs.add(item.rstrip('/').rstrip('\\'))
            else:
                exclude_files.add(item)
    
    # Добавляем исключения по расширениям
    if exclude_extensions:
        exclude_extensions = set(ext if ext.startswith('.') else f'.{ext}' 
                                 for ext in exclude_extensions)
    else:
        exclude_extensions = set()
    
    # Нормализуем пути для include_dirs
    if include_dirs:
        normalized_include_dirs = []
        for d in include_dirs:
            clean_path = d.lstrip('/').lstrip('\\')
            normalized = os.path.normpath(clean_path)
            normalized_include_dirs.append(normalized)
            print(f"Включение директории: {normalized}")
        
        include_dirs = normalized_include_dirs
        include_paths = [root_path / d for d in include_dirs]
        
        # Проверяем существование директорий
        for incl_path in include_paths:
            if not incl_path.exists():
                print(f"Предупреждение: Директория {incl_path} не существует!")
    else:
        include_paths = None
    
    def should_exclude(path, name, is_dir):
        """Проверяет, нужно ли исключить элемент"""
        if name in (exclude_dirs if is_dir else exclude_files):
            return True
        
        if not is_dir and exclude_extensions:
            ext = os.path.splitext(name)[1].lower()
            if ext in exclude_extensions:
                return True
        
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
            if fnmatch.fnmatch(str(path), pattern):
                return True
        
        return False
    
    def is_path_in_included_dirs(path):
        """Проверяет, находится ли путь внутри одной из включенных директорий"""
        if include_paths is None:
            return True
        
        path_obj = Path(path)
        
        # Проверяем, является ли путь самой включенной директорией
        # или находится внутри неё
        for incl_path in include_paths:
            try:
                if path_obj == incl_path or incl_path in path_obj.parents:
                    return True
            except Exception:
                continue
        
        return False
    
    def get_relative_path_for_display(path):
        """Получает относительный путь для отображения"""
        try:
            rel_path = os.path.relpath(path, root_dir)
            if rel_path == '.':
                return os.path.basename(root_dir)
            return rel_path.replace('\\', '/')
        except:
            return str(path)
    
    def should_display_in_tree(path, is_dir):
        """Определяет, нужно ли отображать элемент в дереве структуры"""
        if include_paths is None:
            return True
        
        # Всегда показываем корневую директорию
        if os.path.abspath(path) == root_dir:
            return True
        
        # Проверяем, находится ли путь внутри включенных директорий
        return is_path_in_included_dirs(path)
    
    print(f"Корневая директория: {root_dir}")
    print(f"Включенные директории: {include_dirs}")
    
    with open(output_file, 'w', encoding='utf-8') as md:
        md.write("# Project Documentation\n\n")
        
        # Информация о включенных директориях
        if include_dirs:
            md.write(f"**Сгенерировано для директорий:**\n")
            for d in include_dirs:
                md.write(f"- `{d}`\n")
            md.write("\n")
        else:
            md.write("**Сгенерировано для всего проекта**\n\n")
        
        # 1. Структура проекта
        md.write("## 1. Структура проекта\n")
        md.write("```\n")
        
        def print_tree(path, prefix="", show_root=True):
            """Рекурсивно печатает дерево директорий только для включенных путей"""
            try:
                items = os.listdir(path)
            except PermissionError:
                if show_root:
                    md.write(f"{prefix}[доступ запрещен]\n")
                return
            except Exception as e:
                if show_root:
                    md.write(f"{prefix}[ошибка: {e}]\n")
                return
            
            items.sort()
            
            # Фильтруем элементы
            filtered_items = []
            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                
                # Пропускаем исключенные элементы
                if should_exclude(full_path, item, is_dir):
                    continue
                
                # Проверяем, нужно ли отображать этот элемент в дереве
                if not should_display_in_tree(full_path, is_dir):
                    continue
                
                filtered_items.append((item, full_path, is_dir))
            
            for i, (item, full_path, is_dir) in enumerate(filtered_items):
                is_last = i == len(filtered_items) - 1
                
                if is_dir:
                    if show_root:
                        md.write(f"{prefix}{'┗ ' if is_last else '┣ '}{item}/\n")
                    new_prefix = prefix + ("   " if is_last else "┃  ")
                    # Для поддиректорий всегда показываем содержимое
                    print_tree(full_path, new_prefix, True)
                else:
                    if show_root:
                        md.write(f"{prefix}{'┗ ' if is_last else '┣ '}{item}\n")
        
        # Печатаем корневую структуру
        root_name = os.path.basename(root_dir)
        md.write(f"{root_name}/\n")
        
        if include_paths:
            # Создаем множество для отслеживания уже обработанных родительских путей
            processed_parents = set()
            
            # Для каждой включенной директории
            for incl_path in include_paths:
                # Получаем относительный путь от root_dir
                rel_path = os.path.relpath(incl_path, root_dir)
                path_parts = rel_path.split(os.sep)
                
                # Проходим по всем уровням пути
                current_path = root_dir
                for i, part in enumerate(path_parts):
                    current_path = os.path.join(current_path, part)
                    
                    # Если этот путь еще не обработан
                    if current_path not in processed_parents:
                        # Определяем отступ для этого уровня
                        indent = "   " * i
                        
                        # Проверяем, есть ли другие директории на этом уровне
                        parent_dir = os.path.dirname(current_path)
                        if os.path.exists(parent_dir):
                            try:
                                siblings = os.listdir(parent_dir)
                                # Определяем, последний ли это элемент в родительской директории
                                is_last = True
                                for sibling in sorted(siblings):
                                    sibling_path = os.path.join(parent_dir, sibling)
                                    if (os.path.isdir(sibling_path) and 
                                        should_display_in_tree(sibling_path, True) and
                                        sibling_path != current_path):
                                        is_last = False
                                        break
                            except:
                                is_last = True
                        else:
                            is_last = True
                        
                        # Печатаем текущий уровень
                        if i == len(path_parts) - 1:
                            # Это конечная директория - добавляем слеш
                            md.write(f"{indent}{'┗ ' if is_last else '┣ '}{part}/\n")
                            
                            # Печатаем содержимое конечной директории
                            content_prefix = indent + ("   " if is_last else "┃  ")
                            print_tree(current_path, content_prefix, True)
                        else:
                            # Это промежуточная директория
                            md.write(f"{indent}{'┗ ' if is_last else '┣ '}{part}/\n")
                        
                        processed_parents.add(current_path)
        else:
            # Если нет include_dirs, показываем всё
            print_tree(root_dir, "", True)
            
        md.write("```\n\n")
        
        # 2. Содержимое файлов
        md.write("## 2. Содержимое файлов\n\n")
        
        # Собираем все файлы для обработки
        files_to_process = []
        
        if include_paths:
            # Обрабатываем только указанные директории
            for incl_path in include_paths:
                if incl_path.exists():
                    for root, dirs, files in os.walk(incl_path):
                        # Фильтруем директории
                        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), d, True)]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            if not should_exclude(file_path, file, False):
                                files_to_process.append(file_path)
        else:
            # Обрабатываем всё
            for root, dirs, files in os.walk(root_dir):
                # Фильтруем директории
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), d, True)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if not should_exclude(file_path, file, False):
                        files_to_process.append(file_path)
        
        # Сортируем файлы для консистентности
        files_to_process.sort()
        
        # Обрабатываем каждый файл
        for file_path in files_to_process:
            relative_path = get_relative_path_for_display(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    content = "# Бинарный файл или ошибка чтения\n"
            except Exception as e:
                content = f"# Ошибка чтения файла: {str(e)}\n"
            
            md.write(f"### /{relative_path}\n")
            
            # Определяем расширение для подсветки синтаксиса
            ext = os.path.splitext(file_path)[1][1:] or 'text'
            md.write(f"```{ext}\n")
            md.write(content)
            if content and not content.endswith('\n'):
                md.write("\n")
            md.write("```\n\n")

# Примеры использования:

# 1. Только для конкретных модулей
# generate_simple_docs(
#     root_dir=".", 
#     output_file="MODULE_DOC.md",
#     include_dirs=["src/module1", "src/module2", "tests/test_module1"],
#     exclude_items=["*.pyc", "__pycache__", "temp.log"],
#     exclude_extensions=[".log", ".tmp"]
# )

# 2. Для всего проекта, но с исключениями
# generate_simple_docs(
#     root_dir=".", 
#     output_file="PROJECT.md",
#     exclude_items=["config.py", "secrets.json", "temp_dir"],
#     exclude_extensions=[".pyc", ".log"]
# )

# 3. Для конкретной поддиректории
# generate_simple_docs(
#     root_dir="src", 
#     output_file="SRC_DOC.md",
#     include_dirs=["module1", "module2"],
#     exclude_items=["tests"]
# )
