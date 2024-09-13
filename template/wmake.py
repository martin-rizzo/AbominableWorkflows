"""
  File    : wmake.py
  Brief   : Creates workflows from a template and a config file
  Author  : Martin Rizzo | <martinrizzo@gmail.com>
  Date    : Sep 12, 2024
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
import argparse

# ANSI escape codes for colored terminal output
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
DEFAULT_COLOR = '\033[0m'

# Get the directory of the current Python script
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Default name for the configuration file
CONFIG_DEFAULT_NAME = 'configurations.txt'

# Indentation level for JSON output
JSON_INDENT=2


#----------------------------- ERROR MESSAGES ------------------------------#

def message(text: str) -> None:
    """Displays and logs a regular message to the standard error stream.
    """
    print(f"  {GREEN}>{DEFAULT_COLOR} {text}", file=sys.stderr)


def warning(message: str) -> None:
    """Displays and logs a warning message to the standard error stream.
    """
    print(f"{CYAN}[{YELLOW}WARNING{CYAN}]{YELLOW} {message}{DEFAULT_COLOR}", file=sys.stderr)


def error(message: str) -> None:
    """Displays and logs an error message to the standard error stream.
    """
    print(f"{CYAN}[{RED}ERROR{CYAN}]{RED} {message}{DEFAULT_COLOR}", file=sys.stderr)


def fatal_error(error_message: str, *info_messages: str) -> None:
    """Displays and logs an fatal error to the standard error stream and exits.
    Args:
        error_message : The fatal error message to display.
        *info_messages: Optional informational messages to display after the error.
    """
    error(error_message)
    for info_message in info_messages:
        print(f" {CYAN}\u24d8  {info_message}{DEFAULT_COLOR}", file=sys.stderr)
    exit(1)


#-------------------------- LOADING CONFIGURATION --------------------------#

def read_filename(line: str) -> str:
    """Reads a filename from a line of text.

    Raises a fatal error if the filename contains spaces.
    Args:
        line: The line of text containing the filename.
    Returns:
        The filename, stripped of leading periods and slashes.
    """
    filename = line.strip()
    while filename.startswith(".") or filename.startswith("/"):
        filename = filename[1:]
    if " " in filename:
        fatal_error(f"Filename cannot contain spaces: {filename}", "Please check the input.")
    return filename


def read_keyvalue(line):
    """Read a line of text in the format "key: value"

    Args:
        line (str): The line of text to parse.
    Returns:
        tuple: A tuple containing the key and value.
    """
    key, value = line.split(':', 1)
    key, value = key.strip(), value.strip()
    if value.startswith("'"):
        value = value.strip("'")
    return key, value


def extract_text(filepath: str, start_delimiter: str) -> str:
    """Extracts text between start_delimiter and a line with at least 4 hyphens

    This function reads a file line by line.
    It captured all lines starting from the specified `start_delimiter` until
    it encounters a line  that begins with at least four hyphen-minuses ('---').

    Args:
        filepath        (str): The path to the file to read.
        start_delimiter (str): The delimiter marking the start of the text to extract.
    Returns:
        The extracted text between the delimiters, or an empty string if no delimiter is found.
    """
    extracted_text = ""
    capturing = False
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip() == start_delimiter:
                capturing = True
            elif capturing and line.startswith('----'):
                break
            elif capturing:
                extracted_text += line
    return extracted_text


def load_configs(config_path):
    """Loads configurations from a file.

    Args:
        config_path: The path to the config file.
    Returns:
        A tuple containing a dictionary of configurations by filename
        and a dictionary of global variables.
    """
    configs_by_filename = {}
    config      = {}
    global_vars = {}
    filename    = ''
    config_dir  = os.path.dirname(config_path)

    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                # it's a comment, skip it
                continue

            elif line.startswith("@"):
                # it's a global variable
                key, value = read_keyvalue(line[1:])
                global_vars[key] = value

            elif line.startswith("./"):
                # it's a filename, start of a new config
                if filename and config:
                    configs_by_filename[filename] = config
                filename      = read_filename(line)
                config = {}

            else:
                # it's a config variable
                key, value = read_keyvalue(line)
                if value.startswith("@"):
                    path_ = os.path.join(config_dir, value[1:])
                    value = extract_text(path_, f"./{filename}").strip()
                config[key] = value
                continue

    # if any config is pending, add it to the dictionary
    if filename and config:
        configs_by_filename[filename] = config

    return configs_by_filename, global_vars


#---------------------------------- NODES ----------------------------------#

def get_title(node: dict) -> str:
    if node is None:
        return None
    return node.get('title', node.get('type', ''))

def get_type(node: dict) -> str:
    if node is None:
        return None
    return node.get('type', '')

def get_nodes_by_id(all_nodes:list) -> dict:
    nodes_by_id = {}
    for node in all_nodes:
        id = node.get('id')
        nodes_by_id[id] = node
    return nodes_by_id

def get_links_by_id(all_links:list) -> dict:
    links_by_id = {}
    for link in all_links:
        id = link[0]
        links_by_id[id] = link
    return links_by_id


#----------------------------- WORKFLOW CLASS ------------------------------#
class Workflow:
    """Represents a workflow with a name and a list of steps.
    """

    def __init__(self, data):
        """Initializes a new Workflow object.
        """
        nodes = data.get('nodes')
        links = data.get('links')

        nodes_by_id = {}
        for node in nodes:
            if 'id' in node:
                nodes_by_id[node['id']] = node

        links_by_id = {}
        for link in links:
            if len(link)>=5:
                links_by_id[link[0]] = link

        self.data        = data
        self.nodes       = nodes
        self.links       = links
        self.nodes_by_id = nodes_by_id
        self.links_by_id = links_by_id


    def save_to_json(self, filename: str):
        """Saves the workflow to a JSON file.
        Args:
            filename (str): The name of the JSON file.
        """
        with open(filename, "w") as f:
            json.dump(self.data, f,
                      indent=(JSON_INDENT if JSON_INDENT>0 else None),
                      ensure_ascii=False)


    @staticmethod
    def from_json(filename: str):
        """Loads a Workflow object from a JSON file.
        Args:
            filename (str): The name of the JSON file.
        Returns:
            A Workflow object.
        """
        with open(filename, "r") as f:
            data = json.load(f)
            return Workflow(data)


    def copy(self):
        """Creates a copy of the workflow.
        Returns:
            A new Workflow object with the same data as the original.
        """
        copied_data = self.data.copy()
        return Workflow(copied_data)


    # retorna todos los nodos conectados a un output, resolviendo los reroutes
    # output = node.outputs[n]
    def get_all_connected_nodes(self, node: dict, output_index: int) -> list:
        outputs = node.get('outputs')
        if not outputs or output_index>=len(outputs):
            return None
        output    = outputs[output_index]
        links_ids = output.get('links',[])

        nodes = []
        for link_id in links_ids:
            link = self.links_by_id[ link_id ]
            node = self.nodes_by_id[ link[3] ]
            if get_type(node)=="Reroute":
                nodes.extend( self.get_all_connected_nodes(node,0) )
            else:
                nodes.append(node)
        return nodes

    def set_node(self, node, value):

        if get_type(node)=="PrimitiveNode":
            nodes = self.get_all_connected_nodes(node, 0)
            print("## node:", get_title(node))
            print("## connections:", [get_title(node) for node in nodes])
            #print("## widget_name", widget_name)


#---------------------------- CREATING WORKFLOW ----------------------------#

def create_workflow(template: Workflow, config: dict, global_vars: dict) -> Workflow:

    # create a copy of the workflow to avoid modifying the template
    workflow = template.copy()

    if not template.nodes:
        warning("Pareciera no haber ningun nodo en el template suministrado")
        return workflow

    for node in workflow.nodes:
        title = get_title(node)
        value = config.get(title)
        if value:
            workflow.set_node( node, value )

    return workflow


def make(filename: str, config: dict, global_vars: dict) -> None:
    """Generates a JSON workflow file based on a template and configuration.

    Args:
        filename     (str): The name of the output JSON file.
        config      (dict): A dict containing configuration values to be applied to the template.
        global_vars (dict): A dict containing global variables used in the template.
    """
    workflow_filename = filename if os.path.splitext(filename)[1] else filename + '.json'
    template_filename = global_vars.get('TEMPLATE')

    if not template_filename:
        fatal_error("No template is defined in the configuration.",
                    "You must define the global variable @TEMPLATE in the configuration.")
    if not os.path.isfile(template_filename):
        fatal_error(f"The template file '{template_filename}' does not exist.",
                    "Check the value assigned to the @TEMPLATE variable.")

    # load the JSON template from the file
    template = Workflow.from_json(template_filename)

    message(f"Building '{workflow_filename}'")
    workflow = create_workflow(template, config, global_vars)

    # Save the JSON workflow to a file
    workflow.save_to_json(workflow_filename)


def process(target: str, configs_by_filename: dict, global_vars: dict) -> None:
    """Processes a target based on provided configurations and global variables.

    Args:
        target              (str) : The target to process. Can be 'clean', 'all', or a specific filename.
        configs_by_filename (dict): A dictionary mapping filenames to their corresponding configuration.
        global_vars         (dict): A dictionary containing global variables used during processing.
    """
    if target == 'clean':
        for filename, _ in configs_by_filename.items():
            if os.path.isfile(filename):
                message(f"Removing '{filename}'")
                os.remove(filename)

    elif target == 'all':
        for filename, config in configs_by_filename.items():
            make(filename, config, global_vars)

    else:
        filename = target
        config   = configs_by_filename.get(filename)
        make(filename, config, global_vars)


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    global JSON_INDENT
    parser = argparse.ArgumentParser(
        description="Create workflow files based on the config."
    )
    parser.add_argument('-c', '--config', metavar='FILE',
        help="Read FILE as the configurations (default: configurations.txt)"
    )
    parser.add_argument('-i', '--indent', type=int,
        help=f"Indentation level for the generated JSON files (default: {JSON_INDENT})"
    )
    parser.add_argument('-v', '--version', action='version', version='wmake 0.2',
        help="Show version information and exit."
    )
    parser.add_argument('target', nargs='*', default=['all'],
        help="The name(s) of the workflow file(s) to create. "
             "'all' to create all workflow files specified in the config. "
             "'clean' to remove all workflow files specified in the config."
    )
    args = parser.parse_args()

    # set JSON indentation
    if args.indent:
        JSON_INDENT=args.indent

    # determine the config file path
    if args.config:
        config_path = args.config
    elif os.path.exists(CONFIG_DEFAULT_NAME):
        config_path = CONFIG_DEFAULT_NAME
    else:
        config_path = os.path.join(SCRIPT_DIRECTORY, CONFIG_DEFAULT_NAME)


    # check if the config file exists
    if not os.path.exists(config_path):
        fatal_error(f"config file not found: {config_path}",
                    "Please provide a valid config file path or ensure the default config file exists.")

    # load the configurations
    configs_by_filename, global_vars = load_configs(config_path)

     # process each target
    for target in args.target:
        process(target, configs_by_filename, global_vars)


if __name__ == "__main__":
    main()
