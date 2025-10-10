import os

def generate_simple_docs(root_dir=".", output_file="PROJECT.md", exclude_files_list=None):
    """
    Самый простой генератор документации проекта
    
    Args:
        root_dir: Корневая директория проекта
        output_file: Имя выходного файла
        exclude_files_list: Список файлов для исключения (например, ['config.py', 'secrets.json'])
    """
    exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules'}
    exclude_files = {'.DS_Store', '.env'}
    
    # Добавляем пользовательские исключения
    if exclude_files_list:
        exclude_files.update(exclude_files_list)
    
    with open(output_file, 'w', encoding='utf-8') as md:
        md.write("# Project Documentation\n\n")
        
        # 1. Структура проекта
        md.write("## 1. Структура проекта\n")
        md.write("```\n")
        
        def print_tree(path, prefix=""):
            try:
                items = os.listdir(path)
            except:
                return
                
            items.sort()
            for i, item in enumerate(items):
                full_path = os.path.join(path, item)
                is_last = i == len(items) - 1
                
                if item in exclude_dirs or item in exclude_files:
                    continue
                
                if os.path.isdir(full_path):
                    md.write(f"{prefix}{'┗ ' if is_last else '┣ '}{item}\n")
                    new_prefix = prefix + ("   " if is_last else "┃  ")
                    print_tree(full_path, new_prefix)
                else:
                    md.write(f"{prefix}{'┗ ' if is_last else '┣ '}{item}\n")
        
        md.write(f"{os.path.basename(root_dir)}\n")
        print_tree(root_dir)
        md.write("```\n\n")
        
        # 2. Содержимое файлов
        md.write("## 2. Содержимое файлов\n\n")
        
        for root, dirs, files in os.walk(root_dir):
            # Убираем исключенные директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                    
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except:
                        content = "# Бинарный файл или ошибка чтения\n"
                
                md.write(f"### /{relative_path}\n")
                md.write(f"```{os.path.splitext(file)[1][1:] or 'text'}\n")
                md.write(content)
                if content and not content.endswith('\n'):
                    md.write("\n")
                md.write("```\n\n")