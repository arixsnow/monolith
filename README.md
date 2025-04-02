# Monolith - A Minimalistic Static Site Generator

## Overview
**Monolith** is a lightweight static site generator that compiles YAML-based content into a structured HTML website using a flexible template engine. It enables users to create dynamic templates with conditional rendering, loops, and variable substitution.

## Features
- **Template Rendering**: Supports variable substitution, conditionals, loops, and includes.
- **YAML-Based Content Management**: Provides a structured way to define site content.
- **Customizable Templates**: Allows users to create their own HTML templates with embedded logic.

## Installation
Ensure you have Python installed (>=3). Clone the repository and install the dependencies:

```sh
$ git clone https://github.com/yourusername/monolith.git
$ cd monolith
$ pip install -r requirements.txt
```

## Usage
### Generating a Site
To generate a site using the default configuration file (`content/content.yaml`):

```sh
$ python generate.py
```

To specify a different YAML configuration file:

```sh
$ python generate.py custom_content.yaml
```

### YAML Configuration Example
A basic example of `content.yaml`:

```yaml
outpath: "output"
template_path: "templates"
template: "index.html"
render: "index.html"
title: "My Static Site"
sections:
  - name: "Home"
    content: "Welcome to my site!"
  - name: "About"
    content: "This is a static site generator."
```

### Template Example
A simple template (`index.html`) with variable substitution:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    {%1 for section in sections %}
        <h2>{{ section.name }}</h2>
        <p>{{ section.content }}</p>
    {%1 endfor %}
</body>
</html>
```

## Template Syntax
### Variable Replacement
Use `{{ variable_name }}` to insert values from the context.

```html
<p>Hello, {{ user.name }}!</p>
```

If a variable is missing, you can provide a default value:

```html
<p>Hello, {{ user.name | default:'Guest' }}!</p>
```

### Loops
Use `{%1 for item in list %} ... {%1 endfor %}` to iterate over a list.

```html
<ul>
    {%1 for user in users %}
        <li>{{ user.name }} - {{ user.age }} years old</li>
    {%1 endfor %}
</ul>
```

### Nested Loops
You can nest loops to iterate over sublists.

```html
<ul>
    {%1 for category in categories %}
        <li>{{ category.name }}
            <ul>
                {%2 for item in category.items %}
                    <li>{{ item }}</li>
                {%2 endfor %}
            </ul>
        </li>
    {%1 endfor %}
</ul>
```

### Conditionals
Use `{%1 if condition %} ... {%1 endif %}` for conditional rendering.

```html
{%1 if user.age >= 18 %}
    <p>Welcome, {{ user.name }}!</p>
{%1 else %}
    <p>Sorry, you must be at least 18 years old.</p>
{%1 endif %}
```

## File Structure
```
monolith/
│── engine.py          # Template engine
│── generate.py        # Site generator script
│── templates/         # Directory for HTML templates
│── content/           # Directory for YAML content files
│── output/            # Generated static site
│── README.md          # Documentation
│── LICENSE            # License file
```

## License
This project is licensed under the BSD-style license. See the `LICENSE` file for details.

## Author
Developed by **Arka Mondal**.
