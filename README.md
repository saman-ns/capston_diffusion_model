# MoodVista: Blender Addon for Enhanced Story Previsualization


## Overview
MoodVista is a revolutionary Blender addon designed to integrate stable diffusion technology into 3D storytelling and previsualization workflows. This tool empowers 3D artists to bring their visions to life with unprecedented speed and stylistic flexibility. By using a combination of reference images to fine-tune diffusion models and depth maps for composition guidance, MoodVista facilitates the creation of detailed, stylized scenes directly from simple blockouts and textual prompts. Whether you're exploring new narrative landscapes or refining the visual tone of your project, MoodVista accelerates your creative process, offering a closer glimpse into the final outcome during the previsualization stage.

## Problem Statement
This project aims to integrate the power of diffusion models into the 3d workflow of an animation project specifically for the previsualization parts. making it easier to develop the style of the project 

## Data Science Solution  
the addon uses the mood board to train a diffusion model using the data provided by the artist to optimize the visual development of the animation 

## Features
Style Customization: Fine-tune diffusion models using reference images to align with your project's visual style.
Depth-Map Integration: Utilize Blender-generated depth maps to guide composition, ensuring stylistic and spatial consistency.
Simplified Workflow: Seamlessly integrates into Blender, making advanced diffusion model techniques accessible to 3D artists without requiring deep technical knowledge.
Rapid Previsualization: Accelerate the previsualization process, enabling artists to quickly explore and iterate on visual styles and narrative elements.


## Prerequisites
Blender version 4.5 or higher.
An active Hugging Face account with the necessary credentials.
Note: The addon is currently in development and not yet available for installation.


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
