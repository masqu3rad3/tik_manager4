import re
from pathlib import Path

from krita import Krita


def export_selected_vector_layer_to_svg(file_path: str) -> bool:
    """
    Export the currently selected vector layer in the active Krita document to an SVG file.

    Args:
        file_path (str): Destination file path for the SVG.

    Returns:
        bool: True if export succeeds.

    Raises:
        RuntimeError: If there is no active document or layer.
        TypeError: If the selected node is not a vector layer.
    """
    doc = Krita.instance().activeDocument()
    if doc is None:
        raise RuntimeError("No active document found.")
    node = doc.activeNode()
    if node is None:
        raise RuntimeError("No active layer selected.")
    if node.type() != "vectorlayer":
        raise TypeError("Selected layer is not a vector layer.")

    try:
        svg_data = node.toSvg()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_data)
    except Exception as e:
        raise RuntimeError(f"Failed to export vector layer to SVG: {e}") from e

    return True


def export_merged_visible_layers(file_path: str) -> bool:
    """Export all visible vector layers from the active Krita document as a merged SVG file.

    Recursively traverses all layer groups, collects the inner SVG content of every
    visible vector layer, and writes a single well-formed SVG file sized to the document
    canvas dimensions.

    Args:
        file_path: Destination path for the exported ``.svg`` file.
    Returns:
        True if the file was written successfully.
    Raises:
        ValueError: If no visible vector layers are found in the document.
    """
    doc = Krita.instance().activeDocument()

    all_svg_contents = []

    def gather_layers(nodes):
        """Recursively collect inner SVG content from all visible vector layers.

        Args:
            nodes: List of Krita nodes to inspect.
        """
        for node in nodes:
            if node.type() == "grouplayer":
                gather_layers(node.childNodes())
            elif node.type() == "vectorlayer" and node.visible():
                svg_raw = node.toSvg()
                inner_content = re.search(r'<svg[^>]*>(.*?)</svg>', svg_raw,
                                          re.DOTALL)
                if inner_content:
                    all_svg_contents.append(inner_content.group(1))

    gather_layers(doc.topLevelNodes())

    if not all_svg_contents:
        raise ValueError("No visible vector layers found.")

    # Wrap collected content in a single SVG envelope sized to the document canvas
    width = doc.width()
    height = doc.height()
    merged_svg = (
            f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"'
            f' xmlns="http://www.w3.org/2000/svg">\n'
            + "\n".join(all_svg_contents)
            + "\n</svg>"
    )
    Path(file_path).write_text(merged_svg, encoding="utf-8")
    return True


def open_image_file(file_path: str) -> None:
    """Open an image file in Krita."""
    application = Krita.instance()
    existing_docs = application.documents()
    for doc in existing_docs:
        if file_path == doc.fileName():
            doc.close()
    doc = application.openDocument(file_path)
    application.activeWindow().addView(doc)
