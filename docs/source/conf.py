# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "MarthaRobot"
copyright = "2023, CEI-Lab"
author = "CEI-Lab"

import os, sys

for x in os.walk("..\\..\\HSI"):
    # print(f"adding {x} to path")
    sys.path.insert(0, x[0])
sys.path.insert(0, os.path.abspath("..\\.."))  # Source code dir relative to this file
sys.path.insert(
    0, os.path.abspath("..\\..\\HSI")
)  # Source code dir relative to this file

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]
exclude_patterns = []
autodoc_mock_imports = [
    "RPi",
    "cv2",
    "PIL",
    "picamera",
    "adafruit_vl53l0x",
    "numpy",
    "smbus",
    "pyttsx3",
    "pyrealsense2",
    "vl53l0x_python",
    "tof",
    "spidev",
    "gpiozero",
    "qwiic_scmd",
    "serial",
]


autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = (
    False  # Remove 'view source code' from top of page (for html, not python)
)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
