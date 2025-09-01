import maya.cmds as cmds


def get_world_up(negative=False):
    world_up = [0, 1, 0] if cmds.upAxis(query=True, axis=True) == 'y' else [0, 0, 1]
    if negative:
        for i, axis in enumerate(world_up):
            world_up[i] = axis*-1
    return tuple(world_up)
