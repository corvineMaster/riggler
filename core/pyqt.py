"""pyQt/pySide widgets and helper functions. Taken from mgear/core/pyqt.py"""

#############################################
# GLOBAL
#############################################
import os
import maya.OpenMayaUI as omui
import maya.cmds as cmds


UI_EXT = "ui"

#################
# Old qt importer
#################


def _qt_import(binding, shi=False, cui=False):
    QtGui = None
    QtCore = None
    QtWidgets = None
    wrapInstance = None

    if binding == "PySide6":
        from PySide6 import QtGui, QtCore, QtWidgets, QtSvg
        import shiboken6 as shiboken
        from shiboken6 import wrapInstance

    elif binding == "PySide2":
        from PySide2 import QtGui, QtCore, QtWidgets, QtSvg
        import shiboken2 as shiboken
        from shiboken2 import wrapInstance

    elif binding == "PySide":
        from PySide import QtGui, QtCore
        import PySide.QtGui as QtWidgets
        import shiboken
        from shiboken import wrapInstance
        from pysideuic import compileUi

    elif binding == "PyQt4":
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        import PyQt4.QtGui as QtWidgets
        from sip import wrapinstance as wrapInstance
        from PyQt4.uic import compileUi

        print("Warning: 'shiboken' is not supported in 'PyQt4' Qt binding")
        shiboken = None

    else:
        raise Exception("Unsupported python Qt binding '%s'" % binding)

    rv = [QtGui, QtCore, QtWidgets, wrapInstance]
    if shi:
        rv.append(shiboken)
    if cui:
        rv.append(compileUi)
    return rv


def qt_import(shi=False, cui=False):
    """
    import pyside/pyQt

    Returns:
        multi: QtGui, QtCore, QtWidgets, wrapInstance

    """
    lookup = ["PySide6", "PySide2", "PySide", "PyQt4"]

    for binding in lookup:
        try:
            return _qt_import(binding, shi, cui)
        except Exception:
            pass

    raise _qt_import("ThisBindingSurelyDoesNotExist", False, False)


#############################################
# helper Maya pyQt functions
#############################################


def maya_main_window():
    """Get Maya's main window

    Returns:
        QMainWindow: main window.

    """

    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return shiboken.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def showDialog(dialog, delete_instance=True, dockable=False, *_):
    """
    Show the defined dialog window

    Attributes:
        dialog (QDialog): The window to show.

    """
    if delete_instance:
        try:
            for c in maya_main_window().children():
                if isinstance(c, dialog):
                    c.deleteLater()
        except Exception:
            pass

    # Create minimal dialog object

    windw = dialog()

    # ensure clean workspace name
    if hasattr(windw, "toolName") and dockable:
        control = windw.toolName + "WorkspaceControl"
        if cmds.workspaceControl(control, query=True, exists=True):
            cmds.workspaceControl(control, edit=True, close=True)
            cmds.deleteUI(control, control=True)
    desktop = QtWidgets.QApplication.desktop()
    screen = desktop.screen()
    screen_center = screen.rect().center()
    windw_center = windw.rect().center()
    windw.move(screen_center - windw_center)

    # Delete the UI if errors occur to avoid causing winEvent
    # and event errors (in Maya 2014)
    if dockable:
        windw.show(dockable=True)
    else:
        windw.show()
    return windw


def deleteInstances(dialog, checkinstance):
    """Delete any instance of a given dialog

    Delete any instance of a given dialog and if the dialog is
    instance of checkinstance.

    Attributes:
        dialog (QDialog): The dialog to delete.
        checkinstance (QDialog): The instance to check the type of dialog.

    """
    mayaMainWindow = maya_main_window()
    for obj in mayaMainWindow.children():
        if isinstance(obj, checkinstance):
            if obj.widget().objectName() == dialog.toolName:
                print(("Deleting instance {0}".format(obj)))
                mayaMainWindow.removeDockWidget(obj)
                obj.setParent(None)
                obj.deleteLater()


def position_window(window):
    """set the position for the windonw

    Function borrowed from Cesar Saez QuickLauncher
    Args:
        window (QtWidget): the window to position
    """
    pos = QtGui.QCursor.pos()
    window.move(pos.x(), pos.y())


def get_main_window(widget=None):
    """Get the active window

    Function borrowed from Cesar Saez QuickLauncher
    Args:
        widget (QtWidget, optional): window

    Returns:
        QtWidget: parent of the window
    """
    widget = widget or QtWidgets.QApplication.activeWindow()
    if widget is None:
        return
    parent = widget.parent()
    if parent is None:
        return widget
    return get_main_window(parent)


def get_instance(parent, gui_class):
    """Get instace of a window from a given parent

    Function borrowed from Cesar Saez QuickLauncher
    Args:
        parent (QtWidget): parent
        gui_class (QtWidget): instance class to check

    """
    for children in parent.children():
        if isinstance(children, gui_class):
            return children
    return None


def get_top_level_widgets(class_name=None, object_name=None):
    """
    Get existing widgets for a given class name

    Args:
        class_name (str): Name of class to search top level widgets for
        object_name (str): Qt object name

    Returns:
        List of QWidgets
    """
    matches = []

    # Find top level widgets matching class name
    for widget in QtWidgets.QApplication.topLevelWidgets():
        try:
            # Matching class
            if class_name and widget.metaObject().className() == class_name:
                matches.append(widget)
            # Matching object name
            elif object_name and widget.objectName() == object_name:
                matches.append(widget)
        except AttributeError:
            continue
        # Print unhandled to the shell
        except Exception as e:
            print(e)

    return matches


def clear_layout(layout):
    """Removes all the widgets added in the given layout.

    Args:
         layout (QtWidgets.QLayout): Qt layout to clear.
    """

    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clear_layout(child.layout())


def get_icon_path(icon_name=None):
    """Gets the directory path to the icon"""

    file_dir = os.path.dirname(__file__)

    if "\\" in file_dir:
        file_dir = file_dir.replace("\\", "/")
    file_dir = "/".join(file_dir.split("/")[:-3])
    if icon_name:
        return "{0}/icons/{1}".format(file_dir, icon_name)
    else:
        return "{}/icons".format(file_dir)


def get_icon(icon, size=24):
    """get svg icon from icon resources folder as a pixel map"""
    img = get_icon_path("{}.svg".format(icon))
    svg_renderer = QtSvg.QSvgRenderer(img)
    image = QtGui.QImage(size, size, QtGui.QImage.Format_ARGB32)
    # Set the ARGB to 0 to prevent rendering artifacts
    image.fill(0x00000000)
    svg_renderer.render(QtGui.QPainter(image))
    pixmap = QtGui.QPixmap.fromImage(image)

    return pixmap
