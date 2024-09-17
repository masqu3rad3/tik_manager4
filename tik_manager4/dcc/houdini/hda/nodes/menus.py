def extract_names(node, key):
    """Extract names from the node's userData based on the given key."""
    _list = []
    raw_names = node.userData(key)
    if not raw_names:
        return _list
    for name in raw_names.split(";"):
        _list.append(name)
        _list.append(name)
    return _list

def task_parm(kwargs):
    return extract_names(kwargs.get("node"), "tasks")

def category_parm(kwargs):
    return extract_names(kwargs.get("node"), "categories")

def published_work_parm(kwargs):
    return extract_names(kwargs.get("node"), "published_works")

def version_parm(kwargs):
    return extract_names(kwargs.get("node"), "versions")

def element_parm(kwargs):
    return extract_names(kwargs.get("node"), "elements")