<div align="center">

# Abominable Workflows

<p>
<img alt="Platform"     src="https://img.shields.io/badge/platform-ComfyUI-blue">
<img alt="License"      src="https://img.shields.io/github/license/martin-rizzo/AbominableWorkflows?color=blue">
<img alt="Version"      src="https://img.shields.io/github/v/tag/martin-rizzo/AbominableWorkflows?label=version">
<img alt="Last"         src="https://img.shields.io/github/last-commit/martin-rizzo/AbominableWorkflows"> |
<a href="https://civitai.com/models/420163/abominable-workflows">
   <img alt="CivitAI"      src="https://img.shields.io/badge/page-CivitAI-00F"></a>
<a href="https://huggingface.co/martin-rizzo/AbominableWorkflows">
   <img alt="Hugging Face" src="https://img.shields.io/badge/models-HuggingFace-yellow"></a>
</p>

![Abominable Workflows Grid](./demo_images/abominable_grid.jpg)
</div>

**Abominable Workflows** is a collection of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflows that unleashes the full potential of [PixArt-Sigma](https://github.com/PixArt-alpha/PixArt-sigma) by enhancing its exceptional prompt-following capabilities with the rich detail of SD15 models. <br/>
Each workflow generates a distinct style of imagery:

* **abominable_PHOTO_** : Realistic images with photographic details.
* **abominable_DARKFAN80_** : Dark, cinematic 80s style with VHS aesthetics and dramatic lighting.
* **abominable_PIXEL_** : Pixel art style with retro aesthetics and vibrant, blocky shapes.
* **abominable_INK_** : Ink-style illustrations with bold outlines and a hand-painted finish.
* **abominable_1GIRL_** : Images centered on a captivating woman with photographic realism.
* **abominable_MILO_** : European stylized comic book aesthetic with intricate linework.
* **classic_abominable_spaghetti** : Similar experience to the previous v2 but with all the new enhancements.


## Setup Guide

 * [Required Files](#required-files)
 * [Required Nodes](#required-nodes)
 * [How to Automatically Install the Required Nodes](#how-to-automatically-install-the-required-nodes)
 * [Manually Installing Required Nodes on Linux](#manually-installing-required-nodes-on-linux)
 * [Manually Installing Required Nodes on Windows](#manually-installing-required-nodes-on-windows)


## Required Files

To use the workflows, you need to have the following models installed in ComfyUI.<br/>
Place them in the corresponding directories as specified below.

__`<your_comfyui_dir>` / models / checkpoints :__
 * [pixart_sigma-FP16.safetensors](
   https://huggingface.co/martin-rizzo/AbominableWorkflows/tree/main)
 * [photon_refiner-FP16.safetensors](
   https://huggingface.co/martin-rizzo/AbominableWorkflows/tree/main)

__`<your_comfyui_dir>` / models / clip :__
 * [t5_xxl_encoder-FP8.safetensors](
   https://huggingface.co/martin-rizzo/AbominableWorkflows/tree/main)

__`<your_comfyui_dir>` / models / vae :__
 * [pixart_vae.safetensors](
   https://huggingface.co/martin-rizzo/AbominableWorkflows/tree/main)


## Required Nodes

> [!IMPORTANT]
> Ensure that your ComfyUI is updated to the latest version.

Additionally, the workflows require the following custom nodes to be installed:
 * [__ComfyUI_ExtraModels__](
   https://github.com/city96/ComfyUI_ExtraModels): provides support for PixArt-Sigma.
 * [__ComfyUI-Crystools__](
   https://github.com/crystian/ComfyUI-Crystools): used for some simple string operations.

### How to Automatically Install the Required Nodes

The easiest way to install the required nodes is by using [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager).
This extension for ComfyUI offers management functions to install, remove,
disable, and enable custom nodes. It simplifies the process and can save you
a lot of trouble.

If for some reason you cannot use ComfyUI-Manager, follow the instructions
below to install the nodes manually.

### Manually Installing Required Nodes on Linux

To manually install the nodes, open a terminal and run the following commands:
```
cd <your_comfyui_dir>
git clone https://github.com/city96/ComfyUI_ExtraModels ./custom_nodes/ComfyUI_ExtraModels
git clone https://github.com/crystian/ComfyUI-Crystools ./custom_nodes/ComfyUI-Crystools
```

If ComfyUI is using a virtual environment, you must activate it before installing
the dependencies:
```
# You might need to replace '.venv' with the directory
# where the virtual environment is located
source .venv/bin/activate
```

Then, install the dependencies required by the nodes:
```
python -m pip install -r ./custom_nodes/ComfyUI_ExtraModels/requirements.txt
python -m pip install -r ./custom_nodes/ComfyUI-Crystools/requirements.txt
```

### Manually Installing Required Nodes on Windows

If you are using the standalone ComfyUI release on Windows, open a CMD in
the "ComfyUI_windows_portable" folder (the one containing your `run_nvidia_gpu.bat`
file).

From that directory, run the following commands to install the required nodes:
```
git clone https://github.com/city96/ComfyUI_ExtraModels ComfyUI/custom_nodes/ComfyUI_ExtraModels
git clone https://github.com/crystian/ComfyUI-Crystools ComfyUI/custom_nodes/ComfyUI-Crystools
```

Then, install the dependencies required by these nodes:
```
.\python_embeded\python.exe -s -m pip install -r .\ComfyUI\custom_nodes\ComfyUI_ExtraModels\requirements.txt
.\python_embeded\python.exe -s -m pip install -r .\ComfyUI\custom_nodes\ComfyUI-Crystools\requirements.txt
```


## Project Checklist

- [x] Editable parameters grouped together.
- [x] Explanation of how to install required files.
- [x] Explanation of how to manually install nodes on Linux and Windows.
- [x] Option to select portrait or landscape image orientation.
- [ ] Support for 2K model.
- [ ] Simplify installation process.
- [ ] Automatic detection of model used.
- [ ] Automatic image size selection.


## Lincense

Copyright (c) 2024 Martin Rizzo  
This project is licensed under the MIT license.  
See the ["LICENSE"](LICENSE) file for details.


## Acknowledgments

I would like to thank the developers of PixArt-Σ for their outstanding work.
Their model has been a crucial component in the development of my workflows.

__Further Information about PixArt-Σ__:
  * [PixArt-Σ GitHub Repository](https://github.com/PixArt-alpha/PixArt-sigma)
  * [PixArt-Σ Hugging Face Model](https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS)
  * [PixArt-Σ arXiv Report](https://arxiv.org/abs/2403.04692)

