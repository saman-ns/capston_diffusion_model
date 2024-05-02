bl_info = {
    "name": "Style Blender",
    "description": "Create textures and objects using AI",
    "author": "Sami",
    "version": (1, 0, 1),
    "blender": (4, 0, 0),
    "location": "Image Editor -> Sidebar -> Style Blender",
    "warning": "",
    "doc_url": "https://github.com/saman-ns/capston_diffusion_model",
    "category": "Textures",
}

import bpy



def register():
    handlers.register()
    operators.register()
    preferences.register()
    progress_bar.register()
    properties.register()
    task_queue.register()
    ui_panels.register()
    ui_preset_styles.register()


def unregister():
    handlers.unregister()
    operators.unregister()
    preferences.unregister()
    progress_bar.unregister()
    properties.unregister()
    task_queue.unregister()
    ui_panels.unregister()
    ui_preset_styles.unregister()


if __name__ == "__main__":
    register()