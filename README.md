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

The **Abominable Workflow** combines the high prompt adherence of PixArt-Sigma
with the impactful visual detail of the SD1.5 models that we've always loved.

 * [Required Files](#required-files)
 * [Required Nodes](#required-nodes)
   * [Automatically Installing Required Nodes](#automatically-installing-required-nodes)
   * [Manually Installing Required Nodes on Linux](#manually-installing-required-nodes-on-linux)
   * [Manually Installing Required Nodes on Windows](#manually-installing-required-nodes-on-windows)

## Required Files

The workflow requires the following models to be installed in ComfyUI, please
place them in the directories specified below:

 * __`<your_comfyui_dir>` / models / checkpoints__
   * [PixArt-Sigma-1024.safetensors](https://huggingface.co/martin-rizzo/AbominableWorkflow/tree/main/checkpoints)
   * [Photon-Refiner.safetensors](https://huggingface.co/martin-rizzo/AbominableWorkflow/tree/main/checkpoints)
 * __`<your_comfyui_dir>` / models / clip__
   * [T5-Encoder-Q5_K_M.gguf](https://huggingface.co/martin-rizzo/AbominableWorkflow/tree/main/clip)
 * __`<your_comfyui_dir>` / models / vae__
   * [PixArt-Sigma-VAE.safetensors](https://huggingface.co/martin-rizzo/AbominableWorkflow/tree/main/vae)

## Required Nodes

ComfyUI must also have the following custom nodes installed:
 * **ComfyUI_ExtraModels**: Provides support for PixArt-Sigma.
 * **ComfyUI-GGUF**: Provides support for the GGUF format (quantized T5).
 * **ComfyUI-Crystools**: Used for some simple string operations.

### Automatically Installing Required Nodes

The best way to install the required nodes is to use [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager).
This is an extension for ComfyUI that offers management functions to install,
remove, disable, and enable various custom nodes. From there, you can easily
install the required nodes.

### Manually Installing Required Nodes on Linux

*To be completed soon...*

### Manually Installing Required Nodes on Windows

*To be completed soon...*

## Project Checklist

- [x] Editable parameters grouped together.
- [ ] Explanation of how to install required files.
- [ ] Explanation of how to manually install nodes on Linux and Windows.
- [ ] Support for 2K model.
- [ ] Simplify installation process.
- [ ] Automatic detection of model used.
- [ ] Automatic image size selection.

## Lincense

Copyright (c) 2024 Martin Rizzo  
This project is licensed under the MIT license.  
See the ["LICENSE"](LICENSE) file for details.

