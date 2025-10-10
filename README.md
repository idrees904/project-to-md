```md
# project-to-md

Convert your project’s file structure and contents into a single Markdown file.

Perfect for documentation, code reviews, onboarding, or archiving your codebase in a human-readable format.

---

## 🚀 Features

- 🌲 Visual ASCII tree of your directory structure  
- 📄 Full contents of every file (with syntax highlighting based on file extension)  
- 🧹 Automatically skips common ignored folders (`node_modules`, `.git`, `venv`, etc.)  
- 🛠️ Customizable: exclude any additional files via argument  
- 💾 Output: one clean `.md` file — easy to share or version

---

## 📦 Installation

Just copy `project_to_md.py` to your project or add it to your scripts folder — no dependencies required!

> ✅ Works with Python 3.6+

---

## ▶️ Usage

```bash
python project_to_md.py
```

This will generate `PROJECT.md` in the current directory.

### Custom output file and exclusions

You can also call the function directly in Python:

```python
from project_to_md import generate_simple_docs

generate_simple_docs(
    root_dir=".",
    output_file="docs/project_summary.md",
    exclude_files_list=["secrets.json", "local_config.py"]
)
```

---

## 📁 Example Output

The generated `PROJECT.md` looks like this:

```
# Project Documentation

## 1. Структура проекта
```
my-project
┣ .gitignore
┣ README.md
┗ src
   ┗ main.py
```

## 2. Содержимое файлов

### /README.md
```md
# My Project
...
```

### /src/main.py
```py
print("Hello, world!")
```
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ for developers who love clean, shareable code docs.
```