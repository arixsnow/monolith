# Copyright (c) 2025, Arka Mondal. All rights reserved.
# Use of this source code is governed by a BSD-style license that
# can be found in the LICENSE file.

import re
from pathlib import Path

class Monolith:
    def __init__(self, template_dir="."):
        self.template_dir = Path(template_dir)

    def render(self, template_name, context):
        template_path = self.template_dir / template_name
        with open(template_path, "r") as f:
            template = f.read()

        # template = self._process_includes(template)

        template = self._process_conditionals(template, context)

        template = self._process_loops(template, context)

        template = self._replace_variables(template, context)

        return template

    def _replace_variables(self, template, context):
        """Replace {{ variable }} with values from context, supporting dot notation, list indices, and default values."""

        def resolve_value(var_name, context):
            """Retrieve value from context using dot notation and list indices."""
            parts = var_name.split('|')  # Split variable and filter ("education.2.institute | default:'N/A'")
            variable_path = parts[0].strip()
            default_value = None

            # Extract default value if provided
            if len(parts) > 1 and "default:" in parts[1]:
                default_value = parts[1].split("default:")[1].strip().strip('"').strip("'")

            keys = variable_path.split('.')  # ['education', '0', '2', 'institute']
            value = context

            try:
                for key in keys:
                    if isinstance(value, list) and key.isdigit():
                        index = int(key)
                        value = value[index]
                    elif isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        raise KeyError
            except (KeyError, IndexError, TypeError):
                return default_value if default_value is not None else ""

            return str(value)

        def replace_match(match):
            var_name = match.group(1).strip()
            return resolve_value(var_name, context)

        return re.sub(r'\{\{\s*(.*?)\s*\}\}', replace_match, template)

    def _resolve_value(self, var_name, ctx):
        """Universal resolver with default handling and nested access"""

        parts = var_name.split('|')
        var_path = parts[0].strip().split('.')
        default = None


        if len(parts) > 1 and 'default:' in parts[1]:
            default = parts[1].split('default:')[1].strip().strip('"').strip("'")

        current = ctx
        try:
            for part in var_path:
                part = part.strip()
                if isinstance(current, list) and part.isdigit():
                    current = current[int(part)]
                elif isinstance(current, dict):
                    current = current[part]
                else:
                    raise KeyError(f"Can't resolve {part} in {var_name}")
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return default if default is not None else None

    def _compare_values(self, var_value, operator, comparison_value):
        try:
            num_var = float(var_value)
            num_comp = float(comparison_value)
            return {
                '==': num_var == num_comp,
                '!=': num_var != num_comp,
                '>=': num_var >= num_comp,
                '<=': num_var <= num_comp,
                '>': num_var > num_comp,
                '<': num_var < num_comp
            }.get(operator, False)
        except (ValueError, TypeError):
            str_var = str(var_value).lower()
            str_comp = str(comparison_value).strip('"\'').lower()
            return {
                '==': str_var == str_comp,
                '!=': str_var != str_comp
            }.get(operator, False)

    def _process_conditionals(self, template, context, depth=1):
        """Handle {%1 if condition %}...{%1 endif %} blocks with nested resolution."""

        def eval_condition(condition, ctx):
            """Evaluate complex conditions with comparison operators"""

            if condition.lower() in ['true', 'false']:
                return condition.lower() == 'true'


            operators = ['==', '!=', '>=', '<=', '>', '<']
            for op in operators:
                if op not in condition:
                    continue

                # if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._resolve_value(left.strip(), ctx)
                right_val = self._resolve_value(right.strip(), ctx)
                return self._compare_values(left_val, op, right_val)

            return bool(self._resolve_value(condition, ctx))

        pattern = re.compile(
            r'\{%(\d+)\s+if\s+(.*?)\s*%\}(.*?)\{%\1\s+endif\s*%\}',
            re.DOTALL
        )

        # Process from innermost to outermost
        while True:
            matches = list(pattern.finditer(template))
            if not matches:
                break

            for match in reversed(matches):
                full_block = match.group(0)
                k, condition, block = match.groups()

                processed_block = self._process_conditionals(block, context, depth + 1)

                if eval_condition(condition, context):
                    template = template.replace(full_block, processed_block, 1)
                else:
                    template = template.replace(full_block, '', 1)

        return template

    def _process_loops(self, template, context, depth=1):
        pattern = re.compile(
            r'\{%(\d+)\s+for\s+(\w+)\s+in\s+([\w|\.]+)\s*%\}(.*?)\{%\1\s+endfor\s*%\}',
            re.DOTALL
        )

        # Process all loops in the template
        while True:
            match = pattern.search(template)
            if not match:
                break

            k, item_var, list_var, block = match.groups()

            items = self._resolve_value(list_var, context)

            if items == None:
                items = []

            if not isinstance(items, list):
                items = [items]  # Handle single item contexts

            loop_content = []
            for item in items:
                # new_context = dict(context)
                new_context = dict()
                new_context[item_var] = item

                processed_block = self._process_loops(block, new_context, depth + 1)

                loop_content.append(
                    self._replace_variables(processed_block, new_context)
                )

            sub_pattern = re.compile(
                r'\{%' + re.escape(k) + r'\s+for\s+' + re.escape(item_var) +
                r'\s+in\s+' + re.escape(list_var) + r'\s*%\}(.*?)\{%' +
                re.escape(k) + r'\s+endfor\s*%\}',
                re.DOTALL
            )

            template = sub_pattern.sub(''.join(loop_content), template, count=1)

        return template


    def _process_includes(self, template):
        """Handle {% include "navbar.html" %}"""
        pattern = r'\{%\s*include\s*"(.*?)"\s*%\}'
        matches = re.findall(pattern, template)

        for partial_name in matches:
            partial_path = self.template_dir / partial_name
            if partial_path.exists():
                with open(partial_path, "r") as f:
                    partial_content = f.read()

                template = template.replace(f'{{% include "{partial_name}" %}}', partial_content)

        return template
