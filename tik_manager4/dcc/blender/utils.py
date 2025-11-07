""" This module contains utility functions for Blender. """

from functools import wraps
import traceback
import bpy

def keep_scene_settings(func):
    """Decorator method to keep the current render settings."""
    @wraps(func)
    def _keepfunc(*args, **kwargs):
        resolution_x = bpy.context.scene.render.resolution_x
        resolution_y = bpy.context.scene.render.resolution_y
        resolution_percentage = bpy.context.scene.render.resolution_percentage
        pixel_aspect_x = bpy.context.scene.render.pixel_aspect_x
        pixel_aspect_y = bpy.context.scene.render.pixel_aspect_y
        use_border = bpy.context.scene.render.use_border
        use_crop_to_border = bpy.context.scene.render.use_crop_to_border
        fps = bpy.context.scene.render.fps

        ranges = get_ranges()
        step = bpy.context.scene.frame_step
        frame_map_old = bpy.context.scene.render.frame_map_old
        frame_map_new = bpy.context.scene.render.frame_map_new

        use_multiview = bpy.context.scene.render.use_multiview
        views_format = bpy.context.scene.render.views_format

        filepath = bpy.context.scene.render.filepath
        use_file_extension = bpy.context.scene.render.use_file_extension
        use_render_cache = bpy.context.scene.render.use_render_cache
        file_format = bpy.context.scene.render.image_settings.file_format
        color_mode = bpy.context.scene.render.image_settings.color_mode

        color_management = bpy.context.scene.render.image_settings.color_management
        display_device = bpy.context.scene.display_settings.display_device
        view_transform = bpy.context.scene.view_settings.view_transform
        look = bpy.context.scene.view_settings.look
        exposure = bpy.context.scene.view_settings.exposure
        gamma = bpy.context.scene.view_settings.gamma
        use_curve_mapping = bpy.context.scene.view_settings.use_curve_mapping

        ffmpeg_format = bpy.context.scene.render.ffmpeg.format
        use_autosplit = bpy.context.scene.render.ffmpeg.use_autosplit
        ffmpeg_codec = bpy.context.scene.render.ffmpeg.codec
        constant_rate_factor = bpy.context.scene.render.ffmpeg.constant_rate_factor
        ffmpeg_preset = bpy.context.scene.render.ffmpeg.ffmpeg_preset

        audio_codec = bpy.context.scene.render.ffmpeg.audio_codec

        # metadata
        metadata_input = bpy.context.scene.render.metadata_input
        use_stamp_date = bpy.context.scene.render.use_stamp_date
        use_stamp_time = bpy.context.scene.render.use_stamp_time
        use_stamp_render_time = bpy.context.scene.render.use_stamp_render_time
        use_stamp_frame = bpy.context.scene.render.use_stamp_frame
        use_stamp_frame_range = bpy.context.scene.render.use_stamp_frame_range
        use_stamp_memory = bpy.context.scene.render.use_stamp_memory
        use_stamp_hostname = bpy.context.scene.render.use_stamp_hostname
        use_stamp_camera = bpy.context.scene.render.use_stamp_camera
        use_stamp_lens = bpy.context.scene.render.use_stamp_lens
        use_stamp_scene = bpy.context.scene.render.use_stamp_scene
        use_stamp_marker = bpy.context.scene.render.use_stamp_marker
        use_stamp_filename = bpy.context.scene.render.use_stamp_filename
        use_stamp_sequencer_strip = bpy.context.scene.render.use_stamp_sequencer_strip
        use_stamp_note = bpy.context.scene.render.use_stamp_note
        stamp_note_text = bpy.context.scene.render.stamp_note_text
        use_stamp = bpy.context.scene.render.use_stamp # burn it inot the image

        try:
            return func(*args, **kwargs)
        except Exception as e:
            # traceback.print_exc(e)
            raise e
        finally:
            bpy.context.scene.render.resolution_x = resolution_x
            bpy.context.scene.render.resolution_y = resolution_y
            bpy.context.scene.render.resolution_percentage = resolution_percentage
            bpy.context.scene.render.pixel_aspect_x = pixel_aspect_x
            bpy.context.scene.render.pixel_aspect_y = pixel_aspect_y
            bpy.context.scene.render.use_border = use_border
            bpy.context.scene.render.use_crop_to_border = use_crop_to_border
            bpy.context.scene.render.fps = fps

            bpy.context.scene.render.use_multiview = use_multiview
            bpy.context.scene.render.views_format = views_format

            set_ranges(ranges)
            bpy.context.scene.frame_step = step
            bpy.context.scene.render.frame_map_old = frame_map_old
            bpy.context.scene.render.frame_map_new = frame_map_new

            bpy.context.scene.render.filepath = filepath
            bpy.context.scene.render.use_file_extension = use_file_extension
            bpy.context.scene.render.use_render_cache = use_render_cache
            bpy.context.scene.render.image_settings.file_format = file_format
            bpy.context.scene.render.image_settings.color_mode = color_mode

            bpy.context.scene.render.image_settings.color_management = color_management
            bpy.context.scene.display_settings.display_device = display_device
            bpy.context.scene.view_settings.view_transform = view_transform
            bpy.context.scene.view_settings.look = look
            bpy.context.scene.view_settings.exposure = exposure
            bpy.context.scene.view_settings.gamma = gamma
            bpy.context.scene.view_settings.use_curve_mapping = use_curve_mapping

            bpy.context.scene.render.ffmpeg.format = ffmpeg_format
            bpy.context.scene.render.ffmpeg.use_autosplit = use_autosplit
            bpy.context.scene.render.ffmpeg.codec = ffmpeg_codec
            bpy.context.scene.render.ffmpeg.constant_rate_factor = constant_rate_factor
            bpy.context.scene.render.ffmpeg.ffmpeg_preset = ffmpeg_preset

            bpy.context.scene.render.ffmpeg.audio_codec = audio_codec

            bpy.context.scene.render.metadata_input = metadata_input
            bpy.context.scene.render.use_stamp_date = use_stamp_date
            bpy.context.scene.render.use_stamp_time = use_stamp_time
            bpy.context.scene.render.use_stamp_render_time = use_stamp_render_time
            bpy.context.scene.render.use_stamp_frame = use_stamp_frame
            bpy.context.scene.render.use_stamp_frame_range = use_stamp_frame_range
            bpy.context.scene.render.use_stamp_memory = use_stamp_memory
            bpy.context.scene.render.use_stamp_hostname = use_stamp_hostname
            bpy.context.scene.render.use_stamp_camera = use_stamp_camera
            bpy.context.scene.render.use_stamp_lens = use_stamp_lens
            bpy.context.scene.render.use_stamp_scene = use_stamp_scene
            bpy.context.scene.render.use_stamp_marker = use_stamp_marker
            bpy.context.scene.render.use_stamp_filename = use_stamp_filename
            bpy.context.scene.render.use_stamp_sequencer_strip = use_stamp_sequencer_strip
            bpy.context.scene.render.use_stamp_note = use_stamp_note
            bpy.context.scene.render.stamp_note_text = stamp_note_text
            bpy.context.scene.render.use_stamp = use_stamp

    return _keepfunc


def get_ranges():
    """Get the frame range."""
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end
    return [start, start, end, end]

def set_ranges(range_list):
    """Set the frame range."""
    bpy.context.scene.frame_start = range_list[0]
    bpy.context.scene.frame_end = range_list[-1]

def get_scene_fps():
    """Return the scene FPS."""
    return bpy.context.scene.render.fps

def set_scene_fps(fps_value):
    """Set the scene FPS."""
    bpy.context.scene.render.fps = fps_value

def get_override_context(context=None):
    context = bpy.context.copy()

    for window in bpy.context.window_manager.windows:
        context["window"] = window
        screen = window.screen
        context["screen"] = screen

        if context:
            for area in screen.areas:
                if area.type == "VIEW_3D" or area.type == "IMAGE_EDITOR":
                    context["area"] = area
                    for region in area.regions:
                        if region.type == "WINDOW":
                            context["region"] = region
                            return context

        for area in screen.areas:
            if area.type == "VIEW_3D":
                context["area"] = area
                return context

        for area in screen.areas:
            if area.type == "IMAGE_EDITOR":
                context["area"] = area
                return context

    return context

def get_usd_export_kwargs(
        file_path,
        animation=False,
        uvmaps=True,
        hair=True,
        materials=True,
        mesh_colors=True,
        textures=True,
        convert_orientation=True,
        global_up_selection='Y'
):
    """Generates arguments settings for exporting a USD file.

        Includes options for exporting materials, textures, UV maps,
        animation, hair, mesh colors.
        Adds extra settings for Blender version 4.2 or newer.

        Args:
            file_path (str): File path to write USD file
            animation (bool): Export animated data
            uvmaps (bool): Export UVs
            hair (bool): Export hair particle systems as curves
            materials (bool): Export material data
            mesh_colors (bool): Export color attributes
            textures (bool): Reference external texture files in generated USD
            convert_orientation (bool): Transform scene from Blender coordinate system to USD
            global_up_selection (str): Which axis in Blender will map to +Y in USD (+Y, +Z, -Y, -Z)

        Returns:
            dict: A dictionary of export options.
    """
    kwargs = {
        'filepath': file_path,
        'export_animation': animation,
        'export_uvmaps': uvmaps,
        'export_hair': hair,
        'export_materials': materials,
        'export_mesh_colors': mesh_colors,
        'export_textures': textures
    }

    # Additional export options available in Blender 4.2 LTS and later
    # These options improve orientation handling and global axis alignment
    if bpy.app.version >= (4, 2, 0):
        kwargs.update({
            'convert_orientation': convert_orientation,
            'export_global_up_selection': global_up_selection
        })

    return kwargs