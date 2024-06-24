# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Tik Manager4'
copyright = '2023, Arda Kutlu'
author = 'Arda Kutlu'

release = '0.1'
version = '4.0.2'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_toolbox.collapse',
    'autoapi.extension',
]

autoapi_dirs = ['../../tik_manager4/']
autoapi_type = 'python'
autoapi_ignore = ['*setup*', '*shiboken*', '*PySide2*', '*PySide6*', '*PyQt5*', '*PyQt6*']
autoapi_file_patterns = ['*.py']
add_module_names = False
autoapi_member_order = 'groupwise'
autoapi_python_use_implicit_namespaces = True
# autoapi_own_page_level = "attribute"
autodoc_typehints = "signature"

autoapi_options = [ 'members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'imported-members', ]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 8,  # Set the desired TOC depth
}

# -- Options for EPUB output
epub_show_urls = 'footnote'
