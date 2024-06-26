
import bpy
import threading

# function to tag all info areas for redraw
def tag_image_editor_areas_for_redraw(self, context):
    window = context.window
    if window:
        areas = context.window.screen.areas
        for area in areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()

# a variable where we can store the original draw funtion
info_header_draw = lambda s,c: None

# function to hide progress bar
def hide_progress_bar():
    bpy.context.scene.air_progress = -1


# public functions:
def hide_progress_bar_after_delay(seconds = 4):
    timer = threading.Timer(seconds, hide_progress_bar)
    timer.start()


def register():
    # a value between [0, 100] will show the slider
    bpy.types.Scene.air_progress = bpy.props.FloatProperty(
        default=-1,
        subtype='PERCENTAGE',
        precision=0,
        min=-1,
        soft_min=0,
        soft_max=100,
        max=101,
        update=tag_image_editor_areas_for_redraw,
    )

    # progress bar label can be configured
    bpy.types.Scene.air_progress_label = bpy.props.StringProperty(
        default="Progress",
        update=tag_image_editor_areas_for_redraw,
    )

    # add an optional status message before the progress bar
    bpy.types.Scene.air_progress_status_message = bpy.props.StringProperty(
        default="",
        update=tag_image_editor_areas_for_redraw,
    )

    # save the original draw method of the Info header
    global info_header_draw
    info_header_draw = bpy.types.IMAGE_HT_tool_header.draw

    # create a new draw function
    def newdraw(self, context):
        global info_header_draw

        # first call the original stuff
        info_header_draw(self, context)

        # then add the prop that acts as a progress indicator, if progress is in the
        # range [0, 100]
        if (
            context.scene.air_progress >= 0 and
            context.scene.air_progress <= 100
        ):
            self.layout.separator()

            self.layout.label(text=context.scene.air_progress_status_message)
            self.layout.prop(
                context.scene,
                "air_progress",
                text=context.scene.air_progress_label,
                slider=True,
            )

    # replace the draw function
    bpy.types.IMAGE_HT_tool_header.draw = newdraw


def unregister():
    global info_header_draw
    bpy.types.IMAGE_HT_tool_header.draw = info_header_draw

    del bpy.types.Scene.air_progress
    del bpy.types.Scene.air_progress_label
    del bpy.types.Scene.air_progress_status_message