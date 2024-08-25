<div align="center">

# Abominable Workflow
**A comfyui workflow for PixArt-Sigma employing SD15 to boost its visual impact.**

<p>
<img alt="Platform" src="https://img.shields.io/badge/platform-ComfyUI-33F">
<img alt="License"  src="https://img.shields.io/github/license/martin-rizzo/AbominableWorkflow?color=11D">
<img alt="Last"     src="https://img.shields.io/github/last-commit/martin-rizzo/AbominableWorkflow">
<img alt="Version"  src="https://img.shields.io/github/v/tag/martin-rizzo/AbominableWorkflow?label=version">
</p>

![Abominable Screenshot](examples/abominable_screenshot.jpg)

</div>

The **Abominable Workflow** combines the high prompt adherence of PixArt Sigma with the impactful visual detail of SD1.5 models that we've always loved.

## Required Nodes

To use this workflow, you'll need to have **ComfyUI_ExtraModels** installed. Here's how to do it on Linux in four simple steps:

      cd <your-comfyui-directory>
      cd custom_nodes
      git clone https://github.com/city96/ComfyUI_ExtraModels
      pip install -r requirements.txt


**Note 1:** Running `pip` may require activating the virtual environment used to run ComfyUI.

**Note 2:** Windows users can refer to the installation methods suggested on the project **[GitHub Page](https://github.com/city96/ComfyUI_ExtraModels?tab=readme-ov-file#installation)**

**Note 3:** ComfyUI_ExtraModels has various dependencies and requirements on which it heavily relies. Therefore, it might be more convenient to install it using a node manager like **[ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)**.


## Required Files

You also need to have the following 6 files  locally:

 - **From [PixArt Sigma GitHub Page](https://github.com/PixArt-alpha/PixArt-sigma?tab=readme-ov-file#-available-models):**
    * PixArt-Sigma-XL-2-1024-MS.pth

- **From [PixArt Text Encoder Hugging Face Repo](https://huggingface.co/PixArt-alpha/pixart_sigma_sdxlvae_T5_diffusers/tree/main/text_encoder):**
    * config.json
    * model.safetensors.index.json
    * model-00001-of-00002.safetensors
    * model-00002-of-00002.safetensors

- **From [PixArt VAE Hugging Face Repo](https://huggingface.co/PixArt-alpha/pixart_sigma_sdxlvae_T5_diffusers/tree/main/vae):**
    * diffusion_pytorch_model.safetensors
    * (this file must be renamed to "`pixart_sigma_vae.safetensors`")

### File Placement
Once obtained, place the files within the ComfyUI directory as outlined below:

 - __`comfyui/models/checkpoints`__
     * `PixArt-Sigma-XL-2-1024-MS.pth`
     * `Photon_v1.safetensor` _(or any other SD15 model)_
 - __`comfyui/models/t5`__
     * `config.json`
     * `model.safetensors.index.json`
     * `model-00001-of-00002.safetensors`
     * `model-00002-of-00002.safetensors`
 - __`comfyui/models/vae`__
     * `pixart_sigma_vae.safetensors`


## Project Checklist

- [x] Editable parameters grouped together.
- [x] Explanation of how to install required nodes and files.
- [ ] Support for 2K model.
- [ ] Simplify installation process.
- [ ] Automatic detection of model used.
- [ ] Automatic image size selection.


## Lincense

Copyright (c) 2024 Martin Rizzo  
This project is licensed under the MIT license.  
See the ["LICENSE"](LICENSE) file for details.

