"""Enhanced tree renderer for complete module information."""

from typing import List
from textual.widgets import Tree
from libcst_analysis_tools.analyze_complete import (
    ModuleInfo,
    ImportInfo,
    FunctionInfo,
    VariableInfo,
    get_complete_module_info_from_file
)
from libcst_analysis_tools.list_classes import ClassInfo
from libcst_analysis_tools.list_methods import MethodInfo


class CompleteModuleTreeRenderer:
    """Renderer for complete module information with icons."""
    
    # Emojis for different elements
    IMPORT_EMOJI = "📦"
    FUNCTION_EMOJI = "⚙️"
    CLASS_EMOJI = "🧱"
    METHOD_EMOJI = "🔧"
    VARIABLE_EMOJI = "📊"
    CONSTANT_EMOJI = "🔢"
    
    def fill_tree(self, tree: Tree, data: ModuleInfo) -> None:
        """Fill tree with complete module information."""
        tree.clear()
        tree.root.expand()
        
        # Add imports section
        if data.imports:
            imports_node = tree.root.add(f"📥 Imports ({len(data.imports)})", expand=False)
            for imp in data.imports:
                if imp.is_from:
                    label = f"{self.IMPORT_EMOJI} from {imp.module} import {imp.name}"
                else:
                    label = f"{self.IMPORT_EMOJI} import {imp.name}"
                if imp.alias:
                    label += f" as {imp.alias}"
                label += f" [dim]@{imp.lineno}[/dim]"
                imports_node.add_leaf(label)
        
        # Add module constants
        if data.module_constants:
            constants_node = tree.root.add(f"🔢 Constants ({len(data.module_constants)})", expand=False)
            for const in data.module_constants:
                value_preview = f" = {const.value}" if const.value else ""
                label = f"{self.CONSTANT_EMOJI} {const.name}{value_preview} [dim]@{const.lineno}[/dim]"
                constants_node.add_leaf(label)
        
        # Add module functions
        if data.functions:
            functions_node = tree.root.add(f"⚙️ Functions ({len(data.functions)})", expand=True)
            for func in data.functions:
                params = ", ".join(func.parameters)
                async_marker = "async " if func.is_async else ""
                label = f"{self.FUNCTION_EMOJI} {async_marker}{func.name}({params}) [dim]@{func.lineno}[/dim]"
                functions_node.add_leaf(label)
        
        # Add classes with methods and variables
        if data.classes:
            classes_node = tree.root.add(f"🧱 Classes ({len(data.classes)})", expand=True)
            for cls in data.classes:
                bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
                class_node = classes_node.add(
                    f"{self.CLASS_EMOJI} {cls.name}{bases_str} [dim]@{cls.lineno}[/dim]",
                    expand=True
                )
                
                # Add class variables
                class_vars = data.class_variables.get(cls.name, [])
                if class_vars:
                    vars_node = class_node.add(f"📊 Variables ({len(class_vars)})", expand=False)
                    for var in class_vars:
                        value_preview = f" = {var.value}" if var.value else ""
                        label = f"{self.VARIABLE_EMOJI} {var.name}{value_preview} [dim]@{var.lineno}[/dim]"
                        vars_node.add_leaf(label)
                
                # Add methods
                methods = data.methods_by_class.get(cls.name, [])
                if methods:
                    for method in methods:
                        params = ", ".join(method.parameters)
                        decorators = ""
                        if method.is_staticmethod:
                            decorators = "@staticmethod "
                        elif method.is_classmethod:
                            decorators = "@classmethod "
                        elif method.is_property:
                            decorators = "@property "
                        async_marker = "async " if method.is_async else ""
                        label = f"{self.METHOD_EMOJI} {decorators}{async_marker}{method.name}({params}) [dim magenta]@{method.lineno}[/dim magenta]"
                        class_node.add_leaf(label)
    
    def filter_data(self, data: ModuleInfo, filter_text: str) -> ModuleInfo:
        """Filter module data based on text (placeholder - returns all data for now)."""
        # For now, return all data - filtering can be complex with nested structure
        return data
