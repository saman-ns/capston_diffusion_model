# StyleBlender: Blender Addon for Enhanced Story Previsualization


## Overview
In this project. I am aiming to utilize a diffusion model, in this case, one of the stable diffusion models from stability AI, to develop a tool for 3d artists. the tool is in the form of an add-on for the 3d software Blender3d. it will generate textures for the objects and scenes using a prompt from the artist and the rendering of the scene as a visual prompt.

## Problem Statement
This project aims to integrate the power of diffusion models into the 3d workflow of an animation project specifically for the previsualization parts. making it easier to develop the style of the project 

## Data Science Solution  
using generative AI, specifically diffusion models, the process of texturing objects in a 3d scene can be automated. The struggle so far in this space has been the integration of the tool into the working pipeline. and the lack of fine-tuning of the models available for this purpose.

## Features
Style Customization: Fine-tune diffusion models using reference images to align with your project's visual style.
Depth-Map Integration: Utilize Blender-generated depth maps to guide composition, ensuring stylistic and spatial consistency.
Simplified Workflow: Seamlessly integrates into Blender, making advanced diffusion model techniques accessible to 3D artists without requiring deep technical knowledge.
Rapid Previsualization: Accelerate the previsualization process, enabling artists to quickly explore and iterate on visual styles and narrative elements.


## Prerequisites
Blender version 4.5 or higher.
An active Hugging Face account with the necessary credentials.
Note: The addon is currently in development and not yet available for installation.

## first steps
To better understand the diffusion models, I made a diffusion model from Sctach with PyTorch. the model was built based on the research papers listed below:
1."Denoising Diffusion Probabilistic Models" (https://arxiv.org/abs/2006.11239v2)
2."Diffusion Models Beat GANs on Image Synthesis: (https://doi.org/10.48550/arXiv.2105.05233)

##The link for the model repository is here (this model was not used to generate the images in the tool being developed. it was helpful in understanding the architecture and how integrate it with into the software)


## Installation
The installation guide will be provided upon the addon's completion. Stay tuned for updates on the development process and release information.
 
 
## featuring:

A section for uploading reference images to guide the style.
A field for entering descriptive text prompts.
A button to generate and utilize depth maps from the chosen camera perspective.
Designed primarily for landscape generation, MoodVista streamlines the creation of stylized environments, allowing artists to project generated textures onto 3D objects and animate scenes with enhanced visual fidelity.

## development 
A sample project will be added to showcase the capabilities of the addon 


## scrpts
Ui_menu: the script is a general template to generate the basic UI for the addon 

diffusion-model-test: a separate application made to test the diffusion model that will be used in the addon

operator_mesh_uc: the template required to transfer the result of the diffusion model to the mesh 

integration: part of the case study to understand the texture generation in a blender with diffusion models: This code defines a deep learning model called SeamlessModel that is used for image processing tasks. The model consists of convolutional and recurrent neural network layers. It takes an input image tensor and applies a series of convolutional operations to extract features. The features are then passed through a Gated Recurrent Unit (GRU) layer to capture temporal dependencies. Finally, the output is passed through a linear layer with a sigmoid activation function to produce a single output value. 
