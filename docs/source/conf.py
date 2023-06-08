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
    "sphinx_autopackagesummary",
    "sphinx.ext.autodoc",  # Core Sphinx library for auto html doc generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables for modules/classes/methods etc
    "sphinx.ext.intersphinx",  # Link to other project's documentation (see mapping below)
    "sphinx.ext.viewcode",  # Add a link to the Python source code for classes, functions etc.
    "sphinx_autodoc_typehints",  # Automatically document param types (less noise in class signature)
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
]

templates_path = ["_templates"]
exclude_patterns = ["robot/__main__.py", "calibrate_cam"]
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
    "spidev",
    "vl53l0x_python",
    "qwiic_scmd",
    "serial",
    "robot.commands.tof.VL53L0X",
    "TCPManagerTests",
]
autosummary_mock_imports = [
    "RPi",
    "cv2",
    "PIL",
    "picamera",
    "adafruit_vl53l0x",
    "numpy",
    "smbus",
    "pyttsx3",
    "pyrealsense2",
    "spidev",
    "vl53l0x_python",
    "qwiic_scmd",
    "serial",
    "robot.commands.tof.VL53L0X",
    "TCPManagerTests",
]

nitpicky = True  # If true, Sphinx will warn about all references where the target cannot be found. Default is False. You can activate this mode temporarily using the -n command-line switch.


autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = (
    False  # Remove 'view source code' from top of page (for html, not python)
)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class

# autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False  # Remove namespaces from class/method signatures


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "groundwork"
html_static_path = ["_static"]

html_theme_options = {}
