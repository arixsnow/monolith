# Copyright (c) 2025, Arka Mondal. All rights reserved.
# Use of this source code is governed by a BSD-style license that
# can be found in the LICENSE file.

import yaml
import sys
from pathlib import Path
from engine import Monolith

def parse_yaml(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)

        return content
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file '{filepath}': {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

    return None

def generate_site(configfname = 'content.yaml'):

    # find the yaml find and load it
    filepath = Path("content") / configfname
    context = parse_yaml(filepath)
    if not context:
        sys.exit(1)

    # determine the output path
    outpath = context.get("outpath", "output")

    output_dir = Path(outpath)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Could not create directory '{output_dir}': {e}")

    outfile = context.get("render", "render.html")

    # determine the template path
    template_dir = context.get("template_path", "templates")
    template_name = context.get("template", "base.html")

    # Render the template
    engine = Monolith(template_dir)
    rendered_html = engine.render(template_name, context)

    output_path = output_dir / outfile
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"Site generated successfully...\nFile saved at: {output_path}")
    except Exception as e:
        print(f"Site generation failed!\nError: Could not write to file '{output_path}': {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_site(sys.argv[1])
    else:
        generate_site()
