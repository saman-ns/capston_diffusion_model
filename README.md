# StyleBlender: Blender Addon for Speed up StoryTelling


## Overview
In this project. I am aiming to utilize a diffusion models, specifically SDXL 1.0 from stability AI to develop a tool for 3d artists. the tool is an add-on for the 3d software Blender3d. it will generate textures for the objects and scenes using a prompt from the artist and the render from the scene as a visual prompt.

## Problem Statement
This project aims to integrate the power of diffusion models into the 3d workflow of an animation project specifically for the pre-visualization parts. making it easier to develop the style of the project. currently this exploration is time consuming since each style needs to be developed separately. this step of each project plays a crucial role in how the final product will look like. 

## Data Science Solution  
using generative AI, the process of texturing objects in a 3d scene can would be faster. The struggle so far in this space has been the integration of the tool into the working pipeline. and the lack of fine-tuning of the models available for this purpose. using the primitive shapes as a visual prompt and a description of the scene as a text prompt, the artist can generate a variety of options that was not previously possible.


## Features
Style Customization: Fine-tune diffusion models using reference images to align with your project's visual style.
Depth-Map Integration: Utilize Blender-generated depth maps to guide composition, ensuring stylistic and spatial consistency.
Simplified Workflow: Seamlessly integrates into Blender, making advanced diffusion model techniques accessible to 3D artists without requiring deep technical knowledge.
Rapid Pre-visualization: Accelerate the pre-visualization process, enabling artists to quickly explore and iterate on visual styles and narrative elements.


## Prerequisites
Blender version 4.0 or higher.
An active Hugging Face account with the necessary credentials.
A stability AI API key in to access the generative models

## The Data
Since diffusion models are take a lot of computing power to train. training a model was out of scope of this project. To better understand the diffusion models, I made a diffusion model from Scratch with PyTorch. the model was built based on the research papers listed below:
1."Denoising Diffusion Probabilistic Models" (https://arxiv.org/abs/2006.11239v2)
2."Diffusion Models Beat GANs on Image Synthesis" (https://doi.org/10.48550/arXiv.2105.05233)

##The link for the model repository is here:
https://github.com/saman-ns/Diffusion-model-from-scratch-using-pytorch
 (this model was not used to generate the images in the tool being developed. it was helpful in understanding the architecture and how integrate it into the 3Dsoftware)

## Additional models
Gaining a better understanding on how diffusion models work. In order to have control over the composition of the output to generate textures required for each object. an additional pre-processor needs to be used, ControlNets, are neural network architecture to add spatial conditioning controls to large, pre-trained text-to-image diffusion models. these models were initially introduced in this paper:
 "Adding Conditional Control to Text-to-Image Diffusion Models", https://arxiv.org/abs/2302.05543

and with the below Architecture they allow an added level of control over the outcome. The condition used for this project is the depth data of the picture:
![alt text](Controlnet.JPG)


## Installation
Download the code az a zipfile and in blender go to -> preferences -> add-ons -> StyleBlender
the addon also utilizes automatic1111 to do pre-processing. it can be downloaded from the following directory:
https://github.com/AUTOMATIC1111/stable-diffusion-webui

 
 
## featuring:
A field for entering descriptive text prompts.
A button to generate and utilize depth maps from the chosen camera perspective.
Designed primarily for landscape generation, MoodVista streamlines the creation of stylized environments, allowing artists to project generated textures onto 3D objects and animate scenes with enhanced visual fidelity.

## samples
Here are some samples of what the addon allows the artist to do:
here is the original image:
![alt text](<ai-render-1714923225-steampunk style flowers in a pot and lamp . retro, mechanical, detailed, Victorian-2-after-upscaled-9juaa8b_.png>)
some AI enabled rendering of the same scene
![alt text](<ai-render-1714923225-steampunk style flowers in a pot and lamp . retro, mechanical, detailed, Victorian-2-after-upscaled-9juaa7b_.png>)
![alt text](<ai-render-1714923151-flowers in a pot and lamp . in Shin Hanga style, eldritch-2-after-upscaled-290i904e.png>)

## scripts
ui folder: containing the ui_panels.py file, it configures how the add-on looks in the blender software

sd_backend: containing two files that manage api calls to stability_api (hosts the diffusion model from stable diffusion) and automatic1111_api (used to do the pre-processing as it manages the control api )

__init__: the initial file that will run in order to register all the components and set up the models

config: configuring how add-on is set up for the first time of installation

operators: Blender3D uses operators as a part of the api to handle different tasks this file hosts most of the functionality of the add-on with referenced for different methods 

Preferences: Adjusting the dimensions and the additional prompts needed to generate the final image

task_queue: handles the wait time while the stability ai api generates the image






