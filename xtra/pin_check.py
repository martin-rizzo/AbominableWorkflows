import argparse
import json


def get_unpinned_nodes(filename):
    """Extracts unpinned nodes from a workflow JSON file.

    This function reads a workflow JSON file and extracts all nodes that are not
    pinned. It parses the node's title, position (x, y coordinates), and pinned
    flag.

    Args:
        filename (str): The path to the workflow JSON file.

    Returns:
        list: A list of unpinned nodes, each represented as a namedtuple with
              'name', 'x', and 'y' attributes.
    """
    unpinned_nodes = []

    with open(filename, 'r') as f:
        workflow = json.load(f)

    for workflow_node in workflow['nodes']:
        title = workflow_node.get('title', workflow_node.get('type', '?'))

        flags = workflow_node.get('flags')
        pinned_flag = flags and flags.get('pinned')
        position = workflow_node.get('pos')

        # extract x and y coordinates
        x, y = 0, 0
        if isinstance(position, list):
            x, y = position[0], position[1]
        elif isinstance(position, dict):
            x = position.get('0', x)
            y = position.get('1', y)

        # append unpinned nodes
        if not pinned_flag:
            node = type('Node', (), {'name': title, 'x': x, 'y': y})
            unpinned_nodes.append(node)

    return unpinned_nodes


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(
        description = "Checks if ComfyUI workflows have all their nodes pinned."
        )
    parser.add_argument("workflow_file", nargs="+", help="ComfyUI workflow file(s) (.json) to analyze.")
    parser.add_argument("--verbose", action="store_true", help="Show additional information about unpinned nodes.")

    args = parser.parse_args()

    for filename in args.workflow_file:
        unpinned_nodes = get_unpinned_nodes(filename)
        if unpinned_nodes:
            print(f"File: {filename}")
            print("Unpinned nodes:")
            for node in unpinned_nodes:
                print(f"  - {node.name}  ({node.x}, {node.y})")
        else:
            print(f"All nodes in {filename} are pinned.")


if __name__ == '__main__':
    main()
