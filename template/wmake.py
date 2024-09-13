"""
  File    : wmake.py
  Brief   : Creates workflows from a template and a configuration file
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
import argparse

# ANSI escape codes for colored terminal output.
CYAN   = '\033[96m'
YELLOW = '\033[93m'
RED    = '\033[91m'
DEFAULT_COLOR = '\033[0m'

# Get the directory of the current Python script.
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

CONFIG_DEFAULT_NAME = 'configurations.txt'

#----------------------------- ERROR MESSAGES ------------------------------#

def warning(message: str) -> None:
    """
    Displays and logs a warning message to the standard error stream.
    Args:
        message: The warning message to display.
    """
    print(f"{CYAN}[{YELLOW}WARNING{CYAN}]{YELLOW} {message}{DEFAULT_COLOR}", file=sys.stderr)


def error(message: str) -> None:
    """
    Displays and logs an error message to the standard error stream.
    Args:
        message: The error message to display.
    """
    print(f"{CYAN}[{RED}ERROR{CYAN}]{RED} {message}{DEFAULT_COLOR}", file=sys.stderr)


def fatal_error(error_message: str, *info_messages: str) -> None:
    """
    Displays a fatal error message, logs it to the standard error stream,
    and exits the script with status code 1.
    Optionally displays informational messages after the error.

    Args:
        error_message: The fatal error message to display.
        *info_messages: Optional informational messages to display after the error.
    """
    error(error_message)

    # Print informational messages, if any were provided
    for info_message in info_messages:
        print(f" {CYAN}\xF0\x9F\x9B\x88  {info_message}{DEFAULT_COLOR}", file=sys.stderr)

    exit(1)


#--------------------------- LOAD CONFIGURATION ----------------------------#

def read_filename(line: str) -> str:
    """
    Reads a filename from a line of text.
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
    """
    Read a line of text in the format "key: value"

    Args:
        line (str): The line of text to parse.

    Returns:
        tuple: A tuple containing the key and value.

    Example:
        >>> read_keyvalue("name: John Doe")
        ('name', 'John Doe')
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
        str: The extracted text between the delimiters, or an empty string if no text is found.
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

def load_configuration(config_path):
    variables       = {}
    instructions    = {}
    file_identifier = ''
    instructions_by_file = {}
    config_dir = os.path.dirname(config_path)

    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                # it's a comment, skip it
                continue

            elif line.startswith("@"):
                key, value = read_keyvalue(line[1:])
                variables[key] = value

            elif line.startswith("./"):
                if file_identifier and instructions:
                    instructions_by_file[file_identifier] = instructions
                file_identifier = read_filename(line)

            else:
                key, value = read_keyvalue(line)
                if value.startswith("@"):
                    path_ = os.path.join(config_dir, value[1:])
                    value = extract_text(path_, f"./{file_identifier}").strip()
                instructions[key] = value
                continue

    if file_identifier and instructions:
        instructions_by_file[file_identifier] = instructions
    return variables, instructions_by_file


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(description="Automates workflow creation using templates and configuration files.")
    parser.add_argument("template_file", help="Path to the workflow template file")
    parser.add_argument("--config", "-c", help="Path to the configuration file", default=None)
    args = parser.parse_args()

    # determine the configuration file path
    if args.config:
        config_name = args.config
    elif os.path.exists(CONFIG_DEFAULT_NAME):
        config_name = CONFIG_DEFAULT_NAME
    else:
        config_name = os.path.join(SCRIPT_DIRECTORY, CONFIG_DEFAULT_NAME)

    # check if the configuration file exists
    if not os.path.exists(config_name):
        fatal_error(f"Configuration file not found: {config_name}",
                    "Please provide a valid configuration file path or ensure the default configuration file exists.")

    # load the configuration
    variables, instructions_by_file = load_configuration(config_name)

    # print the loaded configuration
    print("Variables:", variables)
    print("Instructions:", instructions_by_file)


if __name__ == "__main__":
    main()
