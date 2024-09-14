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

# Default name for the configurations file
DEFAULT_CONFIGS_NAME = 'configurations.txt'

# Default extension for workflow files
DEFAULT_WORKFLOW_EXT = '.json'

# Indentation level for JSON output
JSON_INDENT=2

# List of available samplers in ComfyUI
SAMPLER_NAMES = [
    "euler", "euler_cfg_pp", "euler_ancestral", "euler_ancestral_cfg_pp", "heun", "heunpp2","dpm_2", "dpm_2_ancestral",
    "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_2s_ancestral_cfg_pp", "dpmpp_sde", "dpmpp_sde_gpu",
    "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm",
    "ipndm", "ipndm_v", "deis", "ddim", "uni_pc", "uni_pc_bh2"
    ]

# List of available schedulers in ComfyUI
SCHEDULER_NAMES = [
    "normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform", "beta"
    ]


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


#-------------------------- CONFIGURATIONS CLASS ---------------------------#
class Configurations:

    def __init__(self,
                 filenames,
                 parameters_by_target,
                 wildcards_by_target,
                 global_vars):
        """Initializes a new Configuration object.
        """
        self.filenames = filenames
        self.parameters_by_target = parameters_by_target
        self.wildcards_by_target  = wildcards_by_target
        self.global_vars          = global_vars

    @classmethod
    def from_file(cls, configs_path: str) -> 'Configurations':
        """Loads a Configurations object from a file.

        Args:
            config_path: The path to the config file.
        Returns:
            A Configuration object.
        """
        parameters_by_target = {}
        wildcards_by_target  = {}
        parameters    = {}
        wildcards     = []
        global_vars   = {}
        all_filenames = set()
        filename      = ''
        target        = ''
        configs_dir   = os.path.dirname(configs_path)

        with open(configs_path, 'r') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    # it's a comment:
                    #  skip the line
                    continue

                elif line.startswith("@"):
                    # it's a global variable declaration:
                    #  store it in the 'global_vars' dictionary
                    key, strvalue = Configurations._read_keyvalue(line[1:])
                    global_vars[key] = strvalue

                elif line.startswith("./"):
                    # it's a filename declaration:
                    #  1) store the collected 'parameters' for the current target
                    #  2) start a new list of 'parameters' for the new target.
                    if filename and target:
                        all_filenames.add(filename)
                        parameters_by_target[target] = parameters
                        wildcards_by_target[target]  = wildcards
                    parameters = {}
                    wildcards  = []
                    # filenames always have an extension,
                    # targets are filenames without the extension
                    filename     = Configurations._read_filename(line)
                    target, _ext = os.path.splitext(filename)
                    if not _ext:
                        filename += DEFAULT_WORKFLOW_EXT

                else:
                    # it's a parameter declaration:
                    #  collect the parameter in the 'parameters' dictionary
                    key, strvalue = Configurations._read_keyvalue(line,
                                              extern_dir       = configs_dir,
                                              extern_delimiter = f"./{filename}")
                    # parameter names that start with "NODE."
                    # may be defined as global vars
                    if key.startswith('NODE.'):
                        if key in global_vars:
                            key = global_vars[key]
                    # corregir value para que si representa un numero
                    # tenga el tipo correcto de dato
                    value = Configurations._fix_value(strvalue)

                    # if the parameter name contains '*'
                    # it is added to the 'wildcards' list
                    if '*' in key:
                        parts = key.split('*', 1)
                        wildcards.append( (parts[0], parts[1], value) )
                    else:
                        parameters[key] = value

        # if 'parameters' and 'wildcards' are pending,
        # add them to the dictionaries
        if filename and target:
            all_filenames.add(filename)
            parameters_by_target[target] = parameters
            wildcards_by_target[target]  = wildcards

        return cls(all_filenames, parameters_by_target, wildcards_by_target, global_vars)


    def get_global(self, varname: str):
        return self.global_vars.get(varname)


    def get(self, target: str, parameter: str):
        """Retrieves the value of a parameter for a specified workflow.

        This function searches for the value of a configuration parameter
        for the specified workflow target. If the exact parameter is not found,
        it checks for matching wildcards.

        Args:
            target    (str): The name of the workflow where the parameter belongs,
                             (generally the filename without an extension).
            parameter (str): The name of the parameter to retrieve.

        Returns:
            The value of the parameter if found.
            None, if the parameter is not found.
        """
        target = os.path.splitext(target)[0]
        parameters = self.parameters_by_target.get(target)
        value      = parameters.get(parameter) if parameters is not None else None
        if value is not None:
            return value

        wildcards = self.wildcards_by_target.get(target)
        for wildcard in wildcards:
            if parameter.startswith(wildcard[0]) and parameter.endswith(wildcard[1]):
                return wildcard[2]

        return None


    @staticmethod
    def _read_filename(line: str) -> str:
        """Reads a filename from a line of text.
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


    @staticmethod
    def _read_keyvalue(line, extern_dir=None, extern_delimiter=None) -> tuple:
        """Reads a line of text in the format "key: value"

        This function handles various cases for the value:
        - If the value starts with "@", it assumes it's a ref to an external file.
        The function then reads the file and extracts the value using the delimiter.
        - If the value starts with a single quote ('), it assumes it's a string literal.

        Args:
            line             (str): The line of text to parse.
            extern_dir       (str): The directory where external files are located.
            extern_delimiter (str): The delimiter used to extract the value from external file.
        Returns:
            A tuple containing the key and value.
        """
        key, value = line.split(':', 1)
        key, value = key.strip(), value.strip()

        # handle external file reference
        if value.startswith("@")      \
           and extern_dir is not None \
           and extern_delimiter is not None:

            path_ = os.path.join(extern_dir, value[1:])
            value = Configurations._extract_text_from_file(path_, extern_delimiter).strip()

        # handle string literal
        elif value.startswith("'"):
            value = value.strip("'")

        return key, value

    @staticmethod
    def _extract_text_from_file(filepath: str, start_delimiter: str) -> str:
        """Extracts text from a file starting from a specific delimiter.

        This function reads the file line by line and begins capturing text
        when it encounters either:
        1. The specified `start_delimiter`, or
        2. The global wildcard delimiter ">*<".
        The text capture stops when a line starts with a '>' followed by
        two or more hyphens ('>--').

        Args:
            filepath        (str): The path to the file to read.
            start_delimiter (str): The delimiter that marks where to start extracting text.
        Returns:
            The text extracted between the delimiters,
            or an empty string if no valid delimiters are found.
        """
        extracted_text = ""
        capturing = False
        with open(filepath, 'r') as file:
            for line in file:
                if line.strip() == start_delimiter or line.strip() == '>*<':
                    capturing = True
                elif capturing and line.startswith('>--'):
                    break
                elif capturing:
                    extracted_text += line
        return extracted_text

    @staticmethod
    def _fix_value(strvalue:str):
        try:
            return int(strvalue)
        except ValueError:
            try:
                return float(strvalue)
            except ValueError:
                return strvalue


#---------------------------------- NODES ----------------------------------#

def get_name(node: dict) -> str:
    assert node is not None
    return node.get('title', node.get('type', ''))

def get_type(node: dict) -> str:
    assert node is not None
    return node.get('type', '')

def get_values(node: dict) -> list:
    assert node is not None
    return node.get('widgets_values', [])

def get_value_kind(value) -> str:
    if isinstance(value, str):
        if value in SAMPLER_NAMES:
            return "sampler"
        elif value in SCHEDULER_NAMES:
            return "schedulers"
        else:
            return "string"
    else:
        return str(type(value))

def set_node_title(node: dict, title: str):
    assert isinstance(node, dict)
    title = str(title)
    if 'title' in node:
        node['title'] = title

def set_node_value(node: dict, value, index: int=0):
    assert isinstance(node, dict)
    widgets_values = node.get('widgets_values', [])
    if index<len(widgets_values):
        original_type = type(widgets_values[index])
        widgets_values[index] = original_type(value)

def modify_node_value(node: dict,
                      new_value,
                      old_value  = None,
                      value_kind = None,
                      node_name  = None
                      ):
    assert node is not None

    if node_name is None:
        node_name = f"'{get_name(node)}'"

    found_count    = 0
    found_index    = None
    widgets_values = node.get('widgets_values', [])
    for index in range(len(widgets_values)):

        if old_value is not None:
            if isinstance(widgets_values[index], type(old_value)) \
               and widgets_values[index] == old_value:
                found_index  = index
                found_count += 1

        if value_kind is not None:
            if get_value_kind(widgets_values[index]) == value_kind:
                found_index  = index
                found_count += 1

    if found_count == 0:
        warning(f"The configuration {DEFAULT_COLOR}{node_name} = {new_value}{YELLOW} could not be applied.",
                 "(no entry matching the expected type was found).")
        return

    if found_count > 1:
        warning(f"The configuration {DEFAULT_COLOR}{node_name} = {new_value}{YELLOW} could not be applied.",
                 "(multiple matches were found creating ambiguity).")
        return

    original_type = type(widgets_values[found_index])
    widgets_values[found_index] = original_type(new_value)


#----------------------------- WORKFLOW CLASS ------------------------------#
class Workflow:
    """Represents a workflow with a name and a list of steps.
    """

    def __init__(self, data):
        """Initializes a new Workflow object.
        """
        nodes  = data.get('nodes' , [])
        links  = data.get('links' , [])
        groups = data.get('groups', [])

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
        self.groups      = groups
        self.nodes_by_id = nodes_by_id
        self.links_by_id = links_by_id


    def set_node(self, node: dict, value):
        """Sets the value of a node.

        It handles different types of nodes:
          - Primitive node   : modifies the value in the node and all connected nodes.
          - Single-Value node: sets the single configurable value of the node.
          - Note node        : sets the first line as the title and the rest as the content.
          - Other node types : displays a warning message, not yet supported.

        Args:
            node (dict): The node to set the value for.
            value (any): The new value to set.
        """

        # when encountering a `PrimitiveNode`,
        # modify the value in the node AND ALL DIRECTLY CONNECTED NODES
        if get_type(node)=="PrimitiveNode":
            new_value       = value
            old_value       = get_values(node)[0]
            connected_nodes = self.get_all_connected_nodes(node, 0)
            primitive_name  = get_name(node)

            modify_node_value(node, new_value, old_value)
            for connected_node in connected_nodes:
                modify_node_value(connected_node, new_value, old_value,
                                  node_name=f"'{primitive_name}'->'{get_name(connected_node)}'")

        # when encountering a `Note` node,
        # the first line of the text will be the title of the note,
        # the rest of the text will be the content
        elif get_type(node)=="Note":
            lines = str(value).splitlines()
            if len(lines)>1:
                set_node_title( node, lines[0]             )
                set_node_value( node, "\n".join(lines[1:]) )
            else:
                set_node_value( node, "\n".join(lines) )

        # when encountering a node with only one configurable value,
        # simply set that value
        elif len(get_values(node))==1:
            set_node_value( node, value )

        # para any other nodo
        # intentar modificar valor que tenga el mismo kind de dato
        else:
            modify_node_value( node, value, value_kind=get_value_kind(value) )
            # warning(f"The configuration {DEFAULT_COLOR}'{get_name(node)}' = {value}{YELLOW} could not be applied",
            #          "(this type of value/node is not supported by wmake).")


    def set_group(self, group: dict, value: str):
        """Sets the value of a group.
        Args:
            group (dict): The group to set the value for.
            value (str) : The new value to set.
        """
        if not isinstance(value, str):
            return
        group['title'] = value


    @classmethod
    def from_json(cls, filename: str):
        """Loads a Workflow object from a JSON file.
        Args:
            filename (str): The name of the JSON file.
        Returns:
            A Workflow object.
        """
        with open(filename, "r") as f:
            data = json.load(f)
            return cls(data)


    def save_to_json(self, filename: str):
        """Saves the workflow to a JSON file.
        Args:
            filename (str): The name of the JSON file.
        """
        with open(filename, "w") as f:
            json.dump(self.data, f,
                      indent=(JSON_INDENT if JSON_INDENT>0 else None),
                      ensure_ascii=False)


    def copy(self):
        """Creates a copy of the workflow.
        Returns:
            A new Workflow object with the same data as the original.
        """
        copied_data = self.data.copy()
        return Workflow(copied_data)


    def get_all_connected_nodes(self, node: dict, output_index: int) -> list:
        """Returns all nodes connected to a specific output, resolving reroutes.
        Args:
            node        (dict): The node to analyze.
            output_index (int): The index of the output to analyze.

        Returns:
            A list of all connected nodes, including those connected through reroutes.
        """
        outputs = node.get('outputs')
        if not outputs or output_index>=len(outputs):
            return None
        output    = outputs[output_index]
        links_ids = output.get('links',[])

        nodes = []
        for link_id in links_ids:
            link = self.links_by_id[ link_id ]
            # get the node connected to the current link
            connected_node = self.nodes_by_id[ link[3] ]
            if get_type(connected_node)=="Reroute":
                # if the connected node is a reroute,
                # recursively get all connected nodes from its output
                nodes.extend( self.get_all_connected_nodes(connected_node,0) )
            else:
                # if the connected node is NOT a reroute,
                # add it to the list
                nodes.append(connected_node)
        return nodes


#--------------------- CREATING WORKFLOW FROM TEMPLATE ---------------------#

def create_workflow(filename: str,
                    template: Workflow,
                    configs : Configurations) -> Workflow:

    # create a copy of the workflow to avoid modifying the template
    workflow = template.copy()

    if not template.nodes:
        warning("Pareciera no haber ningun nodo en el template suministrado")
        return workflow

    for node in workflow.nodes:
        param_name = get_name(node)
        value      = configs.get(filename, param_name)
        if value is not None:
            workflow.set_node( node, value )

    for group in workflow.groups:
        param_name = get_name(group)
        value      = configs.get(filename, param_name)
        if value is not None:
            workflow.set_group( group, str(value) )

    return workflow


def make(filename: str, configs: Configurations) -> None:
    """Generates a JSON workflow file based on a template and configuration.
    Args:
        filename         (str): The name of the output JSON file.
        config (Configuration): A object with the configuration values to be applied to the template.
    """
    workflow_filename = filename if os.path.splitext(filename)[1] else filename + '.json'
    template_filename = configs.get_global('TEMPLATE')

    if not template_filename:
        fatal_error("No template is defined in the configuration.",
                    "You must define the global variable @TEMPLATE in the configuration.")
    if not os.path.isfile(template_filename):
        fatal_error(f"The template file '{template_filename}' does not exist.",
                    "Check the value assigned to the @TEMPLATE variable.")

    # load the JSON template from the file
    template = Workflow.from_json(template_filename)

    message(f"Building '{workflow_filename}'")
    workflow = create_workflow(filename, template, configs)

    # Save the JSON workflow to a file
    workflow.save_to_json(workflow_filename)


def process(target: str, configs: Configurations) -> None:
    """Processes a target based on provided configurations.
    Args:
        target (str): The target to process, can be 'clean', 'all', or a specific filename.
        config (Configuration): A object with the configuration values.
    """
    if target == 'clean':
        for filename in configs.filenames:
            if os.path.isfile(filename):
                message(f"Removing '{filename}'")
                os.remove(filename)

    elif target == 'all':
        for filename in configs.filenames:
            make(filename, configs)

    else:
        make(filename, configs)


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
        configs_path = args.config
    elif os.path.exists(DEFAULT_CONFIGS_NAME):
        configs_path = DEFAULT_CONFIGS_NAME
    else:
        configs_path = os.path.join(SCRIPT_DIRECTORY, DEFAULT_CONFIGS_NAME)


    # check if the config file exists
    if not os.path.exists(configs_path):
        fatal_error(f"Configurations file not found: {configs_path}",
                    "Please provide a valid file path or ensure the default config file exists.")

    # load the configurations
    configs = Configurations.from_file(configs_path)

     # process each target
    for target in args.target:
        process(target, configs)


if __name__ == "__main__":
    main()
