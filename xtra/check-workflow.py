import argparse
import json

RED   = "\033[91m"
GREEN = "\033[92m"
ENDC  = "\033[0m"

def get_unpinned_nodes(workflow):
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

    return unpinned_nodes

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


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(
        description = "Analyzes ComfyUI workflow files to check for issues."
        )
    parser.add_argument("workflow_file", nargs="+", help="ComfyUI workflow file(s) (.json) to analyze.")
    parser.add_argument("--verbose", action="store_true", help="Show additional information about unpinned nodes.")

    args = parser.parse_args()

    for filename in args.workflow_file:

        print()
        print(filename)
        with open(filename, 'r') as f:
            workflow = json.load(f)

        unpinned_nodes = get_unpinned_nodes(workflow)
        pos_bug_count, size_bug_count = check_node_dimensions(workflow);

        if not unpinned_nodes:
            print(f"{GREEN}  - All nodes are pinned{ENDC}")

        if pos_bug_count > 0:
            print(f"{RED}  - Potential issues with 'pos' attribute : {pos_bug_count}{ENDC}")
        if size_bug_count > 0:
            print(f"{RED}  - Potential issues with 'size' attribute: {size_bug_count}{ENDC}")

        if unpinned_nodes:
            print(f"{RED}  - Found {len(unpinned_nodes)} unpinned nodes:{ENDC}")
            for node in unpinned_nodes:
                #print(f"       {node.name}  ({node.x}, {node.y})")
                print(f"       ({node.x:>4},{node.y:>4}) {node.name}")


if __name__ == '__main__':
    main()
