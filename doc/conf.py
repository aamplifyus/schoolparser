# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import date

import sphinx_bootstrap_theme

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, ".")))
sys.path.append(os.path.abspath(os.path.join(curdir, "..")))
sys.path.append(os.path.abspath(os.path.join(curdir, "../eztrack")))
sys.path.append(os.path.abspath(os.path.join(curdir, "sphinxext")))

# -- Project information -----------------------------------------------------
td = date.today()

project = "EZTrack"
copyright = "%s Adam Li and Patrick Myers. Last updated on %s" % (
    td.year,
    td.isoformat(),
)
author = "Adam Li and Patrick Myers"

# The full version, including alpha/beta/rc tags
version = "0.1"  # eztrack.__version__
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.autosummary",
    "sphinx_gallery.gen_gallery",
    "numpydoc",
]

# generate autosummary
autosumary_generate = True
autodoc_default_flags = ["members", "show-inheritance", "special-members"]
html_static_path = ["_static"]
html_domain_indices = ["py_modindex"]

numpydoc_show_class_members = True
numpydoc_class_members_toctree = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

pygments_style = "sphinx"

todo_include_todos = False

html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

html_theme_options = {
    "navbar_title": "EZTrack",
    "bootswatch_theme": "flatly",
    "navbar_sidebarrel": False,
    "navbar_pagenav": False,
    "bootstrap_version": "3",
    "navbar_links": [],
}

htmlhelp_basename = "eztrackdoc"

# -- Extension configuration -------------------------------------------------
latex_elements = {}

latex_documents = [
    (
        master_doc,
        "eztrack.tex",
        "EZTrack Documentation",
        "Adam Li and Patrick Myers",
        "manual",
    ),
]

man_pages = [(master_doc, "eztrack", "EZTrack Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "eztrack",
        "EZTrack Documentation",
        author,
        "eztrack",
        "One line description of project.",
        "Miscellaneous",
    ),
]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

epub_exclude_files = ["search.html"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "mne": ("https://mne.tools/stable/", None),
    "numpy": ("https://www.numpy.org/devdocs", None),
    "scipy": ("https://scipy.github.io/devdocs", None),
}

sphinx_gallery_conf = {
    "example_dirs": "../examples",
    "gallery_dirs": "auto_examples",
    "filename_pattern": "^((?!sgskip).)*$",
    "backreferences_dir": "generated",
    # 'binder': {
    #     # Required keys
    #     'org': 'Neurologic-solutions',
    #     'repo': 'eegio',
    #     'branch': 'format/bids',
    #     'binder_url': 'https://mybinder.org',
    #     'dependencies': [
    #         '..environment.yml'
    #     ],
    # }
}
