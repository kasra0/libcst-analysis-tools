import textual
from textual.app import App
import inspect
from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods, get_all_classes_with_methods_from_file

print("Textual version:", textual.__version__)

# Récupère et lit le fichier
module_file = inspect.getfile(App)
with open(module_file, 'r', encoding='utf-8') as f:
    source_code = f.read()

# ⚡ UN SEUL parsing pour TOUT!
for cls, methods in get_all_classes_with_methods_from_file(module_file):
    print(cls.name)
    for method in methods:
        print(f"  - {method.name} (line {method.lineno})")
