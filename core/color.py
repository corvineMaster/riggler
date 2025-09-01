from maya import cmds


class indexColors:
    default=0
    black=1
    dark_gray=2
    light_gray=3
    burgundy=4
    dark_blue=5,
    blue=6
    green=7
    dark_purple=8
    pink=9
    brown=10
    dark_brown=11
    dark_red=12
    red=13
    light_green=14
    blue=15
    white=16
    yellow=17
    light_blue=18
    mint=19
    peach=20
    tan=21
    light_yellow=22
    emerald=23
    light_brown=24
    dark_yellow=25
    dark_green=26
    eucalyptus=27
    teal=28
    cobalt=29
    purple=30
    magenta=31


def applyMaterial(objs, mat):
    if isinstance(objs, str):
        objs = [objs]
    mat_set = cmds.listConnections(f'{mat}.outColor', source=False, destination=True)[0]
    shape_nodes = []
    for obj in objs:
        if cmds.nodeType(obj) == 'transform':
            shape_nodes.append(f'{obj}|{cmds.listRelatives(obj, shapes=True)[0]}')
        else:
            shape_nodes.append(obj)
    cmds.sets(shape_nodes, edit=True, forceElement=mat_set)


def createMaterial(name, color):
    material = cmds.shadingNode('lambert', name=name, asShader=True)
    material_set = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{material}SG')
    cmds.connectAttr(f'{material}.outColor', f'{material_set}.surfaceShader', force=True)
    cmds.setAttr(f'{material}.color', color[0], color[1], color[2], type='double3')