# -*- coding: utf-8 -*-
"""
This package contains python specific modes, panels and editor.
"""
import re
import sys
import weakref
from PyQt4 import QtCore, QtGui

from pyqode.core.code_edit import QCodeEdit
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core import style as core_style

from pyqode.python import style
from pyqode.python.modes import PyAutoCompleteMode
from pyqode.python.modes import CalltipsMode
from pyqode.python.modes import CommentsMode
from pyqode.python.modes import PEP8CheckerMode
from pyqode.python.modes import PyAutoIndentMode
from pyqode.python.modes import FrostedCheckerMode
from pyqode.python.modes import PyHighlighterMode
from pyqode.python.modes import PyIndenterMode
from pyqode.python.modes import DEFAULT_DARK_STYLES
from pyqode.python.modes import DEFAULT_LIGHT_STYLES
from pyqode.python.modes import GoToAssignmentsMode
from pyqode.python.modes import DocumentAnalyserMode
from pyqode.python.panels import SymbolBrowserPanel
from pyqode.python.panels import QuickDocPanel

import pyqode.python.ui.pyqode_python_icons_rc


class QPythonCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels specifics to
    a python code editor widget.

    **Panels:**
        * :class:`pyqode.core.FoldingPanel`
        * :class:`pyqode.core.LineNumberPanel`
        * :class:`pyqode.core.MarkerPanel`
        * :class:`pyqode.core.SearchAndReplacePanel`

    **Modes:**
        * :class:`pyqode.core.CaretLineHighlighterMode`
        * :class:`pyqode.core.RightMarginMode`
        * :class:`pyqode.core.CodeCompletionMode`
        * :class:`pyqode.core.ZoomMode`
        * :class:`pyqode.core.SymbolMatcherMode`
        * :class:`pyqode.python.PyAutoCompleteMode`
        * :class:`pyqode.python.PyHighlighterMode`
        * :class:`pyqode.python.PyAutoIndentMode`
        * :class:`pyqode.python.PyFlakesCheckerMode`
        * :class:`pyqode.python.PEP8CheckerMode`
        * :class:`pyqode.python.CalltipsMode`
        * :class:`pyqode.python.PyIndenterMode`

    It also implements utility methods to switch from a white style to a dark
    style and inversely.

    .. note:: This code editor widget use PEP 0263 to detect file encoding.
              If the opened file does not respects the PEP 0263,
              :py:func:`sys.getfilesystemencoding` is used as the default
              encoding.
    """
    DARK_STYLE = 0
    LIGHT_STYLE = 1

    def __init__(self, parent=None):
        super(QPythonCodeEdit, self).__init__(parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("pyQode - Python Editor")

        # install those modes first as they are required by other modes/panels
        api.install_mode(self, DocumentAnalyserMode())

        # panels
        api.install_panel(self, panels.LineNumberPanel())
        api.install_panel(self, panels.MarkerPanel())
        api.install_panel(self, panels.SearchAndReplacePanel(),
                          panels.SearchAndReplacePanel.Position.BOTTOM)
        api.install_panel(self, SymbolBrowserPanel(),
                          SymbolBrowserPanel.Position.TOP)

        # modes
        # generic
        api.install_mode(self, modes.CaretLineHighlighterMode())
        api.install_mode(self, modes.FileWatcherMode())
        api.install_mode(self, modes.RightMarginMode())
        api.install_mode(self, modes.ZoomMode())
        api.install_mode(self, modes.SymbolMatcherMode())
        api.install_mode(self, modes.WordClickMode())
        api.install_mode(self, modes.CodeCompletionMode())
        # python specifics
        api.install_mode(self, PyHighlighterMode(self.document()))
        api.install_mode(self, PyAutoCompleteMode())
        api.install_mode(self, PyAutoIndentMode())
        api.install_mode(self, FrostedCheckerMode())
        api.install_mode(self, PEP8CheckerMode())
        api.install_mode(self, CalltipsMode())
        api.install_mode(self, PyIndenterMode())
        api.install_mode(self, GoToAssignmentsMode())
        api.install_panel(self, QuickDocPanel(), api.Panel.Position.BOTTOM)
        api.install_mode(self, CommentsMode())

    @QtCore.pyqtSlot()
    def use_dark_style(self, use=True):
        """
        Changes the editor style to a dark color scheme similar to pycharm's
        darcula color scheme.
        """
        if not use:
            return
        set_dark_color_scheme(self)

    @QtCore.pyqtSlot()
    def use_white_style(self, use=True):
        """
        Changes the editor style to a dark color scheme similar to QtCreator's
        default color scheme.
        """
        if not use:
            return
        set_white_color_scheme(self)

    def detect_encoding(self, data):
        """
        Detects encoding based on PEP 0263
        """
        encoding = self.default_encoding()
        if sys.version_info[0] == 3:
            data = str(data.decode("utf-8"))
        for l in data.splitlines():
            regexp = re.compile(r"#.*coding[:=]\s*([-\w.]+)")
            match = regexp.match(l)
            if match:
                encoding = match.groups()[0]
        return encoding


def set_dark_color_scheme(code_edit):
    """
    Set a dark scheme on a :class:`pyqode.core.QCodeEdit`.

    The color scheme is similar to pycharm's darcula color scheme.

    .. note:: This function will work only if a
        :class:`pyqode.python.PyHighlighterMode` has been installed on the
        QCodeEdit instance

    :param code_edit: QCodeEdit instance
    :type code_edit: pyqode.core.QCodeEdit
    """
    for k, v in DEFAULT_DARK_STYLES.items():
        style.__dict__['py_' + k] = v
    core_style.background = QtGui.QColor("#252525")
    core_style.foreground = QtGui.QColor("#A9B7C6")
    core_style.caretLineBackground = QtGui.QColor("#2d2d2d")
    core_style.whiteSpaceForeground = QtGui.QColor('#404040')
    core_style.matchedBraceBackground = None
    core_style.matchedBraceForeground = QtGui.QColor("#FF8647")
    code_edit.refresh_style()


def set_white_color_scheme(code_edit):
    """
    Set a light scheme on a :class:`pyqode.core.QCodeEdit`.

    The color scheme is similar to the qt creator's default color scheme.

    .. note:: This function will work only if a
        :class:`pyqode.python.PyHighlighterMode` has been installed on the
        codeEdit instance

    :param code_edit: QCodeEdit instance
    :type code_edit: pyqode.core.QCodeEdit
    """
    for k, v in DEFAULT_LIGHT_STYLES.items():
        style.__dict__['py_' + k] = v
    core_style.background = QtGui.QColor("#FFFFFF")
    core_style.foreground = QtGui.QColor("#000000")
    core_style.caretLineBackground = QtGui.QColor("#E4EDF8")
    core_style.whiteSpaceForeground = QtGui.QColor("#dddddd")
    core_style.matchedBraceBackground = QtGui.QColor("#B4EEB4")
    core_style.matchedBraceForeground = QtGui.QColor("#FF0000")
    code_edit.refresh_style()
