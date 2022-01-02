import param
import pathlib

from panel.template import BootstrapTemplate
from panel.template.theme import DefaultTheme


class BootstrapAcfTheme(DefaultTheme):
    css = param.Filename(default=pathlib.Path(__file__).parent / 'bootstrap-acf.css')

    # This tells Panel to use this implementation
    _template = BootstrapTemplate