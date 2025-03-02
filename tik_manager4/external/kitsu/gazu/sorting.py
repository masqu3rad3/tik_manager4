def sort_by_name(dicts):
    """
    Sorting of a list of dicts. The sorting is based on the name field.

    Args:
        list: The list of dicts to sort.

    Returns:
        Sorted list.
    """
    return sorted(dicts, key=lambda k: k.get("name", "").lower())
