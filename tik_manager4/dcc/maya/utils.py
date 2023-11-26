"""Collection of utility functions for Maya"""
from functools import wraps
from maya import cmds

# decorator to keep the current selection
def keepselection(func):
    """Decorator method to keep the current selection. Useful where
    the wrapped method messes with the current selection"""
    @wraps(func)
    def _keepfunc(*args, **kwargs):
        original_selection = cmds.ls(selection=True)
        component_state = cmds.selectMode(query=True, component=True)
        object_state = cmds.selectMode(query=True, object=True)
        try:
            # start an undo chunk
            return func(*args, **kwargs)
        except Exception as e:
            # log.error(e)
            raise
        finally:
            # after calling the func, end the undo chunk and undo
            cmds.selectMode(object=object_state, component=component_state)
            cmds.select(original_selection)

    return _keepfunc