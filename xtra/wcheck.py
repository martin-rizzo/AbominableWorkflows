import os
import sys
import json
import argparse
try:
    # PIL is used to read workflow data embedded in images
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    print("Warning: The Pillow library is not installed: functionality will be limited.")
    PIL_AVAILABLE = False


# ANSI escape codes for colored terminal output
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
DEFAULT_COLOR = '\033[0m'


def disable_colors():
    """Set all color codes to empty strings, effectively disabling colored output."""
    global RED, GREEN, YELLOW, CYAN, DEFAULT_COLOR
    RED, GREEN, YELLOW, CYAN, DEFAULT_COLOR = '', '', '', '', ''

def is_terminal_output():
    """Check if the standard output is connected to a terminal."""
    return sys.stdout.isatty()

def get_unpinned_nodes(workflow: dict) -> (list, int):
    """Extracts unpinned nodes from a workflow

    This function extracts all nodes that are not pinned.

    Args:
        workflow (dict): A dictionary representing a workflow.

    Returns:
        list: A list of unpinned nodes, each represented as a namedtuple
              with 'name', 'x', and 'y' attributes.
    """
    unpinned_nodes = []

    nodes = workflow.get('nodes')
    if not nodes:
        return []

    for node in nodes:
        title       = node.get('title', node.get('type', '?'))
        flags       = node.get('flags')
        pinned_flag = flags and flags.get('pinned')
        position    = node.get('pos')

        # extract 'x' and 'y' coordinates
        # the coordinates can be located using 'app.canvas.canvas_mouse'
        x, y = 0, 0
        if isinstance(position, list):
            x, y = position[0], position[1]
        elif isinstance(position, dict):
            x = position.get('0', x)
            y = position.get('1', y)

        # append unpinned nodes
        if not pinned_flag:
            unpinned_node = type('Node', (), {'name': title, 'x': x, 'y': y})
            unpinned_nodes.append(unpinned_node)

    return unpinned_nodes, len(nodes)

def is_two_element_array_like(data):
    """Checks if the input data is a two-element array-like structure

    This function checks if the input data is either a list or a dictionary.
    If it's a list, it verifies if it has exactly two elements.
    If it's a dictionary, it checks if it contains keys '0' and '1'.

    Args:
        data: The input data to be checked.

    Returns:
        True if the input data is a two-element array-like structure
    """
    if isinstance(data, list):
        return len(data) == 2
    elif isinstance(data, dict):
        return len(data) == 2 and '0' in data and '1' in data
    else:
        return False

def check_node_dimensions(workflow):
    """Checks if the 'pos' and 'size' node attr are valid two element array-like structures

    This function iterates through the 'nodes' in a given workflow and checks
    if the 'pos' and 'size' attributes of each node are valid two element
    array-like structures.

    Args:
        workflow: The workflow dictionary containing the 'nodes' list.

    Returns:
        A tuple containing the number of nodes with invalid 'pos' and 'size'
        attributes, respectively.
    """
    pos_bug_count  = 0
    size_bug_count = 0

    nodes = workflow.get('nodes')
    if not nodes:
        return None

    for node in nodes:
        pos  = node.get('pos')
        size = node.get('size')
        if pos and not is_two_element_array_like(pos):
            pos_bug_count += 1
        if size and not is_two_element_array_like(size):
            size_bug_count += 1

    return pos_bug_count, size_bug_count


def get_workflow_view(workflow):
    view_x, view_y, view_scale = 0.0, 0.0, 1.0
    ds = workflow.get('extra',{}).get('ds',{})
    if 'offset' in ds and len(ds['offset'])>=2:
        view_x = ds['offset'][0]
        view_y = ds['offset'][1]
    if 'scale' in ds:
        view_scale = ds['scale']
    return view_x, view_y, view_scale


#---------------------------- READING WORKFLOW -----------------------------#

def read_workflow_from_json(filename: str) -> dict:
    """Reads workflow data from a JSON file
    Args:
        filename (str): The path to the JSON file.
    Returns:
        A dictionary containing the workflow data,
        or None if no workflow data is found.
    """
    try:
        workflow = None
        with open(filename, 'r') as f:
            workflow = json.load(f)
        return workflow
    except (FileNotFoundError, IOError, json.JSONDecodeError):
        return None


def read_workflow_from_png(filename: str) -> dict:
    """Reads workflow data embedded in a PNG image
    Args:
        filename (str): The path to the PNG image file.
    Returns:
        A dictionary containing the workflow data,
        or None if no workflow data is found.
    """
    if not PIL_AVAILABLE:
        return None
    try:
        workflow = None
        with Image.open(filename) as image:
            if 'prompt' in image.info and 'workflow' in image.info:
                workflow = image.info.get('workflow')
        return json.loads(workflow) if isinstance(workflow,str) else None
    except (IOError, OSError):
        return None


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(
        description = "Analyzes ComfyUI workflow files to check for issues."
        )
    parser.add_argument("workflow_file" , nargs="+",           help="ComfyUI workflow file(s) (.json) to analyze.")
    parser.add_argument('-c', '--color' , action="store_true", help="use color output when connected to a terminal")
    parser.add_argument('--color-always', action="store_true", help="always use color output")
    parser.add_argument("--verbose"     , action="store_true", help="Show additional information about unpinned nodes.")

    args = parser.parse_args()

    # determine if color should be used
    use_color = args.color_always or (args.color and is_terminal_output())
    if not use_color:
        disable_colors()

    for filename in args.workflow_file:
        print()
        print(filename)

        _, extension = os.path.splitext(filename)
        if extension.lower() == '.json':
            workflow = read_workflow_from_json(filename)
        elif extension.lower() == '.png':
            workflow = read_workflow_from_png(filename)
        else:
            workflow = None

        if not workflow:
            print(f"{YELLOW} - Imposible leer el workflow del archivo.{DEFAULT_COLOR}")
            continue

        unpinned_nodes, total_count   = get_unpinned_nodes(workflow)
        pos_bug_count, size_bug_count = check_node_dimensions(workflow);
        view_x, view_y, view_scale    = get_workflow_view(workflow)
        view_displaced = view_x != 0 or view_y != 0 or view_scale != 1

        if not unpinned_nodes and not view_displaced:
            print(f"{GREEN}  - The {total_count} nodes are pinned and view is at the origin.{DEFAULT_COLOR}")

        if pos_bug_count > 0:
            print(f"{RED}  - Potential issues with 'pos' attribute : {pos_bug_count}{DEFAULT_COLOR}")
        if size_bug_count > 0:
            print(f"{RED}  - Potential issues with 'size' attribute: {size_bug_count}{DEFAULT_COLOR}")

        if view_displaced:
            print(f"{RED} - The view is not at the origin.{DEFAULT_COLOR}")

        if unpinned_nodes:
            print(f"{RED}  - Found {len(unpinned_nodes)} unpinned nodes:{DEFAULT_COLOR}")
            for node in unpinned_nodes:
                #print(f"       {node.name}  ({node.x}, {node.y})")
                print(f"       ({node.x:>4},{node.y:>4}) {node.name}")

    print()

if __name__ == '__main__':
    main()
