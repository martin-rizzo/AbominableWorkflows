"""
  File    : wlabel.py
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

# Default font size for labels
DEFAULT_FONT_SIZE    = 40
DEFAULT_LABEL_WIDTH  = 512
DEFAULT_LABEL_HEIGHT = 64

# Color used for prompt text
PROMPT_TEXT_COLOR = "#333344"

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
def get_word_color(word: str, default_color: str=None) -> str:
    return COLORS_BY_WORD.get(word.upper(), default_color)


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

def find_images_in_dir(directory: str) -> list[str]:
    """Find all PNG image files in a given directory.
    """
    images = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith('.png'):
            images.append(file_path)
    return images


def ascent_diference(font1: ImageFont, font2: ImageFont) -> int:
    """Calculates the difference in ascent between two fonts.
    """
    ascent1, _ = font1.getmetrics()
    ascent2, _ = font2.getmetrics()
    return ascent1 - ascent2


def load_font(filepath: str, font_size: int) -> ImageFont:
    """Attempts to load a font from the specified file.

    Args:
        filepath  (str): The path to the font file;
                         Si `None` o string vacio, retornara el font default.
        font_size (int): The desired font size.
    Returns:
        The loaded font or the default font if loading failed.
    """
    global SHOW_FONT_WARNING

    try:
        font = filepath and ImageFont.truetype(filepath, font_size)
    except Exception:
        font = None

    if not font:
        if SHOW_FONT_WARNING:
            SHOW_FONT_WARNING = False
            warning(f"Could not load font from {filepath}. Using default font.")
        font = ImageFont.load_default()

    return font


def select_font_variation(font: ImageFont,
                          variation: str,
                          variation_alt1: str = None,
                          variation_alt2: str = None) -> None:
    """Selects a specific font variation based on the given names.

    Args:
        font     (ImageFont): This should be a font that supports font variations.
        variation      (str): The primary variation name to apply to the font.
        variation_alt1 (str): An alternative variation name to use if the main variation is not found.
        variation_alt2 (str): Another alternative variation name to use.

    Example:
        >>> font = ImageFont.truetype('arial.ttf', 14)
        >>> select_font_variation(font, 'ital', 'wght')
    """
    try:
        available_variations = font.get_variation_names()
        if variation in available_variations:
            font.set_variation_by_name(variation)
        elif variation_alt1 in available_variations:
            font.set_variation_by_name(variation_alt1)
        elif variation_alt2 in available_variations:
            font.set_variation_by_axes(variation_alt2)
    except:
        return


def wrap_text(text: str, font: ImageFont, width: int) -> tuple[list[str], float]:
    """Splits text into lines that fit within the given width.

    Args:
        text      (str) : The input text to be split.
        font (ImageFont): Font used for rendering the text.
        width     (int) : Maximum width in pixels that each line of text can occupy.

    Returns:
        A list of lines (strings)
        and the percentage length of the last line.
    """
    words = text.split()
    lines = []
    current_line = ""
    for i, word in enumerate(words):
        test_line = f"{current_line} {word}" if i>0 else word
        if font.getlength(test_line) <= width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    last_line_percent = 100.0 * len(lines[-1]) / len(lines[0])
    return lines, last_line_percent


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


def get_prompt_text(workflow_json: str) -> str:

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
    def multiline_textbbox(cls,
                           draw   : ImageDraw,
                           xy     : tuple[float, float],
                           text   : str,
                           font   : ImageFont,
                           anchor : str | None = None,
                           spacing: float      = 4,
                           align  : str        = "left"
                           ):
        return cls( draw.multiline_textbbox( xy, text, font=font, anchor=anchor, spacing=spacing, align=align ) )

    # @classmethod
    # def multiline_bbox(cls, text: str, font: ImageFont, draw: ImageDraw):
    #     draw.multiline_bbox((0,0))

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

    @property
    def center(self):
        return (self[0] + self[2])/2

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

    def shrunken(self, dx: float, dy: float) -> 'Box':
        """Returns a new Box with reduced size by moving its edges inward.
        Args:
            dx (float): The number of pixels to move the left and right edges.
            dy (float): The number of pixels to move the top and bottom edges.
        Returns:
            A new Box with the specified size after shrinking.
        """
        return Box(self.left + dx, self.top + dy, self.right - dx, self.bottom - dy)

    def __repr__(self):
        return f"Box(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom})"


#------------------------ COMPLEX DRAWING FUNCTIONS ------------------------#

def add_borders(image : Image,
                left  : int,
                top   : int,
                right : int,
                bottom: int,
                border_color: tuple[int, int, int] | str
                ) -> Image:
    """Expand the image by adding borders on all sides.

    This function takes an image and expands it by adding specified borders on
    each side with a given color. The size of the new image will be expanded
    based on the provided left, top, right, and bottom values.

    Args:
        image (Image): The original image to which borders are added.
        left   (int) : Number of pixels to add to the left side of the image.
        top    (int) : Number of pixels to add to the top side of the image.
        right  (int) : Number of pixels to add to the right side of the image.
        bottom (int) : Number of pixels to add to the bottom side of the image.
        border_color (tuple or str): The color for the borders, specified as a tuple
            (R, G, B) where R, G, and B are integers in the range [0, 255],
            or as a string representing the color name ("red", "blue", etc.).

    Returns:
        The image with expanded borders.
    """
    width, height = image.size

    # create a new blank image with the expanded size including borders
    new_width  = width  + left + right
    new_height = height + top  + bottom
    new_image  = Image.new(image.mode, (new_width, new_height), color=border_color)

    # paste the original image onto the new image at the correct offset
    new_image.paste(image, (left, top))
    return new_image




def write_text_in_box(image  : Image,
                      box    : Box,
                      text   : str,
                      font   : ImageFont,
                      spacing: float = 4,
                      align  : str  = 'left',
                      color  : str  = 'black',
                      force  : bool = False
                      ) -> bool:
    """Attempts to write a given text within the rectangle defined by the Box object.

    This function only writes the text if it fits completely within the box.

    Args:
        image    (Image): The image object where the text will be written.
        box       (Box) : The bounding box specifying the region in the image where the text should be placed.
        text      (str) : The text string to be written.
        font (ImageFont): The font object used for rendering the text.
        align     (str) : Alignment of the text within the box ('left', 'center' or 'right').
        color     (str) : Color to use for the text.
        force     (bool): If True, writes the text even if it doesn't fit completely inside
                          the box; default is False.
    Returns:
        True if the text was written successfully, False otherwise.
    """
    draw = ImageDraw.Draw(image)

    # split the text into lines within the box width and adjust the box size
    # dynamically to prevent excessively short final line (ensuring last_line>35%)
    for i in range(1, 10):
        lines, last_line_percent = wrap_text( text, font, box.width )
        if last_line_percent > 35  or  box.width < 300:
            break
        box = box.shrunken(20,0)

    # join all lines with newline characters
    text = '\n'.join(lines)

    # set the appropriate position based on alignment
    if align == 'center':
        x, y   = box.center, box.top
        anchor = 'ma'
    elif align == 'right':
        x, y   = box.right, box.top
        anchor = 'ra'
    else:
        align  = 'left'
        x, y   = box.left, box.top
        anchor = 'la'

    textbbox = Box.multiline_textbbox( draw, (0,0), text, font=font, anchor=anchor, spacing=spacing, align=align )
    top_offset = textbbox.top
    _, descent = font.getmetrics()

    textbbox = textbbox.centered_in( box )
    y = textbbox.top - top_offset + (descent/4)

    ## debug rectangles
    #draw.rectangle( box, fill='red' )
    #draw.rectangle( textbbox, fill='yellow')

    if force or textbbox.top >= box.top:
        draw.multiline_text( (x,y), text, font=font, anchor=anchor, spacing=spacing, align=align, fill=color)
        return True
    else:
        return False


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
        image    (Image) : The original image to be labeled.
        width     (int)  : The width of the label rectangle.
        height    (int)  : The height of the label rectangle.
        word1     (str)  : The first word of the label.
        color1    (str)  : The color of the first word.
        font1 (ImageFont): The font used for the first word.
        word2     (str)  : The second word of the label.
        color2    (str)  : The color of the second word.
        font2 (ImageFont): The font used for the second word.

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


#----------------------- WLABEL RENDERING FUNCTIONS ------------------------#

def get_all_required_fonts(font_size: int,
                           scale    : float = 1.0
                           ) -> tuple:
    """Loads all the fonts required for rendering text.

    Args:
        font_size (int): The desired base size of the fonts in points.
        scale   (float): A multiplier to adjust the size of the loaded
                         fonts, default is 1.0 which means no scaling.
    Returns:
        A tuple containing three elements:
            - font_w1: The font used to write the first word on the label.
            - font_w2: The font used to write the second word on the label.
            - prompt_fonts: A list of additional fonts in different sizes used to write the prompt.
    """
    script_dir, script_name = os.path.split( os.path.abspath(__file__) )
    font_dir = os.path.join(script_dir, os.path.splitext(script_name)[0] + "-font")

    # if the font directory does not exist, return immediately
    if not os.path.exists(font_dir):
        return None

    # search through the font directory for TTF files
    opensans_ttf_file   = None
    robotoslab_ttf_file = None
    default_ttf_file    = None
    for filename in os.listdir(font_dir):
        filename_lower = filename.lower()
        if not filename_lower.endswith(".ttf"):
            continue
        elif 'opensans' in filename_lower:
              opensans_ttf_file = os.path.join(font_dir, filename)
        elif 'robotoslab' in filename_lower:
              robotoslab_ttf_file = os.path.join(font_dir, filename)
        elif default_ttf_file is None:
             default_ttf_file = os.path.join(font_dir, filename)

    # load the fonts based on what was found
    label_ttf_file   = robotoslab_ttf_file or default_ttf_file
    prompt_ttf_file  = opensans_ttf_file   or default_ttf_file

    font_w1      = load_font(label_ttf_file, int(font_size * scale * 1.0) )
    font_w2      = load_font(label_ttf_file, int(font_size * scale * 1.1) )
    prompt_fonts = [load_font(prompt_ttf_file, size) for size in range(int(font_size * scale * 1.3), 10, -2)]

    select_font_variation(font_w1, b'ExtraBold', b'Black', b'Bold')
    select_font_variation(font_w2, b'ExtraBold', b'Black', b'Bold')
    for font in prompt_fonts:
        select_font_variation(font, b'Regular', b'Medium')

    return (font_w1, font_w2, prompt_fonts)


def add_label_to_image(image: Image,
                       text : str,
                       font1: ImageFont,
                       font2: ImageFont,
                       scale: float = 1.0
                       ) -> Image:
    """Adds a label with two words to the image.

    Args:
        image    (Image) : The base image to which labels will be added.
        text      (str)  : The input text from which two words will be extracted and used for labeling.
        font1 (ImageFont): The font object to use for the first word in the label.
        font2 (ImageFont): The font object to use for the second word in the label.
        scale    (float) : A scaling factor that adjusts the size of the label.

    Returns:
        The modified image with the labels added.
    """

    # calculate the label size based on the scale provided
    label_width  = int( DEFAULT_LABEL_WIDTH  * scale )
    label_height = int( DEFAULT_LABEL_HEIGHT * scale )

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

    # determine the color for each word based on predefined rules
    color1 = get_word_color(word1, "black")
    color2 = get_word_color(word2, "red"  )

    # add a label with both words to the image
    labeled_image = draw_two_word_label(image,
                                        label_width,
                                        label_height,
                                        word1, color1, font1,
                                        word2, color2, font2 )
    return labeled_image


def add_prompt_to_image(image : Image,
                        prompt: str,
                        fonts : [ImageFont],
                        scale : float = 1.0
                        ) -> Image:
    """Adds a text prompt to the image at the top.

    This function takes an image and adds a text prompt at the top of the image.
    The prompt is split into multiple lines if it exceeds the width of the image.

    Args:
        image      (Image) : The base image to which prompts will be added.
        prompt      (str)  : The text string containing the prompt to be displayed.
        fonts ([ImageFont]): A list of fonts in decreasing order of size for
                             rendering the text. The function will attempt to
                             use the appropriate font size (not implemented)
        scale      (float) : A scaling factor that adjusts the size of the prompt.

    Returns:
        The modified image with the prompt added.
    """
    width, _ = image.size
    box = Box(0,0, int(width), int(200*scale))

    # add a border on top of the image
    # and write the prompt inside the defined box area
    image = add_borders(image, 0, box.height, 0, 0, 'white')

    # va recorriendo todos los fonts hasta que encuentra un font
    # que hace que el texto entre completo dentro del box
    for i, font in enumerate(fonts):
        is_last = ( i == len(fonts)-1 )
        fit = write_text_in_box(image,
                                box.shrunken(16,8),
                                prompt,
                                font,
                                spacing = 0,
                                align   = 'center',
                                color   = PROMPT_TEXT_COLOR,
                                force   = is_last
                                )
        if fit:
            break
    return image


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def process_image(image         : Image,
                  workflow_json : str,
                  font_size     : int   = DEFAULT_FONT_SIZE,
                  write_prompt  : bool  = False,
                  workflow_name : str   = None,
                  output_scale  : float = None,
                  ) -> Image:
    """Process an image by adding labels based on a given workflow.

    Args:
        image        (Image): The base image to process and label.
        workflow_json (str) : The comfyui workflow in JSON format.
        font_size     (int) : Approximate font size used to label the image. Defaults to DEFAULT_FONT_SIZE
        write_prompt  (bool): If True, writes the original prompt text into the image.
        workflow_name (str) : The name of the workflow to be used for labeling the image;
                              if not provided, an attempt will be made to extract it from the JSON.
        output_scale (float): Scaling factor for resizing the final image;
                              a value of 1.0 (or None) means no scaling, defaults to None.
    Returns:
        The processed image with the labels added.
    """

    # determine the workflow name from JSON if not provided
    if not workflow_name:
        workflow_name = get_workflow_name(workflow_json)

    # calculate the scale factor based on the original image size
    # and the size of a normal "abominable" image
    draw_scale = get_abominable_scale(image)

    # get the appropriate fonts based on the calculated scale
    font_w1, font_w2, prompt_fonts = get_all_required_fonts(font_size, scale=draw_scale)

    # add a label to the bottom right of the image indicating the workflow name
    output_image = add_label_to_image(image, workflow_name, font_w1, font_w2, scale=draw_scale)

    # optionally, write the original prompt text on the image
    if write_prompt:
        prompt = get_prompt_text(workflow_json) or "<no prompt found>"
        output_image = add_prompt_to_image(output_image, prompt, prompt_fonts, scale=draw_scale)

    # resize the final image if any output scaling was requested
    if output_scale:
        _width, _height = output_image.size
        _size = ( int(output_scale*_width), int(output_scale*_height) )
        output_image = output_image.resize( _size, Image.Resampling.LANCZOS )

    return output_image


def process_all_images(filenames        : list,
                       font_size        : int,
                       write_prompt     : bool  = False,
                       workflow_name    : str   = None,
                       output_scale     : float = None,
                       output_dir       : str   = None,
                       output_prefix    : str   = None,
                       keep_original_dir: bool  = False,
                       ) -> None:
    """Process multiple images by adding labels and saving them with a new prefix.

    Args:
        filenames      (list): A filename or a list of filenames of the images to process
        font_size      (int) : Approximate font size used to label the images.
        write_prompt   (bool): If True, writes the original prompt from each image.
        workflow_name  (str) : User-provided workflow name that will be labeled on the images;
                               if not provided, it will be extracted from the image metadata.
        output_scale  (float): Scaling factor for resizing the processed images after labeling;
                               a value of 1.0 (or None) means no scaling, defaults to None.
        output_dir     (str) : Directory where the labeled images will be saved.
                               If not provided, the current working directory will be used.
        output_prefix  (str) : A string that prefixes each new filename denoting processing details;
                               defaults to 'labeled' if no scaling is applied and 'scaled' otherwise.
        keep_original_dir (bool): If True, the images will be saved in the same dir as the original
                                  image. Otherwise, they will be stored in the current working dir.
    """
    if not isinstance(filenames,list):
        filenames = [filenames]

    # set output_scale to None if it's exactly 1.0
    # since this means no scaling should be applied
    if output_scale == 1.0:
        output_scale = None

    # determine the output file prefix based on scaling and
    # ensure prefix always ends with an underscore
    if not output_prefix:
        output_prefix = 'labeled' if not output_scale else 'scaled'
    if not output_prefix.endswith('_'):
        output_prefix += '_'

    # create new directories only if a specific output_dir is provided
    should_make_dirs = True if output_dir else False

    for filename in filenames:
        #try:

            # skip images that were previously labeled
            if filename.startswith(output_prefix):
                continue

            # generate a new filename
            original_dir, name  = os.path.split(filename)
            name_without_ext    = os.path.splitext(name)[0]
            new_file_path       = f"{output_prefix}{name_without_ext}.png"
            if keep_original_dir:
                new_file_path = os.path.join(original_dir, new_file_path)
            if output_dir:
                new_file_path = os.path.join(output_dir, new_file_path)
                if new_file_path != os.path.normpath(new_file_path):
                    continue

            # open the image and process it
            with Image.open(filename) as image:
                prompt   = image.info.get('prompt')
                workflow = image.info.get('workflow')
                if not workflow:
                    warning(f"The image {filename} does not seem to contain any workflow.")
                    continue
                output_image = process_image(image, workflow, font_size, write_prompt, workflow_name, output_scale)

            # prepare metadata for saving the processed image
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", prompt)
            if workflow is not None:
                metadata.add_text("workflow", workflow)

            # create new directories if necessary
            if should_make_dirs:
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

            # save the processed image with its new name
            output_image.save(new_file_path, format="PNG", pnginfo=metadata, compress_level=9)
            print(f"Labeled: {new_file_path}")

        #except Exception as e:
        #    print(f"Error processing {filename}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Draws a label to your images with the workflow name (or custom text).")
    parser.add_argument('images'              , nargs="+",           help="Image files (or directories containing .png) to which the label will be applied")
    parser.add_argument('-t', '--text'        ,                      help="Text to write on the image label. If not specified, the workflow name will be used")
    parser.add_argument('-s', '--scale'       , type=float,          help="Scaling factor (max 1.0) to scale the output image")
    parser.add_argument('-p', '--write-prompt', action='store_true', help="Include the original prompt text in the final image")
    parser.add_argument('-k', '--keep-dir'    , action='store_true', help="Keep the structure of directories for processed images")
    parser.add_argument('-o', '--output-dir'  ,                      help="Directory where the labeled images will be saved")
    parser.add_argument(      '--prefix'      ,                      help="Prefix for processed image files")
    parser.add_argument(      '--font'        ,                      help="Path to font file")
    parser.add_argument(      '--font-size'   , type=int,            help="Font size for the label")

    args  = parser.parse_args()

    scale = None
    if args.scale:
        scale = 0.01 if args.scale<=0.01 else 1.0 if args.scale>=1.0 else args.scale

    # find all images from the provided arguments (files or directories)
    images = []
    for image in args.images:
        if os.path.isfile(image):
            images.append(image)
        elif os.path.isdir(image):
            images.extend(find_images_in_dir(image))

    process_all_images(images,
                       font_size     = args.font_size or DEFAULT_FONT_SIZE,
                       write_prompt  = args.write_prompt,
                       workflow_name = args.text,
                       output_scale  = scale,
                       output_dir    = args.output_dir,
                       output_prefix = args.prefix,
                       keep_original_dir = args.keep_dir
                       )


if __name__ == "__main__":
    main()
