"""Enhanced tree renderer for complete module information."""

from typing import List, Union
from textual.widgets import Tree
from libcst_analysis_tools.analyze_complete import (
    ModuleInfo
)
from libcst_analysis_tools.view.Renderer.TreeRenderer import TreeRenderer


class CompleteModuleTreeRenderer(TreeRenderer[ModuleInfo]):
    """Renderer for complete module information with icons."""
    
    # Emojis for different elements
    IMPORT_EMOJI   = "📦"
    FUNCTION_EMOJI = "⚙️ "
    CLASS_EMOJI    = "🧱"
    METHOD_EMOJI   = "🔧"
    VARIABLE_EMOJI = "📊"
    CONSTANT_EMOJI = "🔢"
    
    def fill_tree(self, tree: Tree, data: Union[ModuleInfo, List[ModuleInfo]]) -> None:
        """Fill tree with complete module information."""
        # Handle both single ModuleInfo and list
        if isinstance(data, list):
            # If it's a list, just use the first one or return if empty
            if not data:
                tree.clear()
                return
            module_data = data[0]
        else:
            module_data = data
            
        tree.clear()
        tree.root.expand()
        
        # Add imports section
        if module_data.imports:
            imports_node = tree.root.add(f"📥 Imports ({len(module_data.imports)})", expand=False)
            for imp in module_data.imports:
                if imp.is_from:
                    label = f"{self.IMPORT_EMOJI} from {imp.module} import {imp.name}"
                else:
                    label = f"{self.IMPORT_EMOJI} import {imp.name}"
                if imp.alias:
                    label += f" as {imp.alias}"
                label += f" [dim]@{imp.lineno}[/dim]"
                imports_node.add_leaf(label)
        
        # Add module constants
        if module_data.module_constants:
            constants_node = tree.root.add(f"🔢 Constants ({len(module_data.module_constants)})", expand=False)
            for const in module_data.module_constants:
                value_preview = f" = {const.value}" if const.value else ""
                label = f"{self.CONSTANT_EMOJI} {const.name}{value_preview} [dim]@{const.lineno}[/dim]"
                constants_node.add_leaf(label)
        
        # Add module functions
        if module_data.functions:
            functions_node = tree.root.add(f"⚙️  Functions ({len(module_data.functions)})", expand=True)
            for func in module_data.functions:
                params = ", ".join(func.parameters)
                async_marker = "async " if func.is_async else ""
                label = f"{self.FUNCTION_EMOJI} {async_marker}{func.name}({params}) [dim]@{func.lineno}[/dim]"
                functions_node.add_leaf(label)
        
        # Add classes with methods and variables
        if module_data.classes:
            classes_node = tree.root.add(f"🧱 Classes ({len(module_data.classes)})", expand=True)
            for cls in module_data.classes:
                bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
                class_node = classes_node.add(
                    f"{self.CLASS_EMOJI} {cls.name}{bases_str} [dim]@{cls.lineno}[/dim]",
                    expand=True
                )
                
                # Add class variables
                class_vars = module_data.class_variables.get(cls.name, [])
                if class_vars:
                    vars_node = class_node.add(f"📊 Variables ({len(class_vars)})", expand=False)
                    for var in class_vars:
                        value_preview = f" = {var.value}" if var.value else ""
                        label = f"{self.VARIABLE_EMOJI} {var.name}{value_preview} [dim]@{var.lineno}[/dim]"
                        vars_node.add_leaf(label)
                
                # Add methods
                methods = module_data.methods_by_class.get(cls.name, [])
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
    
    def filter_data(self, data: Union[ModuleInfo, List[ModuleInfo]], filter_text: str) -> Union[ModuleInfo, List[ModuleInfo]]:
        """Filter module data based on text."""
        # Handle list wrapping
        if isinstance(data, list):
            if not data:
                return data
            module_info = data[0]
        else:
            module_info = data
        
        # If no filter, return original
        if not filter_text:
            return data
        
        filter_lower = filter_text.lower()
        
        # Filter imports
        filtered_imports = [
            imp for imp in module_info.imports
            if filter_lower in imp.name.lower() or 
               (imp.module and filter_lower in imp.module.lower()) or
               (imp.alias and filter_lower in imp.alias.lower())
        ]
        
        # Filter module constants
        filtered_constants = [
            const for const in module_info.module_constants
            if filter_lower in const.name.lower()
        ]
        
        # Filter module functions
        filtered_functions = [
            func for func in module_info.functions
            if filter_lower in func.name.lower()
        ]
        
        # Filter classes and their methods/variables
        filtered_classes = []
        filtered_methods_by_class = {}
        filtered_class_variables = {}
        
        for cls in module_info.classes:
            # Check if class name matches
            class_matches = filter_lower in cls.name.lower()
            
            # Filter methods for this class
            methods = module_info.methods_by_class.get(cls.name, [])
            matching_methods = [
                m for m in methods
                if filter_lower in m.name.lower()
            ]
            
            # Filter class variables
            class_vars = module_info.class_variables.get(cls.name, [])
            matching_vars = [
                v for v in class_vars
                if filter_lower in v.name.lower()
            ]
            
            # Include class if it matches or has matching methods/variables
            if class_matches or matching_methods or matching_vars:
                filtered_classes.append(cls)
                if matching_methods:
                    filtered_methods_by_class[cls.name] = matching_methods
                if matching_vars:
                    filtered_class_variables[cls.name] = matching_vars
        
        # Create filtered ModuleInfo
        filtered_module = ModuleInfo(
            imports=filtered_imports,
            functions=filtered_functions,
            classes=filtered_classes,
            methods_by_class=filtered_methods_by_class,
            class_variables=filtered_class_variables,
            module_constants=filtered_constants
        )
        
        return filtered_module
