import maya.cmds as cmds


def direct_connect(source, destination):
    cmds.connectAttr(f'{source}.worldMatrix[0]', f'{destination}.offsetParentMatrix', force=True)