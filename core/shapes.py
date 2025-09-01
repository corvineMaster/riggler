import types
import maya.cmds as cmds
from riggler.core import nodes, transform


def add_display_curve(name, objects, degree, parent=None):
    points = []
    points.append(cmds.xform(obj, query=True, translation=True, worldSpace=True) for obj in objects)
    curve = cmds.curve(name=name, degree=degree, points=points, periodic=False, knots=(len(points) + degree - 1))
    cmds.setAttr(f'{curve}.overrideEnabled', 1)
    cmds.setAttr(f'{curve}.overrideDisplayType', 1)
    if parent:
        cmds.parent(curve, parent)


def create_joint(name='joint1', parent=None, translation=[0, 0, 0], matrix=None, offsetParentMatrix=None):
    joint = cmds.createNode('joint', name=name)
    if offsetParentMatrix:
        nodes._connect_or_set_input_attr(joint, offsetParentMatrix, 'offsetParentMatrix')
    elif matrix:
        # TODO: Convert to om2 so that you can set transform values based on matrices directly
        # nodes._connect_or_set_input_attr(joint, matrix, 'matrix')
        pass
    else:
        cmds.setAttr(f'{joint}.translate', translation[0], translation[1], translation[2])

    if parent:
        cmds.parent(joint, parent)
    return joint


def combineShapes(parent: str, children: list[str]) -> str:
    all_child_shapes = []
    for child in children:
        child_shapes = cmds.listRelatives(child, shapes=True)
        all_child_shapes = all_child_shapes + child_shapes
    cmds.parent(all_child_shapes, parent, relative=True, shape=True)
    cmds.delete(children)

    return parent


def sphere() -> str:
    final_sphere = combineShapes(circleX(), [circleY(), circleZ()])
    return final_sphere


def cylinder() -> str:
    circle1 = cmds.circle(normal=(1, 0, 0), center=(1, 0, 0), constructionHistory=False)[0]
    circle2 = cmds.circle(normal=(1, 0, 0), center=(-1, 0, 0), constructionHistory=False)[0]
    child_transforms = [circle2]
    for coordinate in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        line = cmds.curve(point=[(1, coordinate[0], coordinate[1]), (-1, coordinate[0], coordinate[1])], degree=1, knot=[0, 1])
        child_transforms.append(line)
    final_cylinder = combineShapes(circle1, child_transforms)

    return final_cylinder


def circleX() -> str:
    return cmds.circle(normal=(1, 0, 0), constructionHistory=False)[0]


def circleY() -> str:
    return cmds.circle(normal=(0, 1, 0), constructionHistory=False)[0]


def circleZ() -> str:
    return cmds.circle(normal=(0, 0, 1), constructionHistory=False)[0]


def star() -> str:
    star = circleZ()
    cmds.scale(0, 0, 0, [f'{star}.cv[0]', f'{star}.cv[2]', f'{star}.cv[4]', f'{star}.cv[6]'], absolute=True)

    return star


def pointer() -> str:
    pointer = circleZ()
    cmds.scale(0, 1, 1, [f'{pointer}.cv[0]', f'{pointer}.cv[7]'], pivot=(.666666, .39, 0))
    cmds.scale(0, 1, 1, f'{pointer}.cv[2:3]', pivot=(-.666666, .39, 0))
    cmds.scale(0, 0, 0, [f'{pointer}.cv[4]', f'{pointer}.cv[6]'])

    return pointer


class ctrlShapes:
    diamond = [(0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)]
    arrow = [(-0.5, 0.0, -1.0), (-0.5, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.0, -1.0), (-0.5, 0.0, -1.0)]
    double_arrow = [(-0.5, 0.0, -1.0), (-0.5, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.0, -1.0), (-0.5, 0.0, -1.0)]
    sphere = sphere
    cylinder = cylinder
    circleX = circleX
    circleY = circleY
    circleZ = circleZ
    pointer = pointer
    cube = [(-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0), (1.0, -1.0, 1.0)]
    cross = [(1/3, 0.0, 1.0), (-1/3, 0.0, 1.0), (-1/3, 0.0, 1/3), (-1.0, 0.0, 1/3), (-1.0, 0.0, -1/3), (-1/3, 0.0, -1/3), (-1/3, 0.0, -1.0), (1/3, 0.0, -1.0), (1/3, 0.0, -1/3), (1.0, 0.0, -1/3), (1.0, 0.0, 1/3), (1/3, 0.0, 1/3), (1/3, 0.0, 1.0)]
    cube_with_peak = [(-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (0.0, 1.0, 1.0), (0.0, 1.0, -1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 1.0), (0.0, -1.0, 1.0), (1.0, 0.0, 0.0), (0.0, -1.0, -1.0), (0.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0), (0.0, -1.0, -1.0), (0.0, 1.0, -1.0), (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0)]
    locator = [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0)]


def create_ctrl(shape=ctrlShapes.circleX, name='ctrl', parent=None, translation=[0, 0, 0], rotation=[0, 0, 0], size_mult=1, matrix=None, offsetParentMatrix=None):
    if isinstance(shape, types.FunctionType):
        ctrl = shape()
    else:
        ctrl = cmds.curve(point=shape, degree=1)
    ctrl = cmds.rename(ctrl, name)
    cmds.select(clear=True)

    if offsetParentMatrix:
        nodes._connect_or_set_input_attr(ctrl, offsetParentMatrix, 'offsetParentMatrix')
    elif matrix:
        # TODO: Convert to om2 so that you can set transform values based on matrices directly
        # nodes._connect_or_set_input_attr(ctrl, matrix, 'matrix')
        pass
    else:
        cmds.setAttr(f'{ctrl}.translate', translation[0], translation[1], translation[2])
        cmds.setAttr(f'{ctrl}.rotate', rotation[0], rotation[1], rotation[2])
    cmds.scale(size_mult, size_mult, size_mult, f'{ctrl}.cv[*]')

    if parent:
        cmds.parent(ctrl, parent)

    return ctrl