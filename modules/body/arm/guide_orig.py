import os
import sys

from functools import partial
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from riggler.core import shapes, custom_widgets, guide, component, nodes

from maya import cmds, OpenMayaUI

from PySide6 import QtCore, QtGui, QtWidgets


DESCRIPTION = "Test control module"


class Guide(component.Component):
    def __init__(self, name, parent=None):
        super().__init__(name=name, parent=parent)
        self.name = ''
        self.guide_input = ''
        self.input = ''
        self.guide_output = ''
        self.output = ''
        self.guides = []
        self.internals = []
        self.controls = []
        self.internals = []
        self.deforms = []
        self.displays = []

    def add_objects(self):
        self.shoulder_guide = self.createRootGuide(self.name + '_shoulder_guide', self.org_grps["guides_grp"])
        self.elbow_guide = self.createGuide(self.name + '_elbow_guide', self.org_grps["guides_grp"])
        self.wrist_guide = self.createGuide(self.name + '_wrist_guide', self.org_grps["guides_grp"])
        cmds.setAttr(f'{self.wrist_guide}.translate', 10, 0, 0)
        self.pole_vector_guide = self.createMiscGuide(self.name + '_pole_vector_guide', self.org_grps["guides_grp"])
        cmds.setAttr(f'{self.pole_vector_guide}.translate', 5, 0, 5)

        self.shoulder_fk_ctl = shapes.create_ctrl(self.name + '_shoulder_fk_ctl', self.org_grps["controls_grp"])
        self.elbow_fk_ctl = shapes.create_ctrl(self.name + '_elbow_fk_ctl', self.org_grps["controls_grp"])
        self.elbow_ik_ctl = shapes.create_ctrl(self.name + '_elbow_ik_ctl', self.org_grps["controls_grp"])
        self.wrist_fk_ctl = shapes.create_ctrl(self.name + '_wrist_fk_ctl', self.org_grps["controls_grp"])
        self.wrist_ik_ctl = shapes.create_ctrl(self.name + '_wrist_ik_ctl', self.org_grps["controls_grp"])
        self.pole_vector_ctl = shapes.create_ctrl(self.name + '_pole_vector_ctl', self.org_grps["controls_grp"])

        self.shoulder_ik_jnt = shapes.create_joint(f'{self.name}_shoulder_IK_jnt', self.org_grps["internals_grp"], (0, 0, 0))
        self.elbow_ik_jnt = shapes.create_joint(f'{self.name}_elbow_IK_jnt', self.shoulder_ik_jnt, (1, 0, 0))
        self.wrist_ik_jnt = shapes.create_joint(f'{self.name}_wrist_IK_jnt', self.elbow_ik_jnt, (2, 0, 0))

    def add_attributes(self):
        pass

    def add_operators(self):
        cmds.connectAttr(f'{self.pole_vector_guide}.worldMatrix[0]', f'{self.pole_vector_ctl}.offsetParentMatrix')

        elbow_orientPlane_guide = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            primary_input_axis=(1, 0, 0),
            primary_mode=1,
            primary_target_vector=(0, 0, 0),
            secondary_target_matrix=f'{self.pole_vector_guide}.worldMatrix[0]',
            secondary_input_axis=(0, 1, 0),
            secondary_mode=1,
            secondary_target_vector=(0, 0, 0),
            name=f'{self.name}_elbow_orientPlane_guide'
        )
        elbow_guide_WM = nodes.create_blendMatrix_node(
            input=f'{elbow_orientPlane_guide}.outputMatrix',
            target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            weight=0.5,
            scale_weight=0,
            translate_weight=1,
            rotate_weight=0,
            shear_weight=[0],
            targets=f'{self.elbow_guide}.offsetParentMatrix',
            name=f'{self.name}_elbow_guide_WM'
        )
        elbow_guide_outWM = nodes.create_aimMatrix_node(
            input_matrix=f'{self.elbow_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            primary_input_axis=(1, 0, 0),
            primary_mode=1,
            primary_target_vector=(0, 0, 0),
            secondary_target_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            secondary_input_axis=(0, -1, 0),
            secondary_mode=1,
            secondary_target_vector=(0, 0, 0),
            name=f'{self.name}_elbow_guide_outWM'
        )
        elbow_guide_outWIM = nodes.create_inverseMatrix_node(
            f'{elbow_guide_outWM}.outputMatrix',
            name=f'{self.name}_elbow_guide_outWIM'
        )
        wrist_fk_guide_outWM = nodes.create_blendMatrix_node(
            input=f'{elbow_guide_outWM}.outputMatrix',
            target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            weight=1,
            scale_weight=0,
            translate_weight=1,
            rotate_weight=0,
            shear_weight=0,
            name=f'{self.name}_wrist_fk_guide_outWM'
        )

        wrist_IK_ctl_POM = nodes.create_multMatrix_node(
            [f'{wrist_fk_guide_outWM}.outputMatrix', f'{self.org_grps["parent_guide_inputs_grp"]}.worldInverseMatrix[0]'],
            name=f'{self.name}_wrist_IK_ctl_POM'
        )
        nodes.create_multMatrix_node(
            [f'{wrist_IK_ctl_POM}.matrixSum', f'{self.org_grps["parent_inputs_grp"]}.offsetParentMatrix'],
            f'{self.wrist_ik_ctl}.offsetParentMatrix',
            name=f'{self.name}_wrist_ik_ctl_WM'
        )

        elbow_IK_guide_POM = nodes.create_multMatrix_node(
            [f'{elbow_orientPlane_guide}.outputMatrix', f'{self.org_grps["parent_guide_inputs_grp"]}.worldInverseMatrix'],
            name=f'{self.name}_elbow_IK_guide_POM'
        )
        elbow_IK_baseWM = nodes.create_multMatrix_node(
            [f'{elbow_IK_guide_POM}.matrixSum', f'{self.org_grps["parent_inputs_grp"]}.offsetParentMatrix'],
            name=f'{self.name}_elbow_IK_baseWM'
        )

        nodes.create_blendMatrix_node(
            input=f'{elbow_IK_baseWM}.matrixSum',
            target_matrix=f'{self.wrist_ik_ctl}.worldMatrix[0]',
            weight=0.5,
            scale_weight=0,
            translate_weight=1,
            rotate_weight=0,
            shear_weight=0,
            targets=f'{self.elbow_ik_ctl}.offsetParentMatrix',
            name=f'{self.name}_elbow_IK_ctl_WM'
        )
        elbow_IK_ctl_axisY = nodes.create_rowFromMatrix_node(
            f'{self.elbow_ik_ctl}.worldMatrix[0]',
            input=1,
            name=f'{self.name}_elbow_IK_ctl_axisY'
        )
        # This section should be expanded upon when I finish the manual rig...

        shoulder_guide_outWM = nodes.create_aimMatrix_node(
            input_matrix=f'{self.elbow_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_input_axis=(1, 0, 0),
            primary_mode=1,
            primary_target_vector=(0, 0, 0),
            secondary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            secondary_input_axis=(0, -1, 0),
            secondary_mode=1,
            secondary_target_vector=(0, 0, 0),
            name=f'{self.name}_shoulder_guide_outWM'
        )
        shoudler_fk_ctl_POM = nodes.create_multMatrix_node(
            [f'{shoulder_guide_outWM}.outputMatrix', f'{self.org_grps["parent_guide_inputs_grp"]}.worldInverseMatrix'],
            name=f'{self.name}_shoulder_fk_ctl_POM'
        )
        shoudler_fk_ctl_WM = nodes.create_multMatrix_node(
            [f'{shoudler_fk_ctl_POM}.matrixSum', f'{self.org_grps["parent_inputs_grp"]}.worldInverseMatrix'],
            f'{self.shoulder_fk_ctl}.offsetParentMatrix',
            name=f'{self.name}_shoulder_fk_ctl_WM'
        )
        shoulder_guide_outWIM = nodes.create_inverseMatrix_node(
            f'{shoulder_guide_outWM}.outputMatrix',
            name=f'{self.name}_shoulder_guide_outWIM'
        )
        elbow_fk_ctl_POM = nodes.create_multMatrix_node(
            [f'{elbow_guide_outWM}.outputMatrix', f'{shoulder_guide_outWIM}.outputMatrix'],
            name=f'{self.name}_elbow_fk_ctl_POM'
        )
        elbow_fk_ctl_WM = nodes.create_multMatrix_node(
            [f'{elbow_fk_ctl_POM}.matrixSum', f'{self.shoulder_fk_ctl}.worldMatrix[0]'],
            targets=f'{self.elbow_fk_ctl}.offsetParentMatrix',
            name=f'{self.name}_fk_ctl_WM'
        )
        wrist_fk_ctl_POM = nodes.create_multMatrix_node(
            [f'{wrist_fk_guide_outWM}.outputMatrix', f'{elbow_guide_outWIM}.outputMatrix'],
            name=f'{self.name}_wrist_fk_ctl_POM'
        )
        wrist_fk_ctl_WM = nodes.create_multMatrix_node(
            [f'{wrist_fk_ctl_POM}.matrixSum', f'{self.elbow_fk_ctl}.worldMatrix[0]'],
            f'{self.wrist_fk_ctl}.offsetParentMatrix',
            name=f'{self.name}_wrist_fk_ctl_WM'
        )
        return
        upper_initialLength = nodes.create_distanceBetween_node(
            f'{self.shoulder_guide}.worldMatrix[0]',
            f'{self.elbow_guide}.worldMatrix[0]',
            name=f'{self.name}_upper_initialLength'
        )
        lower_initialLength = nodes.create_distanceBetween_node(
            f'{self.elbow_guide}.worldMatrix[0]',
            f'{self.wrist_guide}.worldMatrix[0]',
            name=f'{self.name}_lower_initialLength'
        )
        initialLength = nodes.create_sum_node(
            [f'{upper_initialLength}.distance', f'{lower_initialLength}.distance'],
            name=f'{self.name}_initialLength'
        )
        length = nodes.create_distanceBetween_node(
            f'{shoudler_fk_ctl_WM}.matrixSum',
            f'{self.wrist_ik_ctl}.worldMatrix[0]',
            name=f'{self.name}length'
        )
        lengthRatio = nodes.create_divide_node(
            f'{length}.distance',
            f'{initialLength}.output',
            name=f'{self.name}_lengthRatio'
        )
        scalar = nodes.create_max_node(
            [f'{lengthRatio}.output', 1],
            name=f'{self.name}_scalar'
        )
        upper_length = nodes.create_multiply_node(
            [f'{upper_initialLength}.distance', f'{scalar}.output'],
            f'{self.elbow_ik_jnt}.translateX',
            name=f'{self.name}_upper_length'
        )
        lower_length = nodes.create_multiply_node(
            [f'{lower_initialLength}.distance', f'{scalar}.output'],
            f'{self.wrist_ik_jnt}.translateX',
            name=f'{self.name}_lower_length'
        )

        # pythagorean theorem, getting the length of side "B"
        a2 = nodes.create_power_node(
            f'{upper_length}.output',
            name='a2'
        )
        b2 = nodes.create_power_node(
            f'{lower_length}.output',
            name='b2'
        )
        c2 = nodes.create_power_node(
            f'{length}.distance',
            name='c2'
        )
        a2_c2_sum = nodes.create_sum_node(
            [f'{a2}.output', f'{c2}.output'],
            name='a2_c2_sum'
        )
        a2_b2_sum = nodes.create_sum_node(
            [f'{a2}.output', f'{b2}.output'],
            name='a2_b2_sum'
        )
        subtract1 = nodes.create_subtract_node(
            f'{a2_c2_sum}.output', 
            f'{b2}.output',
            name='subtract1'
        )
        _2ac = nodes.create_multiply_node(
            [2, f'{length}.distance', f'{upper_length}.output'],
            name='_2ac'
        )
        divide1 = nodes.create_divide_node(
            f'{subtract1}.output',
            f'{_2ac}.output',
            name='divide1'
        )
        acos1 = nodes.create_acos_node(
            f'{divide1}.output',
            f'{self.shoulder_ik_jnt}.rotateY',
            'acos1'
        )
        subtract2 = nodes.create_subtract_node(
            f'{a2_b2_sum}.output',
            f'{_2ac}.output',
            name='subtract1'
        )
        _2ab = nodes.create_multiply_node(
            [2, f'{upper_length}.output', f'{lower_length}.output'],
            name='_2ab'
        )
        divide2 = nodes.create_divide_node(
            f'{subtract2}.output', 
            f'{_2ab}.output',
            name='divide2'
        )
        acos2 = nodes.create_acos_node(
            f'{divide1}.output',
            name='acos2'
        )
        subtract3 = nodes.create_subtract_node(
            f'{acos2}.output', 
            180,
            f'{self.elbow_ik_jnt}.rotateY',
            name='subtract3'
        )


    def add_joints(self):
        pass

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
