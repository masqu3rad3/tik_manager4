"""Module for FBX file format operations.

Documentation:
https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2023/ENU/Maya-DataExchange/files/GUID-F48E3B78-3E56-4869-9914-CE0FAB6E3116-htm.html
"""

from pathlib import Path
from maya import cmds
from maya import mel

import_settings = {
    "merge_mode": "FBXImportMode -v {}",  # add, merge, exmerge, exmergekeyedxforms
    "smoothing_groups": "FBXProperty Import|IncludeGrp|Geometry|SmoothingGroups -v {}",  # False
    "unlock_normals": "FBXProperty Import|IncludeGrp|Geometry|UnlockNormals -v {}",  # False
    "combine_per_vertex_normals": "FBXProperty Import|IncludeGrp|Geometry|HardEdges -v {}",  # False
    "animation": "FBXProperty Import|IncludeGrp|Animation -v {}",  # True
    # We are not adding animation take here because it needs to declared in the import command directly
    "fill_timeline": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|TimeLine -v {}",  # False
    "bake_animation_layers": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|BakeAnimationLayers -v {}",  # True
    "optical_markers": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Markers -v {}",  # False
    "quaternion_interpolation_mode": 'FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Quaternion -v "{}"',  # 'resample'
    "protect_driven_keys": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|ProtectDrivenKeys -v {}",  # False
    "deform_elements_to_joints": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|DeformNullsAsJoints -v {}",  # True
    "update_pivots_from_nulls": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|NullsToPivot -v {}",  # True
    "geometry_cache": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|PointCache -v {}",  # True
    "deformed_models": "FBXProperty Import|IncludeGrp|Animation|Deformation -v {}",  # True
    "skins": "FBXProperty Import|IncludeGrp|Animation|Deformation|Skins -v {}",  # True
    "blend_shapes": "FBXProperty Import|IncludeGrp|Animation|Deformation|Shape -v {}",  # True
    "pre_normalize_weights": "FBXProperty Import|IncludeGrp|Animation|Deformation|ForceWeightNormalize -v {}",  # False
    "constraints": "FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|Constraint -v {}",  # True
    "skeleton_definition_as": 'FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|CharacterType -v "{}"',  # 'HumanIK'
    "cameras": "FBXProperty Import|IncludeGrp|CameraGrp|Camera -v {}",  # True
    "lights": "FBXProperty Import|IncludeGrp|LightGrp|Light -v {}",  # True
    "audio": "FBXProperty Import|IncludeGrp|Audio -v {}",  # True
    "automatic_scale_factor": "FBXProperty Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion -v {}",  # True
    "file_units_converted_to": 'FBXProperty Import|AdvOptGrp|UnitsGrp|UnitsSelector -v "{}"',  # 'Centimeters'
    "show_warnings_manager": "FBXProperty Import|AdvOptGrp|UI|ShowWarningsManager -v {}",  # False
    "generate_log_data": "FBXProperty Import|AdvOptGrp|UI|GenerateLogData -v {}",  # False
    "remove_bad_polygons": "FBXProperty Import|AdvOptGrp|Performance|RemoveBadPolysFromMesh -v {}",  # True
    "blind_data": "FBXProperty Import|IncludeGrp|Geometry|BlindData -v {}",  # False
    "curve_filter": "FBXProperty Import|IncludeGrp|Animation|CurveFilter -v {}",  # False
    "sampling_rate_selector": 'FBXProperty Import|IncludeGrp|Animation|SamplingPanel|SamplingRateSelector -v "{}"',  # Scene (Scene, File, Custom)
    "curve_filter_sampling_rate": "FBXProperty Import|IncludeGrp|Animation|SamplingPanel|CurveFilterSamplingRate -v {}",  # 24
    "axis_conversion": "FBXProperty Import|AdvOptGrp|AxisConvGrp|AxisConversion -v {}",  # False
    "up_axis": 'FBXProperty Import|AdvOptGrp|AxisConvGrp|UpAxis -v "{}"',  # 'Y'
}

export_settings = {
    "smoothing_groups": "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups -v {}",  # False
    "split_per_vertex_normals": "FBXProperty Export|IncludeGrp|Geometry|expHardEdges -v {}",  # False
    "tangents_and_binormals": "FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals -v {}",  # False
    "smooth_mesh": "FBXProperty Export|IncludeGrp|Geometry|SmoothMesh -v {}",  # True
    "selection_sets": "FBXProperty Export|IncludeGrp|Geometry|SelectionSet -v {}",  # False
    "convert_to_null_objects": "FBXProperty Export|IncludeGrp|PivotToNulls -v {}",  # False
    "preserve_instances": "FBXProperty Export|IncludeGrp|Geometry|Instances -v {}",  # False
    "referenced_assets_content": "FBXProperty Export|IncludeGrp|Geometry|ContainerObjects -v {}",  # True
    "triangulate": "FBXProperty Export|IncludeGrp|Geometry|Triangulate -v {}",  # False
    "convert_nurbs_surface_to": 'FBXProperty Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs -v "{}"',  # 'Nurbs'
    "animation": "FBXProperty Export|IncludeGrp|Animation -v {}",  # True
    "use_scene_name": "FBXProperty Export|IncludeGrp|Animation|ExtraGrp|UseSceneName -v {}",  # False
    "remove_single_key": "FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v {}",  # False
    "quaternion_interpolation_mode": 'FBXProperty Export|IncludeGrp|Animation|ExtraGrp|Quaternion -v "{}"',  # 'Resample'
    "bake_animation": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation -v {}",  # False
    "bake_start": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart -v {}",  # 0
    "bake_end": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd -v {}",  # 200
    "bake_step": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep -v {}",  # 1
    "bake_resample_all": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves -v {}",  # False
    "hide_complex_animation_warning": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|HideComplexAnimationBakedWarning -v {}",  # True
    "deformed_models": "FBXProperty Export|IncludeGrp|Animation|Deformation -v {}",  # True
    "skins": "FBXProperty Export|IncludeGrp|Animation|Deformation|Skins -v {}",  # True
    "blend_shapes": "FBXProperty Export|IncludeGrp|Animation|Deformation|Shape -v {}",  # True
    "shape_attributes": "FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes -v {}",  # False
    "attribute_values": 'FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes|ShapeAttributesValues -v "{}"',  # 'Relative'
    "curve_filters": "FBXProperty Export|IncludeGrp|Animation|CurveFilter -v {}",  # False
    "constant_key_reducer": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed -v {}",  # False
    "translation_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec -v {}",  # 0.0001
    "rotation_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec -v {}",  # 0.0090
    "scaling_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec -v {}",  # 0.0040
    "other_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec -v {}",  # 0.0090
    "auto_tangents_only": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly -v {}",  # True
    "geometry_cache": "FBXProperty Export|IncludeGrp|Animation|PointCache -v {}",  # False
    "geometry_cache_set": 'FBXProperty Export|IncludeGrp|Animation|PointCache|SelectionSetNameAsPointCache -v "{}"',  # " "
    "constraints": "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Constraint -v {}",  # False
    "skeleton_definitions": "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Character -v {}",  # False
    "cameras": "FBXProperty Export|IncludeGrp|CameraGrp|Camera -v {}",  # True
    "lights": "FBXProperty Export|IncludeGrp|LightGrp|Light -v {}",  # True
    "audio": "FBXProperty Export|IncludeGrp|Audio -v {}",  # True
    "embed_media": "FBXProperty Export|IncludeGrp|EmbedTextureGrp|EmbedTexture -v {}",  # False
    "include_children": "FBXProperty Export|IncludeGrp|InputConnectionsGrp|IncludeChildren -v {}",  # True
    "input_connections": "FBXProperty Export|IncludeGrp|InputConnectionsGrp|InputConnections -v {}",  # True
    "automatic_scale_factor": "FBXProperty Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion -v {}",  # True
    "file_units_converted_to": 'FBXProperty Export|AdvOptGrp|UnitsGrp|UnitsSelector -v "{}"',  # 'cm'
    "up_axis": 'FBXProperty Export|AdvOptGrp|AxisConvGrp|UpAxis -v "{}"',  # 'Y'
    "show_warning_manager": "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v {}",  # False
    "generate_log_data": "FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v {}",  # False
    "animation_only": "FBXProperty Export|IncludeGrp|Geometry|AnimationOnly -v {}",  # False
    "blind_data": "FBXProperty Export|IncludeGrp|Geometry|BlindData -v {}",  # True
    "bind_pose": "FBXProperty Export|IncludeGrp|BindPose -v {}",  # True
    "bypass_rss_inheritance": "FBXProperty Export|IncludeGrp|BypassRrsInheritance -v {}",  # False
}


def reset_import_settings():
    """Reset import settings to default"""
    mel.eval("FBXResetImport")


def reset_export_settings():
    """Reset import settings to default"""
    mel.eval("FBXResetExport")


def _format(value):
    """Format value for mel command"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return value


def _set_fbx_import_settings(**kwargs):
    """Build FBX import settings"""
    for key, value in kwargs.items():
        value = _format(value)
        if key in import_settings.keys():
            cmd = import_settings[key].format(value)
            mel.eval(cmd)

def _set_fbx_export_settings(**kwargs):
    """Build FBX export settings"""
    for key, value in kwargs.items():
        value = _format(value)
        if key in export_settings.keys():
            cmd = export_settings[key].format(value)
            mel.eval(cmd)


def _import_fbx(file_path, take=-1):
    """Import FBX file."""
    file_path = file_path.replace("\\", "//")  ## for compatibility with mel syntax.
    import_cmd = 'FBXImport -f "{0}" -t {1};'.format(file_path, take)
    mel.eval(import_cmd)


def _export_fbx(file_path, selected=False):
    """Export FBX file."""
    s_flag = " -s" if selected else ""
    file_path = file_path.replace("\\", "//")  ## for compatibility with mel syntax.
    export_cmd = 'FBXExport -f "{0}"{1};'.format(file_path, s_flag)
    mel.eval(export_cmd)


def load(
    file_path,
    merge_mode="merge",  # add, merge, exmergem, exmergekeyedxforms
    namespace=None,
    smoothing_groups=False,
    unlock_normals=False,
    combine_per_vertex_normals=False,
    animation=True,
    take=-1,
    fill_timeline=False,
    bake_animation_layers=True,
    optical_markers=False,
    quaternion_interpolation_mode="resample",
    protect_driven_keys=False,
    deform_elements_to_joints=True,
    update_pivots_from_nulls=True,
    geometry_cache=True,
    deformed_models=True,
    skins=True,
    blend_shapes=True,
    pre_normalize_weights=False,
    constraints=True,
    skeleton_definition_as="HumanIK",  # 'HumanIK', 'None'
    cameras=True,
    lights=True,
    audio=True,
    automatic_scale_factor=True,
    file_units_converted_to="Centimeters",  # 'Centimeters', 'Meters', 'Inches', 'Feet', 'Yards', 'Miles', 'Millimeters', 'Kilometers'
    show_warnings_manager=False,
    generate_log_data=False,
    remove_bad_polygons=True,
    blind_data=False,
    curve_filter=False,
    sampling_rate_selector="Scene",  # 'Scene' , 'File', 'Custom')
    curve_filter_sampling_rate=24,
    axis_conversion=False,
    up_axis="Y",  # 'Y', 'Z'
):
    """
    Load FBX file.
    Args:
        file_path (str): Path to FBX file
        merge_mode (str): Merge mode.
                                add: Adds the content of the FBX file to the scene.
                                merge: Adds new content and updates animation for existing content.
                                exmerge: updates existing animation and poses. No new content is added.
                                exmergekeyedxforms: only updates keyed animation.
                                Defaults to merge.
        namespace (str): Namespace. If defined, the namespace will be added to the imported objects. defaults to None.
        smoothing_groups (bool): Import smoothing groups. Defaults to False.
        unlock_normals (bool): Unlock normals. Defaults to False.
        combine_per_vertex_normals (bool): Import hard edges. Defaults to False.
        blind_data (bool): Import blind data. Defaults to True.
        animation (bool): Import animation. Defaults to True.
        take (int): Take index. -1 for latest. 0 No animation. Defaults to -1.
        fill_timeline (bool): Fills the scene timeline on import (instead of using the Maya default). Defaults to False.
        bake_animation_layers (bool): Activate Bake animation layers to bake (or Plot) animation layers contained in
                                the incoming file. Defaults to True.
        optical_markers (bool): Import markers. Defaults to False.
        quaternion_interpolation_mode (str): Specifies how to handle quaternion imports. Options are:
                                resample: Resample as Euler interpolation.
                                euler: Set as Euler interpolation.
                                quaternion: Retain quaternion interpolation.
                                Defaults to resample.
        protect_driven_keys (bool): Protect driven keys. Defaults to False.
        deform_elements_to_joints (bool): Activate this option to convert deforming elements into Maya joints.
                                If this option is not active, all elements other than joints being used to deform are
                                converted to locators. Defaults to True.
        update_pivots_from_nulls (bool): Activate this option only when you import older (pre-MotionBuilder 5.5) FBX files that
                                contain an animated joint hierarchy, for example, an animated character. This option
                                lets you assign the rotation transformation of the null (or joints) elements in the
                                hierarchy that are used as pre- and post-rotation to the joint orient and the rotate
                                axis of the original node. The pre-rotation and post-rotation nodes are then deleted.
                                Older files created with the Export Pre/Post Rotation as Nulls option are merged back
                                to the original Maya setup. Defaults to True.
        geometry_cache (bool): Activate this option to import FBX-exported geometry cache data during the FBX import
                                process. Defaults to True.
        deformed_models (bool): Activate this option to import FBX-exported deformation data during the FBX import process.
                                Defaults to True.
        skins (bool): Activate this option to import FBX-exported skin data during the FBX import process.
                                Defaults to True.
        blend_shapes (bool): Activate this option to import all geometry Blend Shapes into your scene. Defaults to True.
        pre_normalize_weights (bool): Activate this option to normalize weight assignment. Defaults to False.
        constraints (bool): Activate this option to import FBX-exported constraint data during the FBX import process.
                                Defaults to True.
        skeleton_definition_as (str): Specifies the character type. Options are:
                                None: No character type.
                                HumanIK: HumanIK character type.
                                Defaults to HumanIK.
        cameras (bool): import FBX-exported camera data during the FBX import process. Defaults to True.
        lights (bool): import FBX-exported light data during the FBX import process. Defaults to True.
        audio (bool): import FBX-exported audio data during the FBX import process. Defaults to True.
        automatic_scale_factor (bool): Activate this option to convert the scale of the incoming FBX file to the
                                current scene's units. Defaults to True.
        file_units_converted_to (str): Specifies the units for the incoming FBX file. Options are:
                                Centimeters: Centimeters.
                                Meters: Meters.
                                Millimeters: Millimeters.
                                Kilometers: Kilometers.
                                Inches: Inches.
                                Feet: Feet.
                                Yards: Yards.
                                Miles: Miles.
                                Defaults to Centimeters.
        axis_conversion (bool): Activate this option to convert the axis of the incoming FBX file to the current scene's
                                axis. Defaults to False.
        up_axis (str): Specifies the up axis for the incoming FBX file. Options are:
                                Y: Y.
                                Z: Z.
        show_warnings_manager (bool): Option to show the warnings manager. Defaults to False.
        generate_log_data (bool): Option to generate log data. Defaults to False.
        remove_bad_polygons (bool): Option to remove bad polygons from mesh. Defaults to True.
        sampling_rate_selector (str): Specifies the sampling rate for animation curves. Options are:
                                Scene: Use the scene's current sampling rate.
                                File: Use the sampling rate specified in the FBX file.
                                Custom: Use the sampling rate specified in the Curve Filter Sampling Rate field.
                                Defaults to Scene.
        curve_filter_sampling_rate (float): Specifies the sampling rate for animation curves. Defaults to 24.0.
        curve_filter (bool): Activate this option to filter animation curves. Defaults to False.


    Returns:
        Imported nodes.

    """
    quaternion_interpolation_mode = {
        "resample": "Resample As Euler Interpolation",
        "euler": "Set As Euler Interpolation",
        "quaternion": "Retain Quaternion Interpolation",
    }.get(quaternion_interpolation_mode, "Resample As Euler Interpolation")
    reset_import_settings()
    if namespace:
        if not cmds.namespace(exists=namespace):
            cmds.namespace(addNamespace=namespace)
        cmds.namespace(setNamespace=namespace)

    _set_fbx_import_settings(**locals())

    # file_path = file_path.replace("\\", "//")  ## for compatibility with mel syntax.
    # import_cmd = ('FBXImport -f "{0}" -t {1};'.format(file_path, take))
    # grab a list of nodes before importing
    nodes_before = cmds.ls()
    _import_fbx(file_path, take=take)
    if namespace:
        cmds.namespace(setNamespace=":")
    # mel.eval(import_cmd)
    # grab a list of nodes after importing
    nodes_after = cmds.ls()
    # get the difference between the two lists
    imported_nodes = list(set(nodes_after) - set(nodes_before))
    return imported_nodes


def save(
    file_path,
    force=False,
    selection_only=False,
    smoothing_groups=False,
    split_per_vertex_normals=False,
    tangents_and_binormals=False,
    smooth_mesh=True,
    selection_sets=False,
    convert_to_null_objects=False,
    preserve_instances=False,
    referenced_assets_content=True,
    triangulate=False,
    convert_nurbs_surface_to="nurbs",
    animation=True,
    use_scene_name=False,
    remove_single_key=False,
    quaternion_interpolation_mode="resample",
    bake_animation=False,
    bake_start=0,
    bake_end=200,
    bake_step=1,
    bake_resample_all=False,
    hide_complex_animation_warning=True,
    deformed_models=True,
    skins=True,
    blend_shapes=True,
    shape_attributes=False,
    attribute_values="Relative",  # Relative, Absolute
    curve_filters=False,
    constant_key_reducer=False,
    translation_precision=0.0001,
    rotation_precision=0.009,
    scaling_precision=0.004,
    other_precision=0.009,
    auto_tangents_only=True,
    geometry_cache=False,
    geometry_cache_set=" ",
    constraints=False,
    skeleton_definitions=False,
    cameras=True,
    lights=True,
    audio=True,
    embed_media=False,
    include_children=True,
    input_connections=True,
    automatic_scale_factor=True,
    file_units_converted_to="Centimeters",  # Centimeters, Meters, Millimeters, Kilometers, Inches, Feet, Yards, Miles
    up_axis="Y",  # Y, Z
    show_warning_manager=False,
    generate_log_data=False,
    animation_only=False,
    blind_data=True,
    bind_pose=True,
    bypass_rss_inheritance=False,
):
    """
    Save the current scene to a FBX file.
    Args:
        file_path (str): The path to the FBX file to save.
        force (bool): Force save. Defaults to False.
        selection_only (bool): Export only the selected objects. Defaults to False.
        smoothing_groups (bool): Export smoothing groups. Defaults to False.
        split_per_vertex_normals (bool): Split per vertex normals. Defaults to False.
        tangents_and_binormals (bool): Export tangents and binormals. Defaults to False.
        smooth_mesh (bool): Smooth mesh. Defaults to True.
        selection_sets (bool): Export selection sets. Defaults to False.
        convert_to_null_objects (bool): Convert to null objects. Defaults to False.
        preserve_instances (bool): Preserve instances. Defaults to False.
        referenced_assets_content (bool): Export referenced assets content. Defaults to True.
        triangulate (bool): Triangulate. Defaults to False.
        convert_nurbs_surface_to (str): Convert NURBS surface to. Options are:
                                "nurbs": "NURBS".
                                "display": "Interactive Display Mesh".
                                "render": "Software Render Mesh".
                                Defaults to "nurbs".
        animation (bool): Export animation. Defaults to True.
        use_scene_name (bool): Use scene name. Defaults to False.
        remove_single_key (bool): Remove single key. Defaults to False.
        quaternion_interpolation_mode (str): Specifies the interpolation mode for quaternion curves. Options are:
                                "resample": "Resample As Euler Interpolation".
                                "euler": "Set As Euler Interpolation".
                                "quaternion": "Retain Quaternion Interpolation".
                                Defaults to "resample".
        bake_animation (bool): Bake animation. Defaults to False.
        bake_start (int): Specifies the start frame for baking animation. Defaults to 0.
        bake_end (int): Specifies the end frame for baking animation. Defaults to 200.
        bake_step (int): Specifies the step frame for baking animation. Defaults to 1.
        bake_resample_all (bool): Resample all. Defaults to False.
        hide_complex_animation_warning (bool): Hide complex animation warning. Defaults to True.
        deformed_models (bool): Export deformed models. Defaults to True.
        skins (bool): Export skins. Defaults to True.
        blend_shapes (bool): Export blend shapes. Defaults to True.
        shape_attributes (bool): Export shape attributes. Defaults to False.
        attribute_values (str): Specifies the attribute values to export. Options are:
                                "Relative": "Relative".
                                "Absolute": "Absolute".
                                Defaults to "Relative".
        curve_filters (bool): Export curve filters. Defaults to False.
        constant_key_reducer (bool): Export constant key reducer. Defaults to False.
        translation_precision (float): Specifies the translation precision. Defaults to 0.0001.
        rotation_precision (float): Specifies the rotation precision. Defaults to 0.009.
        scaling_precision (float): Specifies the scaling precision. Defaults to 0.004.
        other_precision (float): Specifies the other precision. Defaults to 0.009.
        auto_tangents_only (bool): Export auto tangents only. Defaults to True.
        geometry_cache (bool): Export geometry cache. Defaults to False.
        geometry_cache_set (str): Specifies the geometry cache set. Defaults to " ".
        constraints (bool): Export constraints. Defaults to False.
        skeleton_definitions (bool): Export skeleton definitions. Defaults to False.
        cameras (bool): Export cameras. Defaults to True.
        lights (bool): Export lights. Defaults to True.
        audio (bool): Export audio. Defaults to True.
        embed_media (bool): Embed media. Defaults to False.
        include_children (bool): Include children. Defaults to True.
        input_connections (bool): Export input connections. Defaults to True.
        automatic_scale_factor (bool): Automatic scale factor. Defaults to True.
        file_units_converted_to (str): Specifies the file units converted to. Options are:
                                "Centimeters": "Centimeters".
                                "Meters": "Meters".
                                "Millimeters": "Millimeters".
                                "Kilometers": "Kilometers".
                                "Inches": "Inches".
                                "Feet": "Feet".
                                "Yards": "Yards".
                                "Miles": "Miles".
                                Defaults to "Centimeters".
        up_axis (str): Specifies the up axis. Options are:
                                "Y": "Y".
                                "Z": "Z".
                                Defaults to "Y".
        show_warning_manager (bool): Show warning manager. Defaults to False.
        generate_log_data (bool): Generate log data. Defaults to False.
        animation_only (bool): Export animation only. Defaults to False.
        blind_data (bool): Export blind data. Defaults to True.
        bind_pose (bool): Export bind pose. Defaults to True.
        bypass_rss_inheritance (bool): Bypass RSS inheritance. Defaults to False.

    Returns:
        (str) FBX file path

    """
    # check if the file exists
    if Path(file_path).exists() and not force:
        raise RuntimeError("File already exists: {}".format(file_path))
    convert_nurbs_surface_to = {
        "nurbs": "NURBS",
        "display": "Interactive Display Mesh",
        "render": "Software Render Mesh",
    }.get(convert_nurbs_surface_to, "NURBS")

    quaternion_interpolation_mode = {
        "resample": "Resample As Euler Interpolation",
        "euler": "Set As Euler Interpolation",
        "quaternion": "Retain Quaternion Interpolation",
    }.get(quaternion_interpolation_mode, "Resample As Euler Interpolation")

    reset_export_settings()
    # create a copy of the locals() dictionary
    settings_dict = locals().copy()
    # remove the selection_only argument
    settings_dict.pop("selection_only")
    settings_dict.pop("force")

    _set_fbx_export_settings(**settings_dict)

    _export_fbx(file_path, selected=selection_only)
    return file_path


#############################################################################
# Output of FBXProperties mel command
#############################################################################
# PATH: Import|PlugInGrp|PlugInUIWidth    ( TYPE: Integer ) ( VALUE: 500 )
# PATH: Import|PlugInGrp|PlugInUIHeight    ( TYPE: Integer ) ( VALUE: 500 )
# PATH: Import|PlugInGrp|PlugInUIXpos    ( TYPE: Integer ) ( VALUE: 100 )
# PATH: Import|PlugInGrp|PlugInUIYpos    ( TYPE: Integer ) ( VALUE: 100 )
# PATH: Import|PlugInGrp|UILIndex    ( TYPE: Enum )  ( VALUE: "ENU" )  (POSSIBLE VALUES: "ENU" "DEU" "FRA" "JPN" "KOR" "CHS" "PTB"  )
# PATH: Import|IncludeGrp|MergeMode    ( TYPE: Enum )  ( VALUE: "Update animation" )  (POSSIBLE VALUES: "Add" "Add and update animation" "Update animation" "Update animation (keyed transforms)"  )
# PATH: Import|IncludeGrp|Geometry|SmoothingGroups    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Geometry|UnlockNormals    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Geometry|HardEdges    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Geometry|BlindData    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|Take    ( TYPE: Enum )  ( VALUE: "No Animation" )  (POSSIBLE VALUES: "No Animation"  )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|TimeLine    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|BakeAnimationLayers    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|Markers    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|Quaternion    ( TYPE: Enum )  ( VALUE: "Resample As Euler Interpolation" )  (POSSIBLE VALUES: "Retain Quaternion Interpolation" "Set As Euler Interpolation" "Resample As Euler Interpolation"  )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|ProtectDrivenKeys    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|DeformNullsAsJoints    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|NullsToPivot    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|ExtraGrp|PointCache    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|Deformation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|Deformation|Skins    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|Deformation|Shape    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|Deformation|ForceWeightNormalize    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Animation|SamplingPanel|SamplingRateSelector    ( TYPE: Enum )  ( VALUE: "Scene" )  (POSSIBLE VALUES: "Scene" "File" "Custom"  )
# PATH: Import|IncludeGrp|Animation|SamplingPanel|CurveFilterSamplingRate    ( TYPE: Number ) ( VALUE: 24.000000 )
# PATH: Import|IncludeGrp|Animation|CurveFilter    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|IncludeGrp|Animation|ConstraintsGrp|Constraint    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Animation|ConstraintsGrp|CharacterType    ( TYPE: Enum )  ( VALUE: "HumanIK" )  (POSSIBLE VALUES: "None" "HumanIK"  )
# PATH: Import|IncludeGrp|CameraGrp|Camera    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|LightGrp|Light    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|IncludeGrp|Audio    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|UnitsGrp|UnitsSelector    ( TYPE: Enum )  ( VALUE: "Centimeters" )  (POSSIBLE VALUES: "Millimeters" "Centimeters" "Decimeters" "Meters" "Kilometers" "Inches" "Feet" "Yards" "Miles"  )
# PATH: Import|AdvOptGrp|AxisConvGrp|AxisConversion    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|AdvOptGrp|AxisConvGrp|UpAxis    ( TYPE: Enum )  ( VALUE: "Y" )  (POSSIBLE VALUES: "Y" "Z"  )
# PATH: Import|AdvOptGrp|UI|ShowWarningsManager    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|AdvOptGrp|UI|GenerateLogData    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Import|AdvOptGrp|FileFormat|Obj|ReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|ReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Texture    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Material    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Animation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Mesh    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Light    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Camera    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|AmbientLight    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Rescaling    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Filter    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Max_3ds|Smoothgroup    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionFrameCount    ( TYPE: Integer ) ( VALUE: 0 )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionFrameRate    ( TYPE: Number ) ( VALUE: 0.000000 )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionActorPrefix    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionRenameDuplicateNames    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionExactZeroAsOccluded    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionSetOccludedToLastValidPos    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionAsOpticalSegments    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionASFSceneOwned    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Motion_Base|MotionUpAxisUsedInFile    ( TYPE: Integer ) ( VALUE: 3 )
# PATH: Import|AdvOptGrp|FileFormat|Biovision_BVH|MotionCreateReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|MotionAnalysis_HTR|MotionCreateReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|MotionAnalysis_HTR|MotionBaseTInOffset    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|MotionAnalysis_HTR|MotionBaseRInPrerotation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_ASF|MotionCreateReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_ASF|MotionDummyNodes    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_ASF|MotionLimits    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_ASF|MotionBaseTInOffset    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_ASF|MotionBaseRInPrerotation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_AMC|MotionCreateReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_AMC|MotionDummyNodes    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_AMC|MotionLimits    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_AMC|MotionBaseTInOffset    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|FileFormat|Acclaim_AMC|MotionBaseRInPrerotation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|Dxf|WeldVertices    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|Dxf|ObjectDerivation    ( TYPE: Enum )  ( VALUE: "By layer" )  (POSSIBLE VALUES: "By layer" "By entity" "By block"  )
# PATH: Import|AdvOptGrp|Dxf|ReferenceNode    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Import|AdvOptGrp|Performance|RemoveBadPolysFromMesh    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|PlugInGrp|PlugInUIWidth    ( TYPE: Integer ) ( VALUE: 500 )
# PATH: Export|PlugInGrp|PlugInUIHeight    ( TYPE: Integer ) ( VALUE: 500 )
# PATH: Export|PlugInGrp|PlugInUIXpos    ( TYPE: Integer ) ( VALUE: 100 )
# PATH: Export|PlugInGrp|PlugInUIYpos    ( TYPE: Integer ) ( VALUE: 100 )
# PATH: Export|PlugInGrp|UILIndex    ( TYPE: Enum )  ( VALUE: "ENU" )  (POSSIBLE VALUES: "ENU" "DEU" "FRA" "JPN" "KOR" "CHS" "PTB"  )
# PATH: Export|IncludeGrp|Geometry|SmoothingGroups    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|expHardEdges    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|TangentsandBinormals    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|SmoothMesh    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Geometry|SelectionSet    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|BlindData    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Geometry|AnimationOnly    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|Instances    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|ContainerObjects    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Geometry|Triangulate    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs    ( TYPE: Enum )  ( VALUE: "NURBS" )  (POSSIBLE VALUES: "NURBS" "Interactive Display Mesh" "Software Render Mesh"  )
# PATH: Export|IncludeGrp|Animation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Animation|ExtraGrp|UseSceneName    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|ExtraGrp|Quaternion    ( TYPE: Enum )  ( VALUE: "Resample As Euler Interpolation" )  (POSSIBLE VALUES: "Retain Quaternion Interpolation" "Set As Euler Interpolation" "Resample As Euler Interpolation"  )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart    ( TYPE: Integer ) ( VALUE: 0 )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd    ( TYPE: Integer ) ( VALUE: 200 )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep    ( TYPE: Integer ) ( VALUE: 1 )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|BakeComplexAnimation|HideComplexAnimationBakedWarning    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|Deformation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Animation|Deformation|Skins    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Animation|Deformation|Shape    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Animation|Deformation|ShapeAttributes    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|Deformation|ShapeAttributes|ShapeAttributesValues    ( TYPE: Enum )  ( VALUE: "Relative" )  (POSSIBLE VALUES: "Relative" "Absolute"  )
# PATH: Export|IncludeGrp|Animation|CurveFilter    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec    ( TYPE: Number ) ( VALUE: 0.000100 )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec    ( TYPE: Number ) ( VALUE: 0.009000 )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec    ( TYPE: Number ) ( VALUE: 0.004000 )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec    ( TYPE: Number ) ( VALUE: 0.009000 )
# PATH: Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Animation|PointCache    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|PointCache|SelectionSetNameAsPointCache    ( TYPE: Enum )  ( VALUE: " " )  (POSSIBLE VALUES: " " "defaultLightSet" "defaultObjectSet"  )
# PATH: Export|IncludeGrp|Animation|ConstraintsGrp|Constraint    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|Animation|ConstraintsGrp|Character    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|CameraGrp|Camera    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|LightGrp|Light    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|Audio    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|EmbedTextureGrp|EmbedTexture    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|BindPose    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|PivotToNulls    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|BypassRrsInheritance    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|IncludeGrp|InputConnectionsGrp|IncludeChildren    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|IncludeGrp|InputConnectionsGrp|InputConnections    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|UnitsGrp|UnitsSelector    ( TYPE: Enum )  ( VALUE: "Centimeters" )  (POSSIBLE VALUES: "Millimeters" "Centimeters" "Decimeters" "Meters" "Kilometers" "Inches" "Feet" "Yards" "Miles"  )
# PATH: Export|AdvOptGrp|AxisConvGrp|UpAxis    ( TYPE: Enum )  ( VALUE: "Y" )  (POSSIBLE VALUES: "Y" "Z"  )
# PATH: Export|AdvOptGrp|UI|ShowWarningsManager    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|UI|GenerateLogData    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Obj|Triangulate    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Obj|Deformation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionFrameCount    ( TYPE: Integer ) ( VALUE: 0 )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionFromGlobalPosition    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionFrameRate    ( TYPE: Number ) ( VALUE: 30.000000 )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionGapsAsValidData    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionC3DRealFormat    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|AdvOptGrp|FileFormat|Motion_Base|MotionASFSceneOwned    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Biovision_BVH|MotionTranslation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionTranslation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionFrameRateUsed    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionFrameRange    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionWriteDefaultAsBaseTR    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionTranslation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionFrameRateUsed    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionFrameRange    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionWriteDefaultAsBaseTR    ( TYPE: Bool ) ( VALUE: "false" )
# PATH: Export|AdvOptGrp|Fbx|AsciiFbx    ( TYPE: Enum )  ( VALUE: "Binary" )  (POSSIBLE VALUES: "Binary" "ASCII"  )
# PATH: Export|AdvOptGrp|Fbx|ExportFileVersion    ( TYPE: Alias )  ( VALUE: "FBX202000" )  (POSSIBLE VALUES: "FBX202000" "FBX201900" "FBX201800" "FBX201600" "FBX201400" "FBX201300" "FBX201200" "FBX201100" "FBX201000" "FBX200900" "FBX200611"  )
# PATH: Export|AdvOptGrp|Dxf|Deformation    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|Dxf|Triangulate    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|Collada|Triangulate    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|Collada|SingleMatrix    ( TYPE: Bool ) ( VALUE: "true" )
# PATH: Export|AdvOptGrp|Collada|FrameRate    ( TYPE: Number ) ( VALUE: 24.000000 )
