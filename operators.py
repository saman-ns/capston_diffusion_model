import bpy
import functools
import math
import random
import re
import time


from . import (
    analytics,
    config,
    progress_bar,
    task_queue,
    utils,
)


# from .sd_backends import automatic1111_api


# example_dimensions_tuple_list = utils.generate_example_dimensions_tuple_list()
# sdxl_1024_dimensions_tuple_list = utils.generate_sdxl_1024_dimensions_tuple_list()


def enable_air(scene):
    # register the task queue (this also needs to be done post-load,
    # because app timers get stopped when loading a new blender file)
    task_queue.register()

    # clear any possible past errors in the file (this would happen if ai render
    # was enabled in a file that we just opened, and it had been saved with
    # an error from a past render)
    clear_error(scene)


def mute_legacy_compositor_node_group(scene):
    if scene.node_tree and scene.node_tree.nodes:
        legacy_node_group = scene.node_tree.nodes.get('AIR')
        if legacy_node_group:
            legacy_node_group.mute = True

def set_image_dimensions(context, width, height):
    context.scene.render.resolution_x = width
    context.scene.render.resolution_y = height
    context.scene.render.resolution_percentage = 100

    clear_error(context.scene)
    
    
def handle_error(msg, error_key = ''):
    """Show an error popup, and set the error message to be displayed in the ui"""
    print("AI Render Error:", msg)
    task_queue.add(functools.partial(bpy.ops.ai_render.show_error_popup, 'INVOKE_DEFAULT', error_message=msg, error_key=error_key))
    analytics.track_event('ai_render_error', value=error_key)
    return False    

def set_silent_error(scene, msg, error_key = ''):
    """Set the error message to be displayed in the ui, but don't show a popup"""
    print("AI Render Error:", msg)
    scene.air_props.error_message = msg
    scene.air_props.error_key = error_key


def clear_error(scene):
    """Clear the error message in the ui"""
    scene.air_props.error_message = ''
    scene.air_props.error_key = ''


def clear_error_handler(self, context):
    clear_error(context.scene)


def generate_new_random_seed(scene):
    props = scene.air_props
    if (props.use_random_seed):
        props.seed = random.randint(1000000000, 2147483647)



###  need to change this so it renders and takes the depth map 
def render_frame(context, current_frame, prompts):
    """Render the current frame as part of an animation"""
    # set the frame
    context.scene.frame_set(current_frame)

    # render the frame
    bpy.ops.render.render()

    # post to the api
    return sd_generate(context.scene, prompts)


def save_render_to_file(scene, filename_prefix):
    try:
        temp_file = utils.create_temp_file(filename_prefix + "-", suffix=f".{utils.get_image_format()}")
    except:
        return handle_error("Couldn't create temp file for image", "temp_file")

    try:
        orig_render_file_format = scene.render.image_settings.file_format
        orig_render_color_mode = scene.render.image_settings.color_mode
        orig_render_color_depth = scene.render.image_settings.color_depth

        scene.render.image_settings.file_format = utils.get_image_format(to_lower=False)
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'

        bpy.data.images['Render Result'].save_render(temp_file)

        scene.render.image_settings.file_format = orig_render_file_format
        scene.render.image_settings.color_mode = orig_render_color_mode
        scene.render.image_settings.color_depth = orig_render_color_depth
    except:
        return handle_error("Couldn't save rendered image", "save_render")

    return temp_file


def save_before_image(scene, filename_prefix):
    ext = utils.get_extension_from_file_format(scene.render.image_settings.file_format)
    if ext:
        ext = f".{ext}"
    filename = f"{filename_prefix}{ext}"
    full_path_and_filename = utils.get_absolute_path_for_output_file(scene.air_props.autosave_image_path, filename)
    try:
        bpy.data.images['Render Result'].save_render(bpy.path.abspath(full_path_and_filename))
    except:
        return handle_error(f"Couldn't save 'before' image to {bpy.path.abspath(full_path_and_filename)}", "save_image")


def save_after_image(scene, filename_prefix, img_file):
    filename = f"{filename_prefix}.{utils.get_image_format()}"
    full_path_and_filename = utils.get_absolute_path_for_output_file(scene.air_props.autosave_image_path, filename)
    try:
        utils.copy_file(img_file, full_path_and_filename)
        return full_path_and_filename
    except:
        return handle_error(f"Couldn't save 'after' image to {bpy.path.abspath(full_path_and_filename)}", "save_image")

def load_image(filename, data_block_name=None):
    name = filename
    if data_block_name:
        name = data_block_name

    if name in bpy.data.images:
        existing_img = bpy.data.images[name]
        existing_img.filepath = filename
        return existing_img

    img_file = bpy.data.images.load(filename, check_existing=False)
    img_file.name = name
    return img_file

def do_pre_render_setup(scene):
    # Lock the user interface when rendering, so that we can change
    # compositor nodes in the render_init handler without causing a crash!
    # See: https://docs.blender.org/api/current/bpy.app.handlers.html#note-on-altering-data
    scene.render.use_lock_interface = True

    # clear any previous errors
    clear_error(scene)

    # mute the legacy compositor node group, if it exists
    mute_legacy_compositor_node_group(scene)


def do_pre_api_setup(scene):
    # TODO: does nothing at the moment
    pass


## this checks if the user had an api_key for dreamStudio and if the dimensions are valid and if they have entered a prompt
def validate_params(scene, prompt=None):
    if utils.get_dream_studio_api_key().strip() == "" and utils.sd_backend() == "dreamstudio":
        return handle_error("You must enter an API Key to render with DreamStudio", "api_key")
    if not utils.are_dimensions_valid(scene):
        return handle_error("Please set width and height to valid values", "invalid_dimensions")
    if utils.are_dimensions_too_small(scene):
        return handle_error("Image dimensions are too small. Please increase width and/or height", "dimensions_too_small")
    if utils.are_dimensions_too_large(scene):
        return handle_error("Image dimensions are too large. Please decrease width and/or height", "dimensions_too_large")
    if prompt == "":
        return handle_error("Please enter a prompt for Stable Diffusion", "prompt")
    return True

## not sure what airprops is 
def get_full_prompt(scene, prompt=None):
    props = scene.air_props

    if prompt is None:
        prompt = props.prompt_text.strip()

    if prompt == config.default_prompt_text:
        prompt = ""

    if props.use_preset:
        prompt = props.preset_style.replace("{prompt}", prompt)

    return prompt


## this seems to be validating the prompt for a single frame
def validate_and_process_animated_prompt_text_for_single_frame(scene, frame):
    positive_lines, negative_lines = validate_and_process_animated_prompt_text(scene)
    if not positive_lines:
        return None, None
    else:
        return get_prompt_at_frame(positive_lines, frame), get_prompt_at_frame(negative_lines, frame)
    
    
    
## this genrates the image using stable diffusion api
def sd_generate(scene, prompts=None, use_last_sd_image=False):
    """Post to the API to generate a Stable Diffusion image and then process it"""
    props = scene.air_props

    # get the prompt if we haven't been given one
    if not prompts:
        if props.use_animated_prompts:
            prompt, negative_prompt = validate_and_process_animated_prompt_text_for_single_frame(scene, scene.frame_current)
            if not prompt:
                return False
        else:
            prompt = get_full_prompt(scene)
            negative_prompt = props.negative_prompt_text.strip()
    else:
        prompt = prompts["prompt"]
        negative_prompt = prompts["negative_prompt"]

    # validate the parameters we will send
    if not validate_params(scene, prompt):
        return False

    # generate a new seed, if we want a random one
    generate_new_random_seed(scene)

    # prepare the output filenames
    before_output_filename_prefix = utils.get_image_filename(scene, prompt, negative_prompt, "-1-before")
    after_output_filename_prefix = utils.get_image_filename(scene, prompt, negative_prompt, "-2-after")
    animation_output_filename_prefix = "ai-render-"

    # if we want to use the last SD image, try loading it now
    if use_last_sd_image:
        if not props.last_generated_image_filename:
            return handle_error("Couldn't find the last Stable Diffusion image", "last_generated_image_filename")
        try:
            img_file = open(props.last_generated_image_filename, 'rb')
        except:
            return handle_error("Couldn't load the last Stable Diffusion image. It's probably been deleted or moved. You'll need to restore it or render a new image.", "load_last_generated_image")
    else:
        # else, use the rendered image...

        # save the rendered image and then read it back in
        temp_input_file = save_render_to_file(scene, before_output_filename_prefix)
        if not temp_input_file:
            return False
        img_file = open(temp_input_file, 'rb')

        # autosave the before image, if we want that, and we're not rendering an animation
        if (
            props.do_autosave_before_images
            and props.autosave_image_path
            and not props.is_rendering_animation
            and not props.is_rendering_animation_manually
        ):
            save_before_image(scene, before_output_filename_prefix)

    # prepare data for the API request
    params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": utils.get_output_width(scene),
        "height": utils.get_output_height(scene),
        "image_similarity": props.image_similarity,
        "seed": props.seed,
        "cfg_scale": props.cfg_scale,
        "steps": props.steps,
        "sampler": props.sampler,
    }

    # get the backend we're using
    sd_backend = utils.get_active_backend()

    # send to whichever API we're using
    start_time = time.time()
    generated_image_file = sd_backend.generate(params, img_file, after_output_filename_prefix, props)

    # if we didn't get a successful image, stop here (an error will have been handled by the api function)
    if not generated_image_file:
        return False

    # autosave the after image, if we should
    if utils.should_autosave_after_image(props):
        generated_image_file = save_after_image(scene, after_output_filename_prefix, generated_image_file)

        if not generated_image_file:
            return False

    # store this image filename as the last generated image
    props.last_generated_image_filename = generated_image_file

    # if we want to automatically upscale (and the backend supports it), do it now
    if props.do_upscale_automatically and sd_backend.supports_upscaling() and sd_backend.is_upscaler_model_list_loaded():
        after_output_filename_prefix = after_output_filename_prefix + "-upscaled"

        opened_image_file = open(generated_image_file, 'rb')
        generated_image_file = sd_backend.upscale(opened_image_file, after_output_filename_prefix, props)

        # if the upscale failed, stop here (an error will have been handled by the api function)
        if not generated_image_file:
            return False

        # autosave the upscaled after image, if we should
        if utils.should_autosave_after_image(props):
            generated_image_file = save_after_image(scene, after_output_filename_prefix, generated_image_file)

            if not generated_image_file:
                return False

    # if we're rendering an animation manually, save the image to the animation output path
    if props.is_rendering_animation_manually:
        generated_image_file = save_animation_image(scene, animation_output_filename_prefix, generated_image_file)

        if not generated_image_file:
            return False

    # load the image into our scene
    try:
        img = load_image(generated_image_file, after_output_filename_prefix)
    except:
        return handle_error("Couldn't load the image from Stable Diffusion", "load_sd_image")

    try:
        # View the image in the Render Result view
        utils.view_sd_in_render_view(img, scene)
    except:
        return handle_error("Couldn't switch the view to the image from Stable Diffusion", "view_sd_image")

    # track an analytics event
    additional_params = {
        "backend": utils.sd_backend(),
        "model": props.sd_model if sd_backend.supports_choosing_model() else "none",
        "preset_style": props.preset_style if props.use_preset else "none",
        "is_animation_frame": "yes" if prompts else "no",
        "has_animated_prompt": "yes" if props.use_animated_prompts else "no",
        "upscale_enabled": "yes" if props.do_upscale_automatically else "no",
        "upscale_factor": props.upscale_factor,
        "upscaler_model": props.upscaler_model,
        "duration": round(time.time() - start_time),
    }
    if props.controlnet_is_enabled and utils.sd_backend() == "automatic1111":
        additional_params["controlnet_enabled"] = "yes"
        additional_params["controlnet_model"] = props.controlnet_model
        additional_params["controlnet_module"] = props.controlnet_module
    else:
        additional_params["controlnet_enabled"] = "no"
        additional_params["controlnet_model"] = "none"
        additional_params["controlnet_module"] = "none"
    event_params = analytics.prepare_event('generate_image', generation_params=params, additional_params=additional_params)
    analytics.track_event('generate_image', event_params=event_params)

    # return success
    return True



class AIR_OT_enable(bpy.types.Operator):
    "Enable AI Render in this scene"
    bl_idname = "ai_render.enable"
    bl_label = "Enable AI Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        enable_air(context.scene)
        context.scene.air_props.is_enabled = True
        return {'FINISHED'}
    
    
    
class AIR_OT_enable(bpy.types.Operator):
    "Enable AI Render in this scene"
    bl_idname = "ai_render.enable"
    bl_label = "Enable AI Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        enable_air(context.scene)
        context.scene.air_props.is_enabled = True
        return {'FINISHED'}


class AIR_OT_disable(bpy.types.Operator):
    "Disable AI Render in this scene"
    bl_idname = "ai_render.disable"
    bl_label = "Disable AI Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.air_props.is_enabled = False
        return {'FINISHED'}


class AIR_OT_set_image_size_to_1024x1024(bpy.types.Operator):
    "Set render width and height to 1024 x 1024"
    bl_idname = "ai_render.set_image_size_to_1024x1024"
    bl_label = "1024 x 1024"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_image_dimensions(context, 1024, 1024)
        return {'FINISHED'}


class AIR_OT_show_other_dimension_options(bpy.types.Operator):
    "Other options for image size"
    bl_idname = "ai_render.show_other_dimension_options"
    bl_label = "Image Size Options"
    bl_options = {'REGISTER', 'UNDO'}

    panel_width = 250

    width: bpy.props.EnumProperty(
        name="Image Width",
        default="1024",
        items=example_dimensions_tuple_list,
        description="Image Width"
    )
    height: bpy.props.EnumProperty(
        name="Image Height",
        default="1024",
        items=example_dimensions_tuple_list,
        description="Image Height"
    )
# this makes the ui for the image size operations
def draw(self, context):
        layout = self.layout
        utils.label_multiline(layout, text=f"Choose dimensions that Stable Diffusion can work with. (If you're unsure, try 1024x1024). Dimensions can be any multiple of {utils.valid_dimension_step_size} in the range {utils.min_dimension_size}-{utils.max_dimension_size}.", width=self.panel_width)

        layout.separator()

        row = layout.row()
        row.label(text="Common Dimensions:")

        row = layout.row()
        col = row.column()
        col.label(text="Width:")
        col = row.column()
        col.prop(self, "width", text="")

        row = layout.row()
        col = row.column()
        col.label(text="Height:")
        col = row.column()
        col.prop(self, "height", text="")

        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.panel_width)

    def execute(self, context):
        set_image_dimensions(context, int(self.width), int(self.height))
        return {'FINISHED'}


class AIR_OT_generate_new_image_from_render(bpy.types.Operator):
    "Generate a new Stable Diffusion image - without re-rendering - from the last rendered image"
    bl_idname = "ai_render.generate_new_image_from_render"
    bl_label = "New Image From Last Render"

    def execute(self, context):
        do_pre_render_setup(context.scene)
        do_pre_api_setup(context.scene)

        # post to the api (on a different thread, outside the operator)
        task_queue.add(functools.partial(sd_generate, context.scene))

        return {'FINISHED'}
    
class AIR_OT_generate_new_image_from_last_sd_image(bpy.types.Operator):
    "Generate a new Stable Diffusion image - without re-rendering - using the most recent Stable Diffusion image as the starting point"
    bl_idname = "ai_render.generate_new_image_from_current"
    bl_label = "New Image From Last AI Image"

    def execute(self, context):
        do_pre_render_setup(context.scene)
        do_pre_api_setup(context.scene)

        # post to the api (on a different thread, outside the operator)
        task_queue.add(functools.partial(sd_generate, context.scene, None, True))

        return {'FINISHED'}

##  this is the way the engine renders image sequences but i think i can get a fram out of it 

    def _pre_render(self, context):
        scene = context.scene

        # do validation and setup
        if validate_params(scene) and validate_animation_output_path(scene):
            do_pre_render_setup(scene)
            do_pre_api_setup(scene)
        else:
            return False

        # validate and process the animated prompts, if we are using them
        if context.scene.air_props.use_animated_prompts:
            self._animated_prompts, self._animated_negative_prompts = validate_and_process_animated_prompt_text(context.scene)
            if not self._animated_prompts:
                return False
        else:
            self._animated_prompts = None
            self._static_prompt = get_full_prompt(context.scene)
            self._negative_static_prompt = scene.air_props.negative_prompt_text.strip()

        return True

    def _start_render(self, context):
        self._finished = False

        self._orig_current_frame = context.scene.frame_current
        self._start_frame = context.scene.frame_start
        self._end_frame = context.scene.frame_end
        self._frame_step = context.scene.frame_step
        self._current_frame = context.scene.frame_start
        context.scene.air_props.is_rendering_animation_manually = True

        context.scene.air_progress_status_message = ""
        context.scene.air_progress_label = self._get_label()
        context.scene.air_progress = 0

        self._ticks_since_last_render = 0
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

#  will need the4 controlnet models for the depth map

class AIR_OT_automatic1111_load_controlnet_models(bpy.types.Operator):
    "Load the available ControlNet models from Automatic1111"
    bl_idname = "ai_render.automatic1111_load_controlnet_models"
    bl_label = "Load ControlNet Models"

    def execute(self, context):
        automatic1111_api.load_controlnet_models(context)
        return {'FINISHED'}


class AIR_OT_automatic1111_load_controlnet_modules(bpy.types.Operator):
    "Load the available ControlNet modules (preprocessors) from Automatic1111"
    bl_idname = "ai_render.automatic1111_load_controlnet_modules"
    bl_label = "Load ControlNet Modules"

    def execute(self, context):
        automatic1111_api.load_controlnet_modules(context)
        return {'FINISHED'}

class AIR_OT_automatic1111_load_controlnet_models_and_modules(bpy.types.Operator):
    "Load the available ControlNet models and modules (preprocessors) from Automatic1111"
    bl_idname = "ai_render.automatic1111_load_controlnet_models_and_modules"
    bl_label = "Load ControlNet Models and Modules"

    def execute(self, context):
        # load the models and modules from the Automatic1111 API
        automatic1111_api.load_controlnet_models(context) and automatic1111_api.load_controlnet_modules(context)

        # set the default values for the ControlNet model and module
        automatic1111_api.choose_controlnet_defaults(context)
        return {'FINISHED'}


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)