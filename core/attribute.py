import maya.cmds as cmds


def lockAttributes(
    node: str,
    attributes: list[str]=["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
):
    """
    Lock attributes of a node. Default: Translate, Rotate, Scale, Visibility.
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', lock=True)


def unlockAttributes(
    node,
    attributes=["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"],
):
    """
    Unlock attributes of a node. Default: Translate, Rotate, Scale, Visibility.
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', lock=False)


def hideAttributes(
        node,
        attributes = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
):
    """
    Hide attributes of a node. Default: Translate, Rotate, Scale, Visibility.
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', keyable=False, channelBox=False)


def showAttributes(
        node,
        attributes = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
):
    """
    Show attributes of a node. Default: Translate, Rotate, Scale, Visibility.
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', channelBox=True)


def lockAndHideAttributes(
        node,
        attributes = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
):
    """
    Lock and hide attributes of a node. Default: Translate, Rotate, Scale, Visibility.
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', lock=True, keyable=False, channelBox=False)



def setKeyableAttributes(
    node: str, attributes: list[str]=["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
):
    """
    Set keyable attributes of a node. Default: Translate, Rotate, Scale, Visibility
    """

    local_attrs = ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz", "v",]

    for attr in local_attrs:
        cmds.setAttr(f'{node}.{attr}', lock=False, keyable=True)


def setNotKeyableAttributes(
        node: str, attributes: list[str]=["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
):
    """
    Set non keyable attributes of a node. Default: Translate, Rotate, Scale, Visibility
    """
    for attr in attributes:
        cmds.setAttr(f'{node}.{attr}', keyable=False, channelBox=True)
