import os
import sys

from functools import partial
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from riggler.core import shapes, custom_widgets, guide

from maya import cmds, OpenMayaUI

from PySide2 import QtCore, QtGui, QtWidgets


DESCRIPTION = "PISTON"

def add_loc(name, parent, position=None):
    loc = icon.guideLocatorIcon(parent, self.getName(name), color=17, m=position)


class Guide(guide.GuideElements):
    def __init__(self):
        pass

    def addObjects(self):
        self.root = self.addRoot()
        self.locs = [self.root]
        for loc in self.settings['loc_num']:
            self.locs.append(self.addLoc(self.root))
        shapes.add_display_curve('crv', self.locs, 1, self.root)

    def addParameters(self):
        # Get the appropriate sub-setting and fill out the guide drop down menu
        # Should also add attributes to the root guide object for future reference
        # Organize by separating widgets into specified groupBoxes
        widget_layout = QtWidgets.QVBoxLayout()
        for settings in self.settings:
            current_layout = QtWidgets.QHBoxLayout()

            widget_type = settings['widget']
            if widget_type == 'label':  # Just text, doesn't represent a kwarg
                widget = QtWidgets.QLabel(settings['label'], parent=current_layout)
            if widget_type == 'spinBox':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QSpinBox(parent=current_layout)
                min_max = settings['min_max']
                if min_max[0]:
                    widget.setMinimum(min_max[0])
                if min_max[1]:
                    widget.setMaximum(min_max[1])
                widget.setValue(settings['default'])
            elif widget_type == 'slider':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QSlider(parent=current_layout)
                min_max = settings['min_max']
                if min_max[0]:
                    widget.setMinimum(min_max[0])
                if min_max[1]:
                    widget.setMaximum(min_max[1])
                widget.setValue(settings['default'])
            elif widget_type == 'spinSlider':  # Custom widget, combination of spinBox and slider
                pass
            elif widget_type == 'comboBox':
                QtWidgets.QLabel(settings['label'], parent=current_layout)
                widget = QtWidgets.QCheckBox(parent=current_layout)
                widget.setChecked(settings['default'])
            elif widget_type == 'checkBox':
                widget = QtWidgets.QComboBox(settings['label'], parent=current_layout)
                items = settings['items']
                widget.addItems(items)
                default = settings['default']
                if default:
                    widget.setCurrentText(default)
            elif widget_type == 'input_single':  # Press button to input single selection into textField
                widget = QtWidgets.QTextField(parent=current_layout)
                input_button = QtWidgets.QPushButton('<<', parent=current_layout)
                input_button.clicked.connect(partial(self.addSelectionToField, widget))
            elif widget_type == 'input_list':  # Press button to input multi selection into listWidget
                widget = QtWidgets.QListWidget(parent=current_layout)
                widget.setDragDropOverwriteMode(True)
                widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                widget.setDefaultDropAction(QtCore.Qt.MoveAction)
                widget.setAlternatingRowColors(True)
                widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
                widget.setSelectionRectVisible(False)
                button_layout = QtWidgets.QVBoxLayout(current_layout)
                input_button = QtWidgets.QPushButton('<<', parent=button_layout)
                input_button.clicked.connect(partial(self.addSelectionToField, widget))
                remove_button = QtWidgets.QPushButton('>>', parent=button_layout)
                remove_button.clicked.connect(partial(self.removeSelectionFromList, widget))
            
            widget_layout.addLayout(current_layout)

    def addSelectionToField(self, field: object):
        selections = cmds.ls(selection=True)
        if isinstance(field, QtWidgets.QTextField):
            field.setText(selections[0])
        else:
            existing_items = [field.item(x).text() for x in range(field.count())]
            for selection in selections:
                if selection not in existing_items:
                    field.addItem(selection)
    
    def removeSelectionFromList(self, field):
        selected_items = field.selectedItems()
        for item in selected_items:
            row = field.row(item)
            field.takeItem(row)
