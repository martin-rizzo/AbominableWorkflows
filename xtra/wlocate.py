"""
  File    : wlocate.py
  Brief   : Moves images to directories based on the workflow name.
  Author  : Martin Rizzo | <martinrizzo@gmail.com>
  Date    : Oct 25, 2024
  Repo    : https://github.com/martin-rizzo/T5ExtendedEncoder
  License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                              Abominable Workflows
        A collection of txt2img comfyui workflows for PixArt-Sigma

     Copyright (c) 2024 Martin Rizzo

     Permission is hereby granted, free of charge, to any person obtaining
     a copy of this software and associated documentation files (the
     "Software"), to deal in the Software without restriction, including
     without limitation the rights to use, copy, modify, merge, publish,
     distribute, sublicense, and/or sell copies of the Software, and to
     permit persons to whom the Software is furnished to do so, subject to
     the following conditions:

     The above copyright notice and this permission notice shall be
     included in all copies or substantial portions of the Software.

     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
     TORT OR OTHERWISE, ARISING FROM,OUT OF OR IN CONNECTION WITH THE
     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import os
import sys
import json
import hashlib
import argparse
from PIL import Image

# ANSI escape codes for colored terminal output
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
DEFAULT_COLOR = '\033[0m'


#----------------------------- ERROR MESSAGES ------------------------------#

def message(text: str) -> None:
    """Displays and logs a regular message to the standard error stream.
    """
    print(f"  {GREEN}>{DEFAULT_COLOR} {text}", file=sys.stderr)

def warning(message: str, *info_messages: str) -> None:
    """Displays and logs a warning message to the standard error stream.
    """
    print(f"{CYAN}[{YELLOW}WARNING{CYAN}]{YELLOW} {message}{DEFAULT_COLOR}", file=sys.stderr)
    for info_message in info_messages:
        print(f"          {YELLOW}{info_message}{DEFAULT_COLOR}", file=sys.stderr)
    print()

def error(message: str, *info_messages: str) -> None:
    """Displays and logs an error message to the standard error stream.
    """
    print(f"{CYAN}[{RED}ERROR{CYAN}]{RED} {message}{DEFAULT_COLOR}", file=sys.stderr)
    for info_message in info_messages:
        print(f"          {RED}{info_message}{DEFAULT_COLOR}", file=sys.stderr)
    print()

def fatal_error(message: str, *info_messages: str) -> None:
    """Displays and logs an fatal error to the standard error stream and exits.
    Args:
        message       : The fatal error message to display.
        *info_messages: Optional informational messages to display after the error.
    """
    error(message)
    for info_message in info_messages:
        print(f" {CYAN}\u24d8  {info_message}{DEFAULT_COLOR}", file=sys.stderr)
    exit(1)


#--------------------------------- HELPERS ---------------------------------#

def replace_filename(path, new_name=None, new_extension=None):
    """Replace the name or extension of a given file path.
    """
    if not path:
        raise ValueError("The 'path' parameter must be provided.")

    directory, filename = os.path.split(path)
    name, extension     = os.path.splitext(filename)

    # replace the name if a new one is provided
    if new_name:
        name = new_name

    # replace the extension if a new one is provided
    if new_extension:
        extension = new_extension

    # construct the new full path with updated name & extension
    new_path = os.path.join(directory, f"{name}{extension}")
    return new_path


def get_unique_path(path):
    """Generates a unique path by appending a counter to the filename if a file already exists.
    """
    directory, filename = os.path.split(path)
    name, extension     = os.path.splitext(filename)
    separator           = '-'

    # if the filename already ends with a separator,
    # no additional separator will be added
    if name.endswith('-') or name.endswith('_'):
        separator = ''

    unique_path, counter = path, 0
    while os.path.exists(unique_path):
        counter += 1
        # format the new filename with a two-digit counter and original extension
        new_filename = name + separator + str(counter).zfill(2) + extension
        unique_path  = os.path.join(directory, new_filename)
    return unique_path


def filter_words(words: list) -> list:
    """Removes words from a list that do not start with an alphanumeric character.
    Args:
        word_list: A list of strings representing words.
    Returns:
        A new list containing only the words that start with an alphanumeric character.
    """
    filtered_words = []
    for word in words:
        if word and word[0].isalnum():
            filtered_words.append(word)
    return filtered_words


def get_workflow_name(workflow_json: str) -> str:
    """Extracts the workflow name from a JSON
    Args:
        workflow_json: A JSON string containing workflow data.
    Returns:
        The title of the maint group in the workflow.
    """
    try:
        name          = 'abominable workflow'
        name_distance = 100000

        workflow = json.loads(workflow_json)
        groups = workflow.get('groups', [])
        for group in groups:
            title    = group.get('title')
            bounding = group.get('bounding')
            if not isinstance(title, str) or not isinstance(bounding, list):
                continue
            if len(bounding)<2:
                continue
            if bounding[0]+bounding[1] < name_distance:
                name_distance = bounding[0]+bounding[1]
                name          = title
        name_words = name.split()
        return ' '.join( filter_words(name_words) )

    except Exception:
        return 'invalid workflow'


def get_prompt_text(workflow_json: str) -> str:
    """Extracts the prompt text from a JSON string
    Args:
        workflow_json (str): A JSON string containing workflow data.
    Returns:
        The text of the prompt node in the workflow.
    """
    prompt = None
    max_distance = 1000

    workflow = json.loads(workflow_json)
    nodes = workflow.get('nodes', [])
    for node in nodes:

        title = node.get('title','')
        pos   = node.get('pos')
        if isinstance(pos, dict):
            distance = pos.get('0',0) + pos.get('1',0)
        elif isinstance(pos, list):
            distance = pos[0] + pos[1]
        else:
            distance = max_distance

        if distance<max_distance and title.lower() == 'prompt':
            widgets_values = node.get('widgets_values')
            if isinstance(widgets_values, list):
                prompt = widgets_values[0]
                max_distance = distance

    return prompt


def generate_hash(input_string: str, length: int = None) -> str:
    """Generates a hash from the input string.
    Args:
        input_string (str): The string to be hashed.
        length       (int): Specify the desired length of the hash (in characters).
    Returns:
        A hexadecimal representation of the hash.
    """
    shake_signature = hashlib.shake_256()
    shake_signature.update(input_string.encode())
    hex_hash = shake_signature.hexdigest( int((length+1)/2) )
    return hex_hash


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def locate_image(filename       : str,
                 root_dir       : str  = None,
                 use_prompt_hash: bool = False,
                 overwrite_files: bool = False):
    """Moves an image to the directory that indicates the workflow with which it was created.

    Args:
        filename    (str) : The path to the image file to locate.
        root_dir    (str) : The base directory for determining the destination folder.
                            If not provided, the current working directory will be used as default.
        prompt_hash (bool): Whether to use the hash of the prompt as the new filename.
        overwrite   (bool): Whether to allow overwriting files with the same name:
                            If True, existing files can be overwritten;
                            If False, a unique filename will be generated to avoid overwriting.
    """

    # get the workflow name from the image
    with Image.open(filename) as image:
        workflow_json = image.info.get('workflow')
        workflow_name = get_workflow_name(workflow_json) or 'No Workflow'
        workflow_name = workflow_name.replace(' ', '_')

    # construct the destination directory path
    destination = workflow_name
    if root_dir:
        destination = os.path.join(root_dir, workflow_name)

    # create the target directory if it doesn't exist
    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)

    try:
        new_location = os.path.join(destination, os.path.basename(filename))
        if use_prompt_hash:
            prompt       = get_prompt_text(workflow_json)
            prompt_hash  = generate_hash(prompt, length=12) if prompt is not None else None
            new_location = replace_filename(new_location, new_name=prompt_hash)
        if not overwrite_files:
            new_location = get_unique_path(new_location)
        os.rename(filename, new_location)
        return True
    except OSError as e:
        print(f"Failed to move file {filename} to {new_location}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Moves images to directories based on the workflow name.")
    parser.add_argument('images'            , nargs="+"         ,  help="Image file(s) to move.")
    parser.add_argument('-r', '--root-dir'  ,                      help="The root directory used as the base of the destination folder.")
    parser.add_argument( '--use-prompt-hash', action='store_true', help="Use the hash of the prompt as the new filename.")
    parser.add_argument( '--overwrite-files', action='store_true', help="Allow overwriting files with the same name.")

    args  = parser.parse_args()
    for filepath in args.images:
        locate_image(filepath, root_dir=args.root_dir, use_prompt_hash=args.use_prompt_hash, overwrite_files=args.overwrite_files)


if __name__ == "__main__":
    main()
