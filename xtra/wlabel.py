"""
  File    : add-label.py
  Brief   : Draws a label with the workflow name on each image.
  Author  : Martin Rizzo | <martinrizzo@gmail.com>
  Date    : Sep 15, 2024
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
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

# ANSI escape codes for colored terminal output
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
DEFAULT_COLOR = '\033[0m'

# Default height value used for an abominable image
DEFAULT_ABOMINABLE_HEIGHT = 1536

# Flag to display a warning if a font fails to load
SHOW_FONT_WARNING = True

# Hex color codes mapped to specific words for visual presentation
COLORS_BY_WORD = {
    "PHOTO"     : "#dd2525", # Red
    "PIXEL"     : "#008800", # Green
    "MILO"      : "#9b00ff", # Purple
    "INK"       : "#0021d1", # Blue
    "1GIRL"     : "#f2258a", # Pink
    "DARKFAN80" : "#4c516c", # Gray
    "WORKFLOW"  : "#dd2525", # - Red
    "WORKFLOWS" : "#dd2525", # - Red
}

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

def get_word_color(word: str, default_color: str=None) -> str:
    return COLORS_BY_WORD.get(word.upper(), default_color)

def ascent_diference(font1: ImageFont, font2: ImageFont) -> int:
    """Calculates the difference in ascent between two fonts.
    """
    ascent1, _ = font1.getmetrics()
    ascent2, _ = font2.getmetrics()
    return ascent1 - ascent2


def load_font(font_name: str, font_size: int) -> ImageFont:
    """Loads a font from a file.

    This function attempts to load a font from the specified file.
    If the font cannot be loaded, it uses the default font.

    Args:
        font_name (str): The path to the font file.
        font_size (int): The desired font size.
    Returns:
        PIL.ImageFont: The loaded font or the default font if loading failed.
    """
    global SHOW_FONT_WARNING
    try:
        font = ImageFont.truetype(font_name, font_size)
    except Exception:
        font = None
    if not font:
        if SHOW_FONT_WARNING:
            SHOW_FONT_WARNING = False
            warning(f"Could not load font from {font_name}. Using default font.")
        font = ImageFont.load_default()
    return font


def get_abominable_scale(image: Image) -> float:
    """Calculates the scale factor for an abominable image.
    Args:
        image (PIL.Image): The image to be scaled.
    Returns:
        float: The scale factor for the abominable image.
    """
    image_width, image_height = image.size
    if image_width>image_height:
        image_width, image_height = image_height, image_width
    return image_height/DEFAULT_ABOMINABLE_HEIGHT


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


#-------------------------------- BOX CLASS --------------------------------#
class Box(tuple):
    def __new__(cls, left, top=None, right=None, bottom=None):
        if isinstance(left,tuple) and len(left)==4:
            left, top, right, bottom = left[0], left[1], left[2], left[3]
        return super(Box, cls).__new__(cls, (left, top, right, bottom))

    @classmethod
    def bounding_for_text(cls, text: str, font: ImageFont):
        return cls( font.getbbox(text) )

    @classmethod
    def container_for_text(cls, text: str, font):
        ascent, descent = font.getmetrics()
        return cls( 0,0, font.getlength(text), ascent+descent )


    @property
    def left(self):
        return self[0]

    @property
    def top(self):
        return self[1]

    @property
    def right(self):
        return self[2]

    @property
    def bottom(self):
        return self[3]

    @property
    def width(self):
        return self[2] - self[0]

    @property
    def height(self):
        return self[3] - self[1]

    def get_size(self):
        """Returns the width and height of the box."""
        width = self.right - self.left
        height = self.bottom - self.top
        return width, height

    def get_pos(self, anchor=None):
        """Returns the position of the box based on the specified anchor.
        Args:
            anchor (str, optional): The anchor point to use. Valid values are:
                - 'lt':  Top-left corner (default).
                - 'rb':  Bottom-right corner.
                - 'rt':  Top-right corner.
                - 'lb':  Bottom-left corner.
        Returns:
            A Box containing the x and y coordinates of the specified anchor point.
        """
        if anchor is None or anchor == 'lt':
            return self.left, self.top
        elif anchor == 'rb':
            return self.right, self.bottom
        elif anchor == 'rt':
            return self.right, self.top
        elif anchor == 'lb':
            return self.left, self.bottom
        else:
            raise ValueError(f"Invalid anchor: {anchor}. Valid anchors are: 'lt', 'rb', 'rt', 'lb'.")

    def with_size(self, width, height):
        """Returns a new Box with the specified size."""
        return Box(self.left, self.top, self.left + width, self.top + height)

    def with_pos(self, left, top):
        """Returns a new Box with the specified top-left position."""
        width, height = self.get_size()
        return Box(left, top, left + width, top + height)

    def moved_to(self, x, y=None, anchor=None ):
        if isinstance(x,tuple) and len(x)>=2:
            x, y = x[0], x[1]
        currx, curry = self.get_pos(anchor)
        return self.moved_by( x-currx, y-curry)

    def moved_by(self, dx, dy):
        """Returns a new Box moved by (dx, dy)."""
        return Box(self.left + dx, self.top + dy, self.right + dx, self.bottom + dy)

    def centered_in(self, container_box):
        """Returns a new Box with the same size but centered within the provided container box."""
        offset_x = (container_box.left + container_box.right  - self.left - self.right )/2
        offset_y = (container_box.top  + container_box.bottom - self.top  - self.bottom)/2
        return self.moved_by(offset_x, offset_y)

    def __repr__(self):
        return f"Box(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom})"


#---------------------------- DRAWING THE LABEL ----------------------------#

def draw_two_word_label(image  : Image,
                        width  : int,
                        height : int,
                        word1: str, color1: str, font1: ImageFont,
                        word2: str, color2: str, font2: ImageFont
                        ) -> Image:
    """Draws a rectangle containing two words on an image.

    This function takes an image, two words, and draws a rectangle with
    a white background containing the two words centered within it.
    The rectangle is drawn in the bottom right corner of the image.

    Args:
        image    (PIL.Image) : The original image to be labeled.
        width        (int)   : The width of the label rectangle.
        height       (int)   : The height of the label rectangle.
        word1        (str)   : The first word of the label.
        color1       (str)   : The color of the first word.
        font1 (PIL.ImageFont): The font used for the first word.
        word2        (str)   : The second word of the label.
        color2       (str)   : The color of the second word.
        font2 (PIL.ImageFont): The font used for the second word.

    Returns:
        PIL.Image: The image with the label added.
    """
    image_width, image_height = image.size
    unit = Box.bounding_for_text('m', font1).width
    space_width = 0.2 * unit # space between the two words
    margin      = 1   * unit # minimum margin between the border and the text

    draw = ImageDraw.Draw(image)

    # calculate the space occupied by the two words
    word1_box = Box.container_for_text(word1, font1)
    word2_box = Box.container_for_text(word2, font2)
    total_width  = word1_box.width + word2_box.width + space_width
    total_height = max(word1_box.height, word2_box.height)
    total_box    = Box(0,0, total_width, total_height)

    # adjust the size of the rectangle to contain the two words
    minimum_width = margin + total_width + margin
    if width < minimum_width:
        width = minimum_width

    # draw the white rectangle
    radius    = height/3 # radius of the rectangle's corner
    whitebox1 = Box(0,0,width,height).moved_to( (image_width, image_height), anchor='rb' )
    whitebox2 = whitebox1.moved_by(-radius,radius).with_size( radius, whitebox1.height-radius )
    circlebox = whitebox1.moved_by(-radius,0).with_size( radius*2, radius*2 )
    draw.rectangle(whitebox1, fill="white")
    draw.rectangle(whitebox2, fill="white")
    draw.ellipse(  circlebox, fill="white")

    # center both words within the whitebox
    total_box = total_box.centered_in( whitebox1.moved_by(-radius/2,0) )

    # position word1 to the left of `total_box` and word2 to the right
    word1_box = word1_box.moved_to( total_box.left, total_box.top, anchor='lt')
    word2_box = word2_box.moved_to( total_box.right, total_box.top, anchor='rt')

    # align word1 with word2 since they have different font sizes
    word1_box = word1_box.moved_by(0, ascent_diference(font2, font1))

    # write the words and return the image
    draw.text(word1_box, word1, fill=color1, font=font1, anchor='la')
    draw.text(word2_box, word2, fill=color2, font=font2, anchor='la')
    return image


def add_label_to_image(image: Image, text: str, font_size: int) -> Image:
    """Adds a label with the text to the image

    Args:
        image (PIL.Image): The image to add the labels to.
        text       (str) : The text to be displayed in the label,
                           (this text will be split into two words).
        font_size  (int) : The approximate font size for the label.

    Returns:
        PIL.Image: The image with the labels added.
    """

     # calculate the scale for drawing the labels
    scale = get_abominable_scale(image)
    label_width  = int( 480 * scale )
    label_height = int(  64 * scale )

    # load the fonts for each word
    font1 = load_font("RobotoSlab-Bold.ttf" , font_size * scale)
    font2 = load_font("RobotoSlab-Black.ttf", font_size * scale * 1.1)

    # extract the first two words from the provided text
    if ' ' in text:
        words = text.split(' ', 2)
    elif '_' in text:
        words = text.split('_', 2)
    elif '-' in text:
        words = text.split('-', 2)
    else:
        words = text
    word1  = words[0] if len(words)>=1 else '???'
    word2  = words[1] if len(words)>=2 else '???'
    color1 = get_word_color(word1, "black")
    color2 = get_word_color(word2, "red"  )

    # add a label with the two words to the image
    labeled_image = draw_two_word_label(image,
                                        label_width,
                                        label_height,
                                        word1, color1, font1,
                                        word2, color2, font2 )
    return labeled_image


def add_label(filenames: list, font_size: int=None, forced_text: str=None, file_prefix: str=None):
    """Processes images by adding labels and saving them with a new prefix.

    Args:
        filenames (str or list): A filename or a list of filenames of the images to process.
        font_size         (int): The approximate font size for the labels, (defaults to 36)
        forced_text       (str): If provided, this text will be used instead of the workflow
                                 name extractedfrom the image's metadata.
        file_prefix       (str): The prefix to be added to each filename when saving the labeled image.
    """
    if not isinstance(filenames,list):
        filenames = [filenames]
    font_size   = 36        if font_size   is None else font_size
    file_prefix = 'labeled' if file_prefix is None else file_prefix

    # ensure `file_prefix` always ends with an underscore
    if not file_prefix.endswith('_'):
        file_prefix += '_'

    for filename in filenames:
        #try:

            # skip images that were previously labeled
            if filename.startswith(file_prefix):
                continue

            with Image.open(filename) as image:

                # attempt to extract the workflow from the PNG file metadata
                prompt   = image.info.get('prompt')
                workflow = image.info.get('workflow')
                if not workflow:
                    warning(f"The image {filename} does not seem to contain any workflow.")
                    continue

                # add label with workflow name
                text = get_workflow_name(workflow) if not forced_text else forced_text
                labeled_image = add_label_to_image(image, text, font_size)

                # generate a new filename
                base_name        = os.path.basename(filename)
                name_without_ext = os.path.splitext(base_name)[0]
                new_file_name = f"{file_prefix}{name_without_ext}.png"

                # save the new image with the workflow in metadata
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", prompt)
                if workflow is not None:
                    metadata.add_text("workflow", workflow)
                labeled_image.save(new_file_name, format="PNG", pnginfo=metadata, compress_level=9)
                print(f"Labeled: {new_file_name}")

        #except Exception as e:
        #    print(f"Error processing {filename}: {str(e)}")


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(description="Draws a label with the workflow name on each image.")
    parser.add_argument("images", nargs="+", help="Image file(s) to process")
    parser.add_argument("--text", help="Text to add to the image")
    parser.add_argument("--prefix", help="Prefix for processed image files")
    parser.add_argument("--font", help="Path to font file")
    parser.add_argument("--font-size", type=int, help="Font size for the label")

    args = parser.parse_args()
    add_label(args.images, font_size=args.font_size, forced_text=args.text, file_prefix=args.prefix)


if __name__ == "__main__":
    main()
