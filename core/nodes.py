"""
A collection of utility functions for generating most of Maya's math nodes, especially the ones created in 2024 and 2025 due to their standardized plug names.
"""
from typing import Union
import maya.cmds as cmds


########## Universal helper functions ##########

def _create_multi_input_math_node(node_type: str, inputs: list[Union[str, int, float]], targets: list[str]=None, matrix: bool=False, name: str=None, input_prefix='input'):
    inputs = _ensure_is_list(inputs)
    targets = _ensure_is_list(targets)

    node = _create_node(node_type, name)
    for i, input in enumerate(inputs):
        if matrix:
            _connect_or_set_input_attr(input, f'{node}.matrixIn[{i}]', is_matrix=True)
        else:
            _connect_or_set_input_attr(input, f'{node}.{input_prefix}[{i}]')
    
    for target in targets:
        cmds.connectAttr(f'{node}.output', target, force=True)
        
    return node


def _create_rgb_xyz_input_math_node(node_type: str, input=(0, 0, 0), targets: list[str]=None, name: str=None, input_prefix: str='input', rgb=False):
    input = _ensure_is_list(input)
    targets = _ensure_is_list(targets)
    suffix_letters = 'RGB' if rgb else 'XYZ'

    node = _create_node(node_type, name)
    for input, suffix in zip(input, suffix_letters):
        _connect_or_set_input_attr(input, f'{node}.{input_prefix + suffix}')
            
    if targets:
        obj, attr = targets[0].split('.')
        target_type = cmds.attributeQuery(attr, node=obj, attributeType=True)
        if target_type == 'double3':
            for target, suffix in zip(targets, suffix_letters):
                cmds.connectAttr(f'{node}.output{suffix}', target, force=True)
        else:
            for target in targets:
                cmds.connectAttr(f'{node}.output', target, force=True)
            
    return node


def _create_dual_input_math_node(node_type: str, input1: Union[str, float, int], input2: Union[str, float, int], targets: list[str]=None, name: str=None):
    targets = _ensure_is_list(targets)

    node = _create_node(node_type, name)
    for input, attr in zip((input1, input2), ('input1', 'input2')):
        _connect_or_set_input_attr(input, f'{node}.{attr}')
    
    for target in targets:
        cmds.connectAttr(f'{node}.output', target, force=True)

    return node


def _create_single_input_math_node(node_type: str, input: Union[str, float, int, list[int]], targets: list[str]=None, in_matrix: bool=False, name: str=None):
    targets = _ensure_is_list(targets)

    node = _create_node(node_type, name)
    if input:
        if isinstance(input, str):
            cmds.connectAttr(input, f'{node}.input')
        elif in_matrix:
            in_attr = 'input' if cmds.objExists(f'{node}.input') else 'inMatrix'
            cmds.setAttr(f'{node}.{in_attr}', input, type='matrix')
        else:
            cmds.setAttr(f'{node}.input', input)
    
    for target in targets:
        output = 'output' if cmds.objExists(f'{node}.output') else 'outMatrix'
        cmds.connectAttr(f'{node}.{output}', target, force=True)
    
    return node


def _set_xyz_outputs(node: str, targets: list[str], add_w_output: bool=False):
    targets = _ensure_is_list(targets)
    if not targets:
        return

    obj, attr = targets[0].split('.')
    attr_type = cmds.attributeQuery(attr, node=obj, attributeType=True)
    if attr_type == 'double4' or attr_type == 'double3':
        for target in targets:
            cmds.connectAttr(f'{node}.output', target, force=True)
    else:
        xyz = 'XYZW' if add_w_output else 'XYZ'
        for target, axis in zip(targets, xyz):
            cmds.connectAttr(f'{node}.output{axis}', target, force=True)

# create_aimMatrix_node
def _connect_or_set_input_attr(source_attr: Union[str, int, float, list[int]], dest_attr: str, is_matrix: bool=False):
    if source_attr is None or dest_attr is None:
        return
    if isinstance(source_attr, str):
        cmds.connectAttr(source_attr, dest_attr)
    elif is_matrix:
        cmds.setAttr(dest_attr, source_attr, type='matrix')
    else:
        cmds.setAttr(dest_attr, source_attr)

def _ensure_is_list(var: any):
    return [] if var is None else list(var) if isinstance(var, (tuple, list, set, dict)) else [var]

def _create_node(node_type: str, name: str=None):
    node = cmds.createNode(node_type)
    if name:
        node = cmds.rename(node, name)
    return node

########## Comparison ##########

def create_and_node(input1: Union[str, bool], input2: Union[str, bool], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('and', input1, input2, targets, name)


def create_equal_node(input1: Union[str, int, float], input2: Union[str, int, float], epsilon: Union[str, int, float]=0, targets: list[str]=None, name: str=None):
    node = _create_dual_input_math_node('equal', input1, input2, targets, name)
    _connect_or_set_input_attr(epsilon, f'{node}.epsilon')
    return node


def create_greaterThan_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('greaterThan', input1, input2, targets, name)


def create_lessThan_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('lessThan', input1, input2, targets, name)


def create_max_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_multi_input_math_node('max', input, targets, name=name)


def create_min_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_multi_input_math_node('min', input, targets, name=name)


def create_not_node(input: Union[str, bool], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('not', input, targets)


def create_or_node(input1: Union[str, bool], input2: Union[str, bool], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('or', input1, input2, targets, name)


########## Operation ##########

def create_absolute_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('max', input, targets)


def create_average_node(inputs: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_multi_input_math_node('average', inputs, targets, name=name)


def create_divide_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('divide', input1, input2, targets, name)


def create_inverseLerp_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, interpolation: Union[str, int, float]=0, name: str=None):
    node = _create_dual_input_math_node('inverseLerp', input1, input2, targets, name)
    _connect_or_set_input_attr(interpolation, f'{node}.interpolation')
    return node


def create_lerp_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, weight: Union[str, int, float]=0, name: str=None):
    node = _create_dual_input_math_node('lerp', input1, input2, targets, name)
    _connect_or_set_input_attr(weight, f'{node}.weight')
    return node


def create_log_node(input: Union[str, float, int], targets: list[str]=None, base: Union[str, int, float]=2, name: str=None):
    node = _create_single_input_math_node('log', input, targets, name=name)
    _connect_or_set_input_attr(base, f'{node}.base')
    return node


def create_modulo_node(input: Union[str, float, int], targets: list[str]=None, modulus: Union[str, int, float]=1, name: str=None):
    node = _create_single_input_math_node('modulo', input, targets, name=name)
    _connect_or_set_input_attr(modulus, f'{node}.modulus')
    return node


def create_multiply_node(inputs: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_multi_input_math_node('multiply', inputs, targets, name=name)


def create_negate_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('negate', input, targets, name=name)


def create_power_node(input: Union[str, float, int], targets: list[str]=None, exponent: Union[str, int, float]=2, name: str=None):
    node = _create_single_input_math_node('power', input, targets, name=name)
    _connect_or_set_input_attr(exponent, f'{node}.exponent')
    return node


def create_subtract_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('subtract', input1, input2, targets, name=name)


def create_sum_node(inputs: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_multi_input_math_node('sum', inputs, targets, name=name)


########## Rounding ##########

def create_ceil_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('ceil', input, targets, name=name)


def create_clampRange_node(input: Union[str, float, int], targets: list[str]=None, minimum: Union[str, float, int]=0, maximum: Union[str, float, int]=1, name: str=None):
    node = _create_single_input_math_node('clampRange', input, targets, name=name)
    _connect_or_set_input_attr(minimum, f'{node}.minimum')
    _connect_or_set_input_attr(maximum, f'{node}.maximum')
    return node


def create_floor_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('floor', input, targets, name=name)


def create_round_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('round', input, targets, name=name)


def create_smoothStep_node(input: Union[str, float, int], targets: list[str]=None, leftEdge: Union[str, float, int]=0, rightEdge: Union[str, float, int]=1, name: str=None):
    node = _create_single_input_math_node('smoothStep', input, targets, name=name)
    _connect_or_set_input_attr(leftEdge, f'{node}.leftEdge')
    _connect_or_set_input_attr(rightEdge, f'{node}.rightEdge')
    return node


def create_truncate_node(input: Union[str, float, int], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('truncate', input, targets, name=name)


########## Matrix ##########

def create_addMatrix_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    node = _create_multi_input_math_node('addMatrix', input, matrix=True, name=name)

    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.matrixSum', target)

    return node


def create_aimMatrix_node(
    input_matrix: Union[str, list[int]], 
    primary_target_matrix: Union[str, list[int]], 
    secondary_target_matrix: Union[str, list[int]], 
    targets: list[str]=None, 
    primary_input_axis: Union[tuple[str], tuple[Union[int, float]]]=(1, 0, 0), 
    secondary_input_axis: Union[tuple[str], tuple[Union[int, float]]]=(0, 1, 0), 
    primary_mode: int=1, 
    secondary_mode: int=0, 
    primary_target_vector: Union[tuple[str], tuple[Union[int, float]]]=(0, 0, 0), 
    secondary_target_vector: Union[tuple[str], tuple[Union[int, float]]]=(0, 0, 0), 
    pre_space_matrix: Union[str, list[int]]=None, 
    post_space_matrix: Union[str, list[int]]=None,
    name: str=None
):
    node = _create_node('aimMatrix', name)
    _connect_or_set_input_attr(input_matrix, f'{node}.inputMatrix', is_matrix=True)
    _connect_or_set_input_attr(primary_target_matrix, f'{node}.primary.primaryTargetMatrix', is_matrix=True)
    _connect_or_set_input_attr(secondary_target_matrix, f'{node}.secondary.secondaryTargetMatrix', is_matrix=True)
    for i, axis in enumerate('XYZ'):
        _connect_or_set_input_attr(primary_input_axis[i], f'{node}.primaryInputAxis{axis}')
        _connect_or_set_input_attr(primary_target_vector[i], f'{node}.primaryTargetVector{axis}')
        _connect_or_set_input_attr(secondary_input_axis[i], f'{node}.secondaryInputAxis{axis}')
        _connect_or_set_input_attr(secondary_target_vector[i], f'{node}.secondaryTargetVector{axis}')
    cmds.setAttr(f'{node}.primaryMode', primary_mode)
    cmds.setAttr(f'{node}.secondaryMode', secondary_mode)
    _connect_or_set_input_attr(pre_space_matrix, f'{node}.preSpaceMatrix', is_matrix=True)
    _connect_or_set_input_attr(post_space_matrix, f'{node}.postSpaceMatrix', is_matrix=True)

    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outputMatrix', target, force=True)

    return node


def create_axisFromMatrix_node(input: Union[str, list[int]], targets: list[str]=None, axis: int=0, name: str=None):
    node = _create_single_input_math_node('axisFromMatrix', input, in_matrix=True, name=name)
    cmds.setAttr(f'{node}.axis', axis)
    _set_xyz_outputs(node, targets)

    return node


def create_blendMatrix_node(
        input: Union[str, list[int]], 
        target_matrix: Union[str, list[str], list[list[int]]], 
        weight: Union[str, int, float, list[Union[str, int, float]]] = 1,
        scale_weight: Union[str, int, float, list[Union[str, int, float]]] = 1,
        translate_weight: Union[str, int, float, list[Union[str, int, float]]] = 1,
        rotate_weight: Union[str, int, float, list[Union[str, int, float]]] = 1,
        shear_weight: Union[str, int, float, list[Union[str, int, float]]] = 1,
        targets: list[str]=None, 
        pre_space_matrix: list[int]=None, 
        post_space_matrix: list[int]=None,
        name: str=None
    ):
    node = _create_node('blendMatrix', name)
    _connect_or_set_input_attr(input, f'{node}.inputMatrix', is_matrix=True)

    for i, matrix in enumerate(_ensure_is_list(target_matrix)):
        _connect_or_set_input_attr(matrix, f'{node}.target[{i}].targetMatrix', is_matrix=True)
    for weight_type, weight_values in {
        'weight': _ensure_is_list(weight), 
        'scaleWeight': _ensure_is_list(scale_weight), 
        'translateWeight': _ensure_is_list(translate_weight), 
        'rotateWeight': _ensure_is_list(rotate_weight), 
        'shearWeight': _ensure_is_list(shear_weight)
    }.items():
        for i, value in enumerate(weight_values):
            _connect_or_set_input_attr(value, f'{node}.target[{i}].{weight_type}')

    if pre_space_matrix:
        _connect_or_set_input_attr(pre_space_matrix, f'{node}.preSpaceMatrix', is_matrix=True)
    if post_space_matrix:
        _connect_or_set_input_attr(post_space_matrix, f'{node}.postSpaceMatrix', is_matrix=True)

    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outputMatrix', target, force=True)

    return node


def create_columnFromMatrix_node(in_matrix: Union[str, list[int]], targets: list[str]=None, input: int=0, name: str=None):
    node = _create_single_input_math_node('columnFromMatrix', in_matrix, in_matrix=True, name=name)
    cmds.setAttr(f'{node}.input', input)
    _set_xyz_outputs(node, targets, add_w_output=True)

    return node


def create_crossProduct_node(input1: list[Union[str, int, float]], input2: list[Union[str, int, float]], targets: str, name: str=None):
    node = _create_node('crossProduct', name)
    for in_1, in_2, xyz in zip(input1, input2, 'XYZ'):
        _connect_or_set_input_attr(in_1, f'{node}.input1{xyz}')
        _connect_or_set_input_attr(in_2, f'{node}.input2{xyz}')

    _set_xyz_outputs(node, targets)

    return node


def create_decomposeMatrix_node(in_matrix: str, targets: list[str]=None, translate: bool=True, rotate: bool=True, scale: bool=True, shear: bool=True, name: str=None):
    node = _create_node("decomposeMatrix", name)
    cmds.connectAttr(in_matrix, f"{node}.inputMatrix")
    for target in _ensure_is_list(targets):
        if translate:
            cmds.connectAttr(f"{node}.outputTranslate", f'{target}.translate')
        if rotate:
            cmds.connectAttr(f"{node}.outputRotate", f'{target}.rotate')
        if scale:
            cmds.connectAttr(f"{node}.outputScale", f'{target}.scale')
        if shear:
            cmds.connectAttr(f"{node}.outputShear",f'{target}.shear')

    return node


def create_determinant_node(input: Union[str, list[int]], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('determinant', input, targets, in_matrix=True, name=name)


def create_dotProduct_node(input1: list[Union[str, int, float]], input2: list[Union[str, int, float]], targets: list[str], name: str=None):
    node = _create_node('dotProduct', name)
    for in_1, in_2, xyz in zip(input1, input2, 'XYZ'):
        _connect_or_set_input_attr(in_1, f'{node}.input1{xyz}')
        _connect_or_set_input_attr(in_2, f'{node}.input2{xyz}')

    _set_xyz_outputs(node, targets)

    return node


def create_fourByFourMatrix_node(inputs: list[Union[str, int]], targets: list[str]=None, name: str=None):
    node = _create_node('fourByFourMatrix', name)
    input_index = 0
    for i in range(4):
        if input_index == len(inputs):
            break
        for j in range(4):
            if input_index == len(inputs):
                break
            _connect_or_set_input_attr(inputs[input_index], f'{node}.{i}{j}')
            input_index += 1
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.output', target, force=True)
    
    return node


def create_holdMatrix_node(input: Union[str, list[int]], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('holdMatrix', input, targets, in_matrix=True, name=name)


def create_inverseMatrix_node(input: Union[str, list[int]], targets: list[str]=None, name: str=None):
    node = _create_node('inverseMatrix', name)
    _connect_or_set_input_attr(input, f'{node}.inputMatrix')
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outputMatrix', target, force=True)

    return node



def create_multiplyPointByMatrix_node(inputs: list[Union[str, int, float]], matrix: Union[str, list[int]], targets: list[str]=None, name: str=None):
    node = _create_single_input_math_node('multiplyPointByMatrix', matrix, in_matrix=True, name=name)
    for input, xyz in zip(inputs, 'XYZ'):
        _connect_or_set_input_attr(input, f'{node}.input{xyz}')

    _set_xyz_outputs(node, targets)

    return node


def create_multiplyVectorByMatrix_node(inputs: list[Union[str, int, float]], matrix: Union[str, list[int]], targets: list[str]=None, name: str=None):
    node = _create_rgb_xyz_input_math_node('multiplyVectorByMatrix', inputs, targets, name)
    _connect_or_set_input_attr(matrix, f'{node}.matrix')

    return node


def create_multMatrix_node(in_matrix: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    node = _create_multi_input_math_node('multMatrix', in_matrix, matrix=True, name=name)
    
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.matrixSum', target, force=True)

    return node


def create_normalize_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_rgb_xyz_input_math_node('normalize', input, targets, name)


def create_parentMatrix_node(
    in_matrix: Union[str, list[int]], 
    in_target_matrices: list[Union[str, list[int]]]=None, 
    in_offset_matrices: list[Union[str, list[int]]]=None, 
    in_weights: Union[str, int, float]=None, 
    targets: list[str]=None, 
    pre_space_matrix: Union[str, list[int]]=None, 
    post_space_matrix: Union[str, list[int]]=None,
    name: str=None
):
    node = _create_node('parentMatrix', name)
    # single input attrs
    for source_attr, dest_attr in zip((in_matrix, 'inputMatrix'), (pre_space_matrix, 'preSpaceMatrix'), (post_space_matrix, 'postSpaceMatrix')):
        _connect_or_set_input_attr(source_attr, f'{node}.{dest_attr}')

    # multi input attrs
    for source_dest_attrs in (in_target_matrices, 'targetMatrix'), (in_offset_matrices, 'offsetMatrix'), (in_weights, 'weight'):
        for source_attr_set, dest_attr in source_dest_attrs:
            if not source_attr_set:
                continue
            for i, source_attr in enumerate(source_attr_set):
                _connect_or_set_input_attr(in_matrix, f'{node}.target[{i}].{dest_attr}', in_matrix=True)
    
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outputMatrix', target, force=True)

    return node


def create_passMatrix_node(input: Union[str, list[int]], targets: list[str]=None, in_scale: Union[str, int, float]=2, name: str=None):
    node = _create_single_input_math_node('passMatrix', input, targets, in_matrix=True, name=name)
    cmds.setAttr(f'{node}.inScale', in_scale)

    return node


def create_pickMatrix_node(in_matrix: Union[str, list[int]]=None, targets: list[str]=None, scale: bool=True, rotate: bool=True, translate: bool=True, shear: bool=True, name: str=None):
    node = _create_node('pickMatrix', name)
    cmds.setAttr(f'{node}.useScale', scale)
    cmds.setAttr(f'{node}.useRotate', rotate)
    cmds.setAttr(f'{node}.useTranslate', translate)
    cmds.setAttr(f'{node}.useShear', shear)
    if in_matrix:
        _connect_or_set_input_attr(in_matrix, f'{node}.inputMatrix', is_matrix=True)
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outputMatrix', target, force=True)

    return node


def create_pointMatrixMult_node(input: Union[str, list[int]], in_point: list[Union[str, int, float]], targets: list[str]=None, vector_multiply: bool=False, name: str=None):
    node = _create_single_input_math_node('pointMatrixMult', input, targets, in_matrix=True, name=name)
    for point, xyz in zip(in_point, 'XYZ'):
        _connect_or_set_input_attr(point, f'{node}.inPoint{xyz}')
    cmds.setAttr(f'{node}.vectorMultiply', vector_multiply)

    return node


def create_rotationFromMatrix_node(in_matrix: Union[str, list[int]], targets: list[str]=None, name: str=None):
    node = _create_single_input_math_node('rotationFromMatrix', in_matrix, in_matrix=True, name=name)
    _set_xyz_outputs(node, targets)

    return node


def create_rowFromMatrix_node(in_matrix: Union[str, list[int]], targets: list[str]=None, input: Union[str, int, float]=0, name: str=None):
    node = _create_node('rowFromMatrix', name)
    _connect_or_set_input_attr(in_matrix, f'{node}.matrix', is_matrix=True)
    _connect_or_set_input_attr(input, f'{node}.input')
    _set_xyz_outputs(node, targets, add_w_output=True)

    return node


def create_scaleFromMatrix_node(in_matrix: Union[str, list[int]], targets: list[str]=None, name: str=None):
    node = _create_single_input_math_node('scaleFromMatrix', in_matrix, in_matrix=True, name=name)
    _set_xyz_outputs(node, targets)

    return node


def create_translationFromMatrix_node(in_matrix, targets: list[str]=None, name: str=None):
    node = _create_single_input_math_node('translationFromMatrix', in_matrix, in_matrix=True, name=name)
    _set_xyz_outputs(node, targets)

    return node

########## Trigonometry ##########

def create_acos_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('acos', input, targets, name=name)


def create_asin_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('asin', input, targets, name=name)


def create_atan_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('atan', input, targets, name=name)


def create_atan2_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('atan2', input1, input2, targets, name=name)


def create_cos_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('cos', input, targets, name=name)


def create_sin_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('sin', input, targets, name=name)


def create_tan_node(input: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_single_input_math_node('tan', input, targets, name=name)

########## Utility ##########

def create_addDoubleLinear_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('addDoubleLinear', input1, input2, targets, name)


def create_angleBetween_node(
        vector1: list[Union[str, int, float]]=[0, 1, 0], 
        vector2: list[Union[str, int, float]]=[0, 0, 1], 
        axis_targets: list[str]=None, 
        euler_targets: list[str]=None, 
        angle_targets: list[str]=None,
        name: str=None
):
    node = _create_rgb_xyz_input_math_node('angleBetween', vector1, name=name, input_prefix='vector1')
    for input, attr in zip((vector2[0], vector2[1], vector2[2]), ('vector2X', 'vector2Y', 'vector2Z')):
        _connect_or_set_input_attr(input, f'{node}.{attr}')

    for target, xyz in zip(_ensure_is_list(axis_targets), 'XYZ'):
        cmds.connectAttr(f'{node}.axis{xyz}', target)
    for target, xyz in zip(_ensure_is_list(euler_targets), 'XYZ'):
        cmds.connectAttr(f'{node}.euler{xyz}', target)
    for target in _ensure_is_list(angle_targets):
        cmds.connectAttr(f'{node}.angle', target)
    
    return node


def create_blendColors_node(
        color1: list[Union[str, int, float]]=[0, 1, 0], 
        color2: list[Union[str, int, float]]=[0, 0, 1], 
        blender: Union[str, int, float]=0.5, 
        targets: list[str]=None, 
        name: str=None
):
    node = _create_rgb_xyz_input_math_node('blendColors', color1, targets=targets, name=name, input_prefix='color1', rgb=True)
    for source_attr, rgb in zip(color2, 'RGB'):
        _connect_or_set_input_attr(source_attr, f'{node}.{rgb}')
    _connect_or_set_input_attr(blender, f'{node}.blender')

    return node


def create_choice_node(inputs: list[Union[str, int, float]], selector: Union[str, int]=0, targets: list[str]=None, name: str=None):
    node = _create_multi_input_math_node('choice', inputs, targets, name=name)
    _connect_or_set_input_attr(selector, f'{node}.selector')

    return node


def create_clamp_node(
        input: list[Union[str, int, float]]=[0, 0, 0], 
        max: list[Union[str, int, float]]=[0, 0, 0], 
        min: list[Union[str, int, float]]=[0, 0, 0], 
        targets: list[str]=None, 
        name: str=None
):
    node = _create_rgb_xyz_input_math_node('clamp', input, targets, name, rgb=True)
    for source_attr, rgb in zip(_ensure_is_list(max), 'RGB'):
        _connect_or_set_input_attr(source_attr, f'{node}.{rgb}')
    for source_attr, rgb in zip(_ensure_is_list(min), 'RGB'):
        _connect_or_set_input_attr(source_attr, f'{node}.{rgb}')

    return node


def create_condition_node(
        true_input: list[Union[str, int, float]]=[0, 0, 0], 
        false_input: list[Union[str, int, float]]=[0, 0, 0], 
        first_term: Union[str, int, float]=0, 
        second_term: Union[str, int, float]=0, 
        operation: int=0, 
        targets: list[str]=None, 
        name: str=None
):
    node = _create_rgb_xyz_input_math_node('condition', true_input, targets, name, 'colorIfTrue', rgb=True)
    for source_attr, rgb in zip(false_input, 'RGB'):
        _connect_or_set_input_attr(source_attr, f'{node}.colorIfFalse{rgb}')
    _connect_or_set_input_attr(first_term, f'{node}.firstTerm')
    _connect_or_set_input_attr(second_term, f'{node}.secondTerm')
    cmds.setAttr(f'{node}.operation', operation)

    return node


def create_curveInfo_node(
        curve: str, 
        arc_length_targets: list[str]=None, 
        control_points_targets: list[list[str]]=None, 
        knots_targets: list[str]=None, 
        weights_targets: list[str]=None, 
        name: str=None
):
    node = _create_node('curveInfo', name)
    cmds.connectAttr(curve, f'{node}.curve')
    for target in _ensure_is_list(arc_length_targets):
        cmds.connectAttr(f'{node}.arcLength', target)
    for control_point in _ensure_is_list(control_points_targets):
        _set_xyz_outputs(node, control_point)
    for i, target in enumerate(_ensure_is_list(knots_targets)):
        cmds.connectAttr(f'{node}.knots[{i}]', target)
    for i, target in enumerate(_ensure_is_list(weights_targets)):
        cmds.connectAttr(f'{node}.weights[{i}]', target)
    
    return node


def create_distanceBetween_node(start, end, targets: list[str]=None, name: str=None):
    node = _create_node('distanceBetween', name)
    if isinstance(start, str):
        try:
            cmds.connectAttr(start, f'{node}.point1')
        except RuntimeError:
            cmds.connectAttr(start, f'{node}.inMatrix1')
    elif isinstance(start, tuple):
        cmds.setAttr(f'{node}.point1', start[0], start[1], start[2])
    else:
        cmds.setAttr(f'{node}.inMatrix1', start, type='matrix')

    if isinstance(end, str):
        try:
            cmds.connectAttr(end, f'{node}.point2')
        except RuntimeError:
            cmds.connectAttr(end, f'{node}.inMatrix2')
    elif isinstance(end, tuple):
        cmds.setAttr(f'{node}.point2', end[0], end[1], end[2])
    else:
        cmds.setAttr(f'{node}.inMatrix2', end, type='matrix')

    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.distance', target, force=True)
    
    return node


def create_multDoubleLinear_node(input1: Union[str, int, float], input2: Union[str, int, float], targets: list[str]=None, name: str=None):
    return _create_dual_input_math_node('multDoubleLinear', input1, input2, targets, name)


def create_multiplyDivide_node(
        input1: Union[list[Union[str, int, float]], str, int, float], 
        input2: Union[list[str, int, float], str, int, float], 
        operation: int=1, 
        targets: list[str]=None, 
        name: str=None
):
    node = _create_rgb_xyz_input_math_node('multiplyDivide', input1, name=name)
    for input, xyz in zip(input2, 'XYZ'):
        _connect_or_set_input_attr(input, f'{node}.input2{xyz}')
    _set_xyz_outputs(node, targets)
    cmds.setAttr(f'{node}.operation', operation)

    return node


def create_plusMinusAverage_node(inputs: Union[list[Union[str, int, float]], str, int, float], targets: list[str]=None, input_output_type: int=1, operation: int=1, name: str=None):
    inputs = _ensure_is_list(inputs)
    targets = _ensure_is_list(targets)
    if input_output_type == 1:
        node = _create_multi_input_math_node('plusMinusAverage', inputs, targets, name=name, input_prefix='input1D')
    elif input_output_type == 2:
        node = _create_node('plusMinusAverage', name)
        for i in range(len(inputs)):
            for input, xy in zip(inputs[i], 'xy'):
                _connect_or_set_input_attr(input, f'{node}.input2D[{i}].input2D{xy}')
        for target, xy in zip(targets, 'xy'):
            cmds.connectAttr(f'{node}.output2D{xy}', target)
    else:
        node = _create_rgb_xyz_input_math_node('plusMinusAverage', inputs[0], targets, name, input_prefix='input3D')
        for i in range(1, len(inputs)):
            for input, xyz in zip(inputs[i], 'xyz'):
                _connect_or_set_input_attr(input, f'{node}.input3D[{i}].input3D{xyz}')
    
    cmds.setAttr(f'{node}.operation', operation)

    return node


def create_remapValue_node(input: Union[str, int, float], input_min: Union[str, int, float], input_max: Union[str, int, float], output_min: Union[str, int, float], output_max: Union[str, int, float], targets: list[str]=None, name: str=None):
    node = _create_node('remapValue', name)
    for dest_attr, source_attr in {'inputValue': input, 'inputMin': input_min, 'inputMax': input_max, 'outputMin': output_min, 'outputMax': output_max}.items():
        _connect_or_set_input_attr(source_attr, f'{node}.{dest_attr}')
    for target in _ensure_is_list(targets):
        cmds.connectAttr(f'{node}.outValue', target, force=True)
    
    return node


def create_reverse_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    node = _create_rgb_xyz_input_math_node('reverse', input, name=name)
    _set_xyz_outputs(node, targets)

    return node


def create_setRange_node(input: Union[str, int, float], min: Union[str, int, float], max: Union[str, int, float], old_min: Union[str, int, float], old_max: Union[str, int, float], targets: list[str]=None, name: str=None):
    node = _create_node('remapValue', name)
    for dest_attr, source_attr in {'value': input, 'min': min, 'max': max, 'oldMin': old_min, 'oldMax': old_max}.items():
        for attr, xyz in zip(_ensure_is_list(source_attr), 'XYZ'):
            _connect_or_set_input_attr(attr, f'{node}.{dest_attr}{xyz}')
    
    for target, xyz in zip(_ensure_is_list(targets), 'XYZ'):
        cmds.connectAttr(f'{node}.outValue{xyz}', target, force=True)
    
    return node


def create_vectorProduct_node(input1: list[Union[str, int, float]], input2: list[Union[str, int, float]], targets: list[str]=None, operation: int=1, normalize_output: bool=False, name: str=None):
    node = _create_rgb_xyz_input_math_node('vectorProduct', input1, targets, name, 'input1')
    for input, xyz in zip(_ensure_is_list(input2), 'XYZ'):
        _connect_or_set_input_attr(input, f'{node}.input2{xyz}')
    cmds.setAttr(f'{node}.operation', operation)
    cmds.setAttr(f'{node}.normalizeOutput', normalize_output)

    return node

########## Other ##########

def create_length_node(input: list[Union[str, int, float]], targets: list[str]=None, name: str=None):
    return _create_rgb_xyz_input_math_node('length', input, targets, name)