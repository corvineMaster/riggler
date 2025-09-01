import os
import sys

from functools import partial
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from riggler.core import shapes, custom_widgets, guide, component, nodes, attribute, transform

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
        self.shoulder_guide = self.createRootGuide(self.name + '_shoulder', self.org_grps["guides_grp"], show_axis=True)
        self.elbow_guide = self.createGuide(self.name + '_elbow', self.org_grps["guides_grp"], show_axis=True)
        cmds.setAttr(f'{self.elbow_guide}.tx', lock=True)
        cmds.transformLimits(self.elbow_guide, translationY=(-0.01, -0.01), enableTranslationY=(0, 1))
        self.wrist_guide = self.createGuide(self.name + '_wrist', self.org_grps["guides_grp"])
        cmds.setAttr(f'{self.wrist_guide}.translate', 10, 0, 0)
        self.pole_vector_guide = self.createMiscGuide(self.name + '_pole_vector', self.org_grps["guides_grp"])
        cmds.setAttr(f'{self.pole_vector_guide}.translate', 5, 0, 5)

        for guide in (self.elbow_guide, self.wrist_guide, self.pole_vector_guide):
            attribute.lockAndHideAttributes(guide, ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        attribute.lockAndHideAttributes(self.shoulder_guide, ['sx', 'sy', 'sz', 'v'])
        attribute.lockAndHideAttributes(self.elbow_guide, ['tx'])
        cmds.setAttr(f'{self.pole_vector_guide}.v', lock=False)

        self.shoulder_fk_ctl = shapes.create_ctrl(shapes.ctrlShapes.circleX, self.name + '_shoulder_fk_ctl', self.org_grps["controls_grp"])
        self.elbow_fk_ctl = shapes.create_ctrl(shapes.ctrlShapes.circleX, self.name + '_elbow_fk_ctl', self.org_grps["controls_grp"])
        self.elbow_ik_ctl = shapes.create_ctrl(shapes.ctrlShapes.pointer, self.name + '_elbow_ik_ctl', self.org_grps["controls_grp"])
        self.wrist_fk_ctl = shapes.create_ctrl(shapes.ctrlShapes.circleX, self.name + '_wrist_fk_ctl', self.org_grps["controls_grp"])
        self.wrist_ik_ctl = shapes.create_ctrl(shapes.ctrlShapes.cube, self.name + '_wrist_ik_ctl', self.org_grps["controls_grp"])
        self.pole_vector_ctl = shapes.create_ctrl(shapes.ctrlShapes.diamond, self.name + '_pole_vector_ctl', self.org_grps["controls_grp"])

        self.shoulder_ik_jnt = shapes.create_joint(f'{self.name}_shoulder_IK_jnt', self.org_grps["internals_grp"], (0, 0, 0))
        self.elbow_ik_jnt = shapes.create_joint(f'{self.name}_elbow_IK_jnt', self.shoulder_ik_jnt, (1, 0, 0))
        self.wrist_ik_jnt = shapes.create_joint(f'{self.name}_wrist_IK_jnt', self.elbow_ik_jnt, (2, 0, 0))

        for control in [self.shoulder_fk_ctl, self.elbow_fk_ctl, self.elbow_ik_ctl, self.wrist_fk_ctl, self.wrist_ik_ctl, self.pole_vector_ctl]:
            attribute.lockAndHideAttributes(control, ['sx', 'sy', 'sz', 'v'])
        attribute.lockAndHideAttributes(self.pole_vector_ctl, ['tx', ])
        attribute.lockAndHideAttributes(self.elbow_ik_ctl, ['tx', 'ty', 'tz', 'ry', 'rz'])

    def add_attributes(self):
        pass

    def add_operators(self):
        world_up = transform.get_world_up(negative=True)
        # FK control chain without parenting
        elbow_fk_ctl_WM = nodes.create_multMatrix_node(
            [f'{self.elbow_guide}.matrix', f'{self.shoulder_fk_ctl}.worldMatrix'], 
            f'{self.elbow_fk_ctl}.offsetParentMatrix', 
            f'{self.elbow_fk_ctl}_WM'
        )
        wrist_fk_ctl_WM = nodes.create_multMatrix_node(
            [f'{self.wrist_guide}.matrix', f'{self.elbow_fk_ctl}.worldMatrix'], 
            f'{self.wrist_fk_ctl}.offsetParentMatrix', 
            f'{self.wrist_fk_ctl}_WM'
        )

        # FK guide chain without parenting
        elbow_fk_ctl_POM = nodes.create_multMatrix_node(
            [f'{self.elbow_guide}.worldMatrix[0]', f'{self.shoulder_guide}.worldInverseMatrix[0]'], 
            f'{elbow_fk_ctl_WM}.matrixIn[0]', 
            f'{self.elbow_fk_ctl}_POM'
        )
        wrist_fk_ctl_POM = nodes.create_multMatrix_node(
            [f'{self.wrist_guide}.worldMatrix[0]', f'{self.elbow_guide}.worldInverseMatrix[0]'], 
            f'{wrist_fk_ctl_WM}.matrixIn[0]',
            f'{self.wrist_fk_ctl}_POM'
        )

        # align controls without rotating guides
        shoulder_guide_outWM = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.elbow_guide}.worldMatrix[0]',
            secondary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            secondary_input_axis = world_up,
            secondary_mode=1,
            targets=f'{self.shoulder_fk_ctl}.offsetParentMatrix',
            name=f'{self.shoulder_guide}_outWM'
        )
        shoulder_fk_ctl_WM = self.connect_to_input(self.shoulder_fk_ctl)
        shoulder_guide_outWIM = nodes.create_inverseMatrix_node(f'{shoulder_guide_outWM}.outputMatrix', f'{elbow_fk_ctl_POM}.matrixIn[1]', f'{self.shoulder_guide}_outWIM')
        elbow_guide_outWM = nodes.create_aimMatrix_node(
            input_matrix=f'{self.elbow_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            secondary_target_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            secondary_input_axis=world_up,
            secondary_mode=1,
            targets=f'{elbow_fk_ctl_POM}.matrixIn[0]',
            name=f'{self.elbow_guide}_outWM'
        )
        elbow_guide_outWIM = nodes.create_inverseMatrix_node(f'{elbow_guide_outWM}.outputMatrix', f'{wrist_fk_ctl_POM}.matrixIn[1]', f'{self.elbow_guide}_outWIM')
        # NOTE: This does not properly orient the wrist control to the elbow
        wrist_guide_outWM = nodes.create_blendMatrix_node(
            input=f'{elbow_guide_outWM}.outputMatrix',
            target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            scale_weight=0,
            rotate_weight=0,
            shear_weight=0,
            targets=[f'{wrist_fk_ctl_POM}.matrixIn[0]', f'{self.wrist_ik_ctl}.offsetParentMatrix'],
            name=f'{self.wrist_guide}_outWM'
        )
        # Choose whether or not to the wrist should aim at the elbow. NOTE: Should eventually replace with adjusting f'{wrist_guide_outWM}.rotateWeight'
        wrist_fk_ctl_aim_enable = nodes.create_choice_node(
            inputs=[f'{wrist_guide_outWM}.outputMatrix', f'{self.wrist_guide}.worldMatrix[0]'], 
            selector=0,
            targets=f'{wrist_fk_ctl_POM}.matrixIn[0]',
            name=f'{self.wrist_fk_ctl}_aim_enable'
            )
        
        # Align with pole vector
        orientPlane_pole_vector_guide = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            secondary_target_matrix=f'{self.pole_vector_guide}.worldMatrix[0]',
            secondary_input_axis=world_up,
            secondary_mode=1,
            name=f'{self.name}_orientPlane_pole_vector_guide'
        )
        orientPlane_rotate_guide = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            secondary_target_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            secondary_input_axis=world_up,
            secondary_mode=2,
            secondary_target_vector=(0, 0, 1),
            name=f'{self.name}_orientPlane_rotate_guide'
        )

        orientPlane_pole_vector_enable = nodes.create_choice_node(
            inputs=[f'{orientPlane_pole_vector_guide}.outputMatrix', f'{orientPlane_rotate_guide}.outputMatrix'], 
            selector=0,
            name=f'{self.wrist_fk_ctl}_orientPlane_pole_vector_enable'
            )
        for axis in 'XYZ':
            cmds.connectAttr(f'{orientPlane_pole_vector_enable}.selector', f'{self.shoulder_guide}|pointer{axis}Shape.visibility')
        nodes.create_reverse_node(
            input=f'{orientPlane_pole_vector_enable}.selector',
            targets=f'{self.pole_vector_guide}.v'
        )

        # Setup IK controls
        cmds.connectAttr(f'{self.pole_vector_guide}.worldMatrix[0]', f'{self.pole_vector_ctl}.offsetParentMatrix')
        elbow_guide_WM = nodes.create_blendMatrix_node(
            input=f'{orientPlane_pole_vector_enable}.output',
            target_matrix=f'{self.wrist_guide}.worldMatrix[0]',
            weight=0.5,
            scale_weight=0,
            rotate_weight=0,
            shear_weight=0,
            targets=[f'{self.elbow_guide}.offsetParentMatrix', f'{self.elbow_ik_ctl}.offsetParentMatrix'],
            name=f'{self.elbow_guide}_WM'
        )
        ################# Experimental Pole Vector Appproach (Start) #################
        orientPlane_pole_vector = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_ik_ctl}.worldMatrix[0]',
            secondary_target_matrix=f'{self.pole_vector_ctl}.worldMatrix[0]',
            secondary_input_axis=world_up,
            secondary_mode=1,
            name=f'{self.name}_orientPlane_pole_vector'
        )
        orientPlane_rotate = nodes.create_aimMatrix_node(
            input_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            primary_target_matrix=f'{self.wrist_ik_ctl}.worldMatrix[0]',
            secondary_target_matrix=f'{self.shoulder_guide}.worldMatrix[0]',
            secondary_input_axis=world_up,
            secondary_mode=2,
            secondary_target_vector=(0, 0, 1),
            name=f'{self.name}_orientPlane_rotate'
        )
        orientPlane_pole_vector_enable_02 = nodes.create_choice_node(
            inputs=[f'{orientPlane_pole_vector}.outputMatrix', f'{orientPlane_rotate}.outputMatrix'], 
            selector=f'{orientPlane_pole_vector_enable}.selector',
            name=f'{self.wrist_fk_ctl}_orientPlane_pole_vector_enable_02'
        )
        ################# Experimental Pole Vector Appproach (End) #################
        elbow_ik_ctl_WM = nodes.create_blendMatrix_node(
            input=f'{orientPlane_pole_vector_enable_02}.output',
            target_matrix=f'{self.wrist_ik_ctl}.worldMatrix[0]',
            weight=0.5,
            scale_weight=0,
            rotate_weight=0,
            shear_weight=0,
            name=f'{self.elbow_ik_ctl}_WM'
        )
        elbow_ik_ctl_WM_WM = self.connect_to_input(elbow_ik_ctl_WM, 'inputMatrix')
        wrist_ik_ctl_WM = self.connect_to_input(self.wrist_ik_ctl)
        
        # Joint setup
        cmds.connectAttr(f'{shoulder_fk_ctl_WM}.matrixSum', f'{self.shoulder_ik_jnt}.offsetParentMatrix')
        ik_handle, effector = cmds.ikHandle(startJoint=self.shoulder_ik_jnt, endEffector=self.wrist_ik_jnt, solver='ikRPsolver', name=f'{self.name}_ikHandle')
        cmds.parent(ik_handle, self.org_grps["internals_grp"])
        effector = cmds.rename(effector, f'{self.name}_effector')
        cmds.setAttr(f'{ik_handle}.translate', 0, 0, 0)
        elbow_ik_ctl_WM_axisY = nodes.create_multiplyVectorByMatrix_node(
            inputs=[0, -1, 0],
            matrix=f'{elbow_ik_ctl_WM}.outputMatrix',
            name=f'{elbow_ik_ctl_WM}_axisY'
        )
        cmds.connectAttr(f'{elbow_ik_ctl_WM_axisY}.output', f'{ik_handle}.poleVector')
        cmds.connectAttr(f'{self.elbow_ik_ctl}.rotateX', f'{ik_handle}.twist')

        wrist_ik_ctl_outWTM = nodes.create_pickMatrix_node(
            f'{self.wrist_ik_ctl}.worldMatrix[0]',
            f'{ik_handle}.offsetParentMatrix',
            scale=False,
            rotate=False,
            shear=False,
            name=f'{self.wrist_ik_ctl}_outWTM'
        )

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
            f'{shoulder_fk_ctl_WM}.matrixSum',
            f'{self.wrist_ik_ctl}.worldMatrix[0]',
            name=f'{self.name}_length'
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

        return
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
