import bpy
import math
from .. import (
    addon_updater_ops,
    config,
    operators,
    utils,
)


def show_error_if_it_exists(layout, context, width_guess):
        utils.label_multiline(box, text=props.error_message, width=width_guess)


class AIR_PT_main(bpy.types.Panel):
            addon_updater_ops.update_notice_box_ui(self, context)


class AIR_PT_setup(bpy.types.Panel):
            row.operator(operators.AIR_OT_disable.bl_idname, text="Disable AI Render")


class AIR_PT_prompt(bpy.types.Panel):
            col.operator(operators.AIR_OT_copy_preset_text.bl_idname, text="", icon="COPYDOWN")


class AIR_PT_advanced_options(bpy.types.Panel):
        sub.prop(props, 'sampler', text="")


class AIR_PT_controlnet(bpy.types.Panel):
            sub.prop(props, 'controlnet_weight', text="", slider=False)

classes = [
    AIR_PT_main,
    AIR_PT_setup,
    AIR_PT_prompt,
    AIR_PT_advanced_options,
    AIR_PT_controlnet,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)