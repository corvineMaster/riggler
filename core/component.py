import os
import sys

from functools import partial
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from riggler.core import guide, shapes

from maya import cmds, mel, OpenMayaUI

from PySide6 import QtCore, QtGui, QtWidgets

from riggler.core import attribute, color, nodes


def add_underscore_to_string(string: str) -> str:
    if string:
        string = string + '_'
    return string


def cleanup_name(name_orig):
    name = ''.join([letter if letter.isalnum() else '_' for letter in name_orig])
    if name[0].isnumeric():
        name = f'_{name}'
    return name


def checkDuplicateName(name_orig):
    name = name_orig
    if cmds.objExists(name_orig):
        i = 1
        while cmds.objExists(name_orig + str(i)):
            i += 1
        name = name_orig + str(i)
    return name


class Component(guide.GuideElements):
    about_grp = 'about'
    inputs_grp = 'inputs'
    parent_inputs_grp = 'parent_inputs'
    parent_guide_inputs_grp = 'parent_guide_inputs'
    outputs_grp = 'outputs'
    guides_grp = 'guides'
    internals_grp = 'internals'
    controls_grp = 'controls'
    displays_grp = 'displays'

    steps = [
        "Objects",
        "Properties",
        "Operators",
        "Connect",
        "Joints",
        "Finalize",
    ]
    settings = {}

    def __init__(self, name: str, parent: str=None) -> None:
        super().__init__()
        self.org_grps = {
            'about_grp': 'about',
            'inputs_grp': 'inputs',
            'parent_inputs_grp': 'parent_input',
            'parent_guide_inputs_grp': 'parent_guide_input',
            'outputs_grp': 'outputs',
            'guides_grp': 'guides',
            'internals_grp': 'internals',
            'controls_grp': 'controls',
            'displays_grp': 'displays'
        }
        self.name = cleanup_name(name)
        self.parent = parent
        self.comp_root = ''
        self.stepMethods = [
            getattr(self, f"step_0{i}")()
            for i in range(len(self.steps))
        ]
    
    def step_00(self):
        self.create_initial_component()
        self.connect_to_parent(self.parent)
        self.add_objects()
        
    def step_01(self):
        self.add_attributes()
        
    def step_02(self):
        self.add_operators()
        
    def step_03(self):
        self.add_connections()
        
    def step_04(self):
        self.add_joints()
        
    def step_05(self):
        self.finalize()
    
    def create_initial_component(self) -> None:
        if cmds.objExists(self.name + '_cmpt'):
            return
        self.comp_root = self.create_comp_part('cmpt')
        for org_grp, part in self.org_grps.items():
            parent = 'inputs' if part.endswith('_input') else self.comp_root
            self.create_comp_part(part, org_grp, parent)
    
    def create_comp_part(self, name: str, org_grp: str=None, parent: str=None) -> str:
        if parent and not parent.startswith(self.name):
            parent = self.name + '_' + parent
        if not name.startswith(self.name):
            name = self.name + '_' + name
        if parent is None:
            org_part = cmds.group(name=name, world=True, empty=True)
        else:
            org_part = cmds.group(name=name, parent=parent, empty=True)
        attribute.hideAttributes(org_part)
        cmds.addAttr(org_part, longName='is_cmpt_org', attributeType='bool', defaultValue=True)
        if org_grp:
            self.org_grps[org_grp] = org_part
        return org_part

    def connect_to_parent(self, component_name: str) -> None:
        """
        Creates parent connections between and given component and this component

        Args:
            component_name: The name of the component that we're parenting to this one
        """
        if component_name is None:
            return
        parent_guide_out, parent_out = cmds.listRelatives(component_name + '_outputs')
        cmds.connectAttr(f'{parent_guide_out}.worldMatrix[0]', f'{self.org_grps["parent_guide_inputs_grp"]}.offsetParentMatrix', force=True)
        cmds.connectAttr(f'{parent_out}.worldMatrix[0]', f'{self.org_grps["parent_inputs_grp"]}.offsetParentMatrix', force=True)

    def connect_to_input(self, obj: str, input_attr: str='offsetParentMatrix') -> None:
        """
        Creates a connection between the parent input nodes and a given object

        Args:
            obj: The object to connect the input nodes to
            input_attr: The node attribute to connect everything to
        """
        in_matrix_0 = cmds.listConnections(f'{obj}.{input_attr}', destination=False, plugs=True)
        if not in_matrix_0:
            in_matrix_0 = [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]]  # Identity Matrix
        obj_POM = nodes.create_multMatrix_node(
            in_matrix=[in_matrix_0[0], f'{self.org_grps["parent_guide_inputs_grp"]}.worldInverseMatrix[0]'],
            name=f'{obj}_POM'
        )
        obj_WM = nodes.create_multMatrix_node(
            in_matrix=[f'{obj_POM}.matrixSum', f'{self.org_grps["parent_inputs_grp"]}.offsetParentMatrix'],
            name=f'{obj}_WM'
        )
        cmds.connectAttr(f'{obj_WM}.matrixSum', f'{obj}.{input_attr}', force=True)

        return obj_WM

    def create_output(self, obj: str, is_guide: bool=False):
        suffix = 'guide_output' if is_guide else 'output'
        output_node = cmds.group(name=f'{obj}_{suffix}', parent=self.org_grps['outputs_grp'], empty=True)
        attribute.hideAttributes(output_node)
        cmds.connectAttr(f'{obj}.worldMatrix[0]', f'{output_node}.offsetParentMatrix')
        cmds.select(clear=True)
        return output_node
    
    def add_objects(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')

    def add_attributes(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')

    def add_operators(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')

    def add_connections(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')
    
    def add_joints(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')
    
    def finalize(self):
        cmds.warning('THIS STEP IS NOT IMPLEMENTED, SKIPPING.')
