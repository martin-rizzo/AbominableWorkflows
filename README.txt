# Abominable Workflows v3

**Abominable Workflows** is a collection of ComfyUI workflows that unleashes the full potential of PixArt-Sigma by enhancing its exceptional prompt-following capabilities with the rich detail of SD15 models. Each workflow generates a distinct style of imagery:

 *  **abominable_PHOTO_**     : Realistic images with photographic details.
 *  **abominable_DARKFAN80_** : Dark, cinematic 80s style with VHS aesthetics and dramatic lighting.
 *  **abominable_PIXEL_**     : Pixel art style with retro aesthetics and vibrant, blocky shapes.
 *  **abominable_INK_**       : Ink-style illustrations with bold outlines and a hand-painted finish.
 *  **abominable_1GIRL_**     : Images centered on a captivating woman with photographic realism.
 *  **abominable_MILO_**      : European stylized comic book aesthetic with intricate linework.
 *  **classic_abominable_spaghetti** : Similar experience to the previous v2 but with all the new enhancements.


## Required Files

To use the workflows, you need to have the following models installed in ComfyUI.
Place them in the corresponding directories as specified below. 

<your_comfyui_dir> / models / checkpoints :
  * pixart_sigma-FP16.safetensors   (1.2GB)
  * photon_refiner-FP16.safetensors (2.1GB)

<your_comfyui_dir> / models / clip :
  * t5_xxl_encoder-FP8.safetensors  (4.9GB)

<your_comfyui_dir> / models / vae :
  * pixart_vae.safetensors          (0.1GB)

```
https://huggingface.co/martin-rizzo/AbominableWorkflows/tree/main
```


## Required Nodes

> [!IMPORTANT]
> Ensure that your ComfyUI is updated to the latest version.

Additionally, the workflows require the following custom nodes to be installed:
  * ComfyUI_ExtraModels : provides support for PixArt-Sigma.
  * ComfyUI-Crystools   : used for some simple string operations.

```
https://github.com/crystian/ComfyUI-Crystools
https://github.com/city96/ComfyUI_ExtraModels
```


### How to Automatically Install the Required Nodes

The easiest way to install the required nodes is by using ComfyUI-Manager.
This extension for ComfyUI offers management functions to install, remove,
disable, and enable custom nodes. It simplifies the process and can save you
a lot of trouble.

```
https://github.com/ltdrdata/ComfyUI-Manager
```

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
# You might need to replace '.venv' with the dir where the virt environment is located
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

### Workflows
- [x] Editable parameters grouped together.
- [x] Option to select portrait or landscape image orientation.
- [x] Option to choose between two samplers (fast/quality).
- [x] Option for refiner to ignore prompt and focus on other elements.
- [x] Variations by changing the refiner seed.
- [x] Preconfigured workflows with different styles.
- [x] Unified PixArt prompt and refiner prompt.
- [x] CivitAI prompt extractor compatibility.
- [ ] Support for PixArt 2K model.
- [ ] Automatic detection of the model used and the optimal image size.

### Development & documentation
- [x] Explanation of how to install required files.
- [x] Explanation of how to manually install nodes on Linux and Windows.
- [x] Models in FP16 or FP8 for minimal VRAM (6 or 8GB).
- [ ] Apply ComfyUI advances to speed up inference (own nodes?).
- [ ] Simplify installation with minimal custom nodes.


## Lincense

Copyright (c) 2024 Martin Rizzo  
This project is licensed under the MIT license.  
See the ["LICENSE"](LICENSE) file for details.


## Acknowledgments

I would like to thank the developers of PixArt-Σ for their outstanding work.
Their model has been a crucial component in the development of my workflows.

__Further Information about PixArt-Σ__:
  * [PixArt-Σ GitHub Repository]( https://github.com/PixArt-alpha/PixArt-sigma )
  * [PixArt-Σ Hugging Face Model]( https://huggingface.co/PixArt-alpha/PixArt-Sigma-XL-2-1024-MS )
  * [PixArt-Σ arXiv Report]( https://arxiv.org/abs/2403.04692 )

