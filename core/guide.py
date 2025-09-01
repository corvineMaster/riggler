import os
import sys

from functools import partial
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from riggler.core import shapes

from maya import cmds, mel, OpenMayaUI

from PySide6 import QtCore, QtGui, QtWidgets

from riggler.core import color


def createDisplayCurve(objs, degree=1, width=5):
    point_coords = [(0, 0, 0) for obj in objs]
    crv = cmds.curve(point=point_coords, degree=degree)
    for i, obj in enumerate(objs):
        cmds.cluster(f'{crv}.cv[{i}]', weightedNode=(obj, obj))
    crv_shp = cmds.listRelatives(crv, shapes=True)[0]
    cmds.setAttr(f'{crv_shp}.overrideEnabled', True)
    cmds.setAttr(f'{crv_shp}.overrideDisplayType', 2)
    cmds.setAttr(f'{crv_shp}.lineWidth', width)
    cmds.parent(crv, objs[0])
    cmds.makeIdentity(crv, translate=True, rotate=True, scale=True)
    cmds.connectAttr(f'{objs[0]}.worldInverseMatrix[0]', f'{crv}.offsetParentMatrix')
    
    return crv
from maya import cmds
from riggler.core import guide


class GuideElements:
    red_mat = 'riggler_red'
    orange_mat = 'riggler_orange'
    yellow_mat = 'riggler_yellow'
    green_mat = 'riggler_green'
    blue_mat = 'riggler_blue'
    pink_mat = 'riggler_purple'

    def __init__(self):
        self.createGuideMaterials()

    def createGuideMaterials(self):
        guide_materials = cmds.ls('riggler*', type='lambert')
        color_values = {
            self.red_mat:(1,0,0), 
            self.green_mat:(0,1,0), 
            self.blue_mat:(0,0,1), 
            self.orange_mat:(1,0.3,0), 
            self.yellow_mat:(1,1,0),
            self.pink_mat:(0.627,0,1)}
        for name, rgb in color_values.items():
            if name not in guide_materials:
                color.createMaterial(name, rgb)

    def createRootGuide(self, name, parent=None, show_axis=False):
        base = self._createRootGuideBase(name)
        if show_axis:
            self._addGuidePointers(base, root=True)
        if parent:
            cmds.parent(base, parent)
        return base

    def createGuide(self, name, parent=None, show_axis=False):
        base = self._createGuideBase(name)
        if show_axis:
            self._addGuidePointers(base)
        if parent:
            cmds.parent(base, parent)
        return base
    
    def createMiscGuide(self, name, parent=None, show_axis=False):
        base = self._createMiscGuideBase(name)
        if show_axis:
            self._addGuidePointers(base)
        if parent:
            cmds.parent(base, parent)
        return base

    def _createRootGuideBase(self, name):
        base = cmds.polyCube(name=f'{name}_root')[0]
        cmds.polyBevel3(base, fraction=0.2, segments=2, subdivideNgons=True, offsetAsFraction=True)
        cmds.polySoftEdge(base, angle=60)
        mel.eval('DeleteHistory;')
        cmds.addAttr(base, shortName='irg', longName='isRigglerGuide', attributeType='bool', defaultValue=True)
        color.applyMaterial(base, self.orange_mat)
        return base

    def _createGuideBase(self, name):
        base = cmds.polySphere(name=f'{name}_guide', constructionHistory=False)[0]
        cmds.setAttr(f'{base}.scale', 0.5, 0.5, 0.5)
        cmds.makeIdentity(base, apply=True, scale=True)
        cmds.addAttr(base, shortName='irg', longName='isRigglerGuide', attributeType='bool', defaultValue=True)
        color.applyMaterial(base, self.yellow_mat)
        return base
    
    def _createMiscGuideBase(self, name):
        base = cmds.polySphere(name=f'{name}_misc', subdivisionsAxis=4, subdivisionsHeight=3, constructionHistory=False)[0]
        cmds.polyBevel3(base, fraction=0.2, segments=2, subdivideNgons=True, offsetAsFraction=True)
        cmds.polySoftEdge(base, angle=60)
        mel.eval('DeleteHistory;')
        cmds.setAttr(f'{base}.scale', 0.6, 0.6, 0.6)
        cmds.makeIdentity(base, apply=True, scale=True)
        cmds.addAttr(base, shortName='irg', longName='isRigglerGuide', attributeType='bool', defaultValue=True)
        color.applyMaterial(base, self.pink_mat)
        return base
    
    def _addGuidePointers(self, base, root=False):
        pointer_info = ((self.red_mat, 'X', 'Z', -90), (self.green_mat, 'Y', 'Y', 0), (self.blue_mat, 'Z', 'X', 90))
        for info in pointer_info:
            pointer = cmds.polyCone(name=f'pointer{info[1]}', constructionHistory=False)[0]
            color.applyMaterial(pointer, info[0])
            cmds.setAttr(f'{pointer}.translate{info[1]}', 0.8)
            cmds.setAttr(f'{pointer}.rotate{info[2]}', info[3])
            if root:
                cmds.setAttr(f'{pointer}.scale', 0.3, 0.375, 0.3)
            else:
                cmds.setAttr(f'{pointer}.scale', 0.2, 0.375, 0.2)
            cmds.makeIdentity(pointer, apply=True, translate=True, rotate=True, scale=True)
            pointer_shape = cmds.listRelatives(pointer, shapes=True)[0]
            cmds.parent(f'{pointer}|{pointer_shape}', base, relative=True, shape=True)
            cmds.delete(pointer)


def convertSettingsToAttributes(settings):
    pass


class widget_getter:
    def __init__(self):
        self.current_layout = object

    def getWidgets(self, settings):
        options = settings['options']
        for option in options:
            self.getWidgetParameters(option)

    def getWidgetParameters(self, option):
        widget_layout = QtWidgets.QVBoxLayout()
        self.self.current_layout = QtWidgets.QHBoxLayout()
        widget_type = option['widget']

        if widget_type == 'label':  # Just text, doesn't represent a kwarg
            self.createLabelWidget(option)
        elif widget_type == 'spinBox':
            self.createSpinBoxWidget(option)
        elif widget_type == 'slider':
            self.createSliderWidget(option)
        elif widget_type == 'spinSlider':  # Custom widget, combination of spinBox and slider
            self.createSpinSliderWidget(option)
        elif widget_type == 'checkBox':
            self.createCheckBoxWidget(option)
        elif widget_type == 'comboBox':
            self.createComboboxWidget(option)
        elif widget_type == 'inputSingle':
            self.createInputSingleWidget(option)
        elif widget_type == 'inputList':
            self.createInputListWidget(option)

        widget_layout.addLayout(self.current_layout)
    
    def createLabelWidget(self, option):
        QtWidgets.QLabel(option['label'], parent=self.current_layout)

    def createSpinBoxWidget(self, option):
        QtWidgets.QLabel(option['label'], parent=self.current_layout)
        widget = QtWidgets.QSpinBox(parent=self.current_layout)
        min_max = option['min_max']
        if min_max[0]:
            widget.setMinimum(min_max[0])
        if min_max[1]:
            widget.setMaximum(min_max[1])
        widget.setValue(option['default'])

    def createSliderWidget(self, option):
        QtWidgets.QLabel(option['label'], parent=self.current_layout)
        widget = QtWidgets.QSlider(parent=self.current_layout)
        min_max = option['min_max']
        if min_max[0]:
            widget.setMinimum(min_max[0])
        if min_max[1]:
            widget.setMaximum(min_max[1])
        widget.setValue(option['default'])

    def createSpinSliderWidget(self, option):
        pass

    def createCheckBoxWidget(self, option):
        QtWidgets.QLabel(option['label'], parent=self.current_layout)
        widget = QtWidgets.QCheckBox(parent=self.current_layout)
        widget.setChecked(option['default'])

    def createComboBoxWidget(self, option):
        widget = QtWidgets.QComboBox(option['label'], parent=self.current_layout)
        items = option['items']
        widget.addItems(items)
        default = option['default']
        if default:
            widget.setCurrentText(default)

    def createInputSingleWidget(self, option):
        # Press button to input single selection into textField
        widget = QtWidgets.QTextField(parent=self.current_layout)
        input_button = QtWidgets.QPushButton('<<', parent=self.current_layout)
        input_button.clicked.connect(partial(self.addSelectionToField, widget))

    def createInputListWidget(self, option):
        widget = QtWidgets.QListWidget(parent=self.current_layout)
        widget.setDragDropOverwriteMode(True)
        widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        widget.setDefaultDropAction(QtCore.Qt.MoveAction)
        widget.setAlternatingRowColors(True)
        widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        widget.setSelectionRectVisible(False)
        button_layout = QtWidgets.QVBoxLayout(self.current_layout)
        input_button = QtWidgets.QPushButton('<<', parent=button_layout)
        input_button.clicked.connect(partial(self.addSelectionToField, widget))
        remove_button = QtWidgets.QPushButton('>>', parent=button_layout)
        remove_button.clicked.connect(partial(self.removeSelectionFromList, widget))
        return self.current_layout


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


def test_createGuides():
    try:
        cmds.delete('root')
    except:
        pass
    cls = GuideElements()
    previous_guide = cls.createRootGuide()
    guides = [previous_guide]
    for i in range(10):
        guide = cls.createGuide()
        guide = cmds.rename(guide, guide + f'_{i}')
        cmds.parent(guide, previous_guide)
        cmds.setAttr(f'{guide}.tx', 2)
        guides.append(guide)
        previous_guide = guide
    cmds.setAttr(f'{guides[0]}.ty', 10)
    crv = createDisplayCurve(guides)
    cmds.select(clear=True)

WIDGET_ATTRIBUTE_DICT = {
    'spinBox': 'float',
    'slider': 'float',
    'spinSlider': 'float',
    'checkBox': 'bool',
    'comboBox': 'enum',
    'inputSingle': 'string',
    'inputList': 'string'
}

def test_createGuideAttributes(options, node):
    for option in options:
        widget = option['widget']
        arg = option['arg']
        default = option['default']
        
        widget_attr = WIDGET_ATTRIBUTE_DICT[widget]
        if widget_attr == 'float':
            attr = cmds.addAttr(node, longName=arg, defaultValue=default, attributeType='float')
            minimum, maximum = option['min_max']
            if minimum:
                cmds.addAttr(f'{node}.{arg}', edit=True, minValue=minimum)
            if maximum:
                cmds.addAttr(f'{node}.{arg}', edit=True, maxValue=maximum)
                
        elif widget_attr == 'bool':
            cmds.addAttr(node, longName=arg, defaultValue=default, attributeType='bool')
            
        elif widget_attr == 'enum':
            items = option['items']
            default = default if type(default) == int else items.index(default)
            cmds.addAttr(node, longName=arg, enumName=':'.join(items), defaultValue=default, attributeType='enum')
            
        elif widget_attr == 'string':
            cmds.addAttr(node, longName=arg, defaultValue=default, dataType='string')

if __name__ == '__main__':
    settings = {
        'sections': 1,
        "fk_ik": ["FK", "IK", "FK/IK"]
    }
    convertSettingsToAttributes(options)
