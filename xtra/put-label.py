"""
  File    : put-label.py
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
import argparse
from PIL import Image, ImageDraw, ImageFont


#--------------------------------- HELPERS ---------------------------------#

def height_diference(font1, font2):
    ascent1, _ = font1.getmetrics()
    ascent2, _ = font2.getmetrics()
    return ascent1 - ascent2

def load_font(font_name, font_size):
    try:
        font = ImageFont.truetype(font_name, font_size)
    except Exception:
        font = None
    if not font:
        print(f"Warning: Could not load font from {font_name}. Using default font.")
        font = ImageFont.load_default()
    return font

#-------------------------------- BOX CLASS --------------------------------#
class Box(tuple):
    def __new__(cls, left, top=None, right=None, bottom=None):
        if isinstance(left,tuple) and len(left)==4:
            left, top, right, bottom = left[0], left[1], left[2], left[3]
        return super(Box, cls).__new__(cls, (left, top, right, bottom))

    @classmethod
    def bounding_for_text(cls, text, font):
        return cls(0,0,0,0)

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


#------------------------------ DRAWING LABEL ------------------------------#

def add_label(image, width, height, word1, color1, font1, word2, color2, font2):
    """
    image: la imagen original a etiquetar
    width: el ancho de la etiqueta en pixeles
    height: la altura de la etiqueta en pixeles
    word1: la primer palabra de la etiqueta
    color1: el color de la primer palabra
    font1: el font utilizado en la primer palabra
    word2: la segunda palabra de la etiqueta
    color2: el color de la segunda palabra
    font2: el font utilizado en la segunda palabra
    font_size: el tama~nio aproximado del font a utilizar
    autoscale: si True entonces la etiqueta se escalara acorde al tama~nio de la imagen
    """
    image_width, image_height = image.size
    radius      = height/3 # radio de la esquina del rectangulo
    space_width = 10       # el espacio entre ambas palabras
    margin      = 10       # el margen minimo entre el borde y el texto

    draw = ImageDraw.Draw(image)

    # calcular el espacio que ocuparan las palabras
    word1_box = Box.container_for_text(word1, font1)
    word2_box = Box.container_for_text(word2, font2)
    total_width  = word1_box.width + word2_box.width + space_width
    total_height = max(word1_box.height, word2_box.height)
    total_box    = Box(0,0, total_width, total_height)

    minimum_width = margin + total_width + margin
    if width < minimum_width:
        width = minimum_width

    # dibujar el rectangulo blanco
    whitebox1 = Box(0,0,width,height).moved_to( (image_width, image_height), anchor='rb' )
    whitebox2 = whitebox1.moved_by(-radius,radius).with_size( radius, whitebox1.height-radius )
    circlebox = whitebox1.moved_by(-radius,0).with_size( radius*2, radius*2 )
    draw.rectangle(whitebox1, fill="white")
    draw.rectangle(whitebox2, fill="white")
    draw.ellipse(  circlebox, fill="white")


    # centrar ambas palabras dentro del whitebox
    total_box = total_box.centered_in( whitebox1.moved_by(-radius/2,0) )

    # acomodar la palabra 1 a la izquierda de la total_box
    # y la palabra 2 a la derecha de la total_box
    word1_box = word1_box.moved_to( total_box.left, total_box.top, anchor='lt')
    word2_box = word2_box.moved_to( total_box.right, total_box.top, anchor='rt')

    # alinear la palabra 1 con la palabra 2
    # ya que ambos fonts tienen distintos tama~nios
    word1_box = word1_box.moved_by(0, height_diference(font2, font1))

    # escribir y retornar
    draw.text(word1_box, word1, fill=color1, font=font1, anchor='la')
    draw.text(word2_box, word2, fill=color2, font=font2, anchor='la')
    return image


def add_workflow_label(filenames, font_size, prefix='labeled'):
    """
    Process images by adding labels and saving them with a new prefix.
    # filenames = una lista con los nombres de archivo de las imagenes a procesar
    # font_size = el tamanio aproximado del texto a escribir
    # prefix = el prefijo que sera agregado a cada nombre de archivo al salvar la imagen
    """

    # crea los 2 fonts que seran utilizados para etiquetar las imagenes
    font1 = load_font("RobotoSlab-Bold.ttf" , font_size)
    font2 = load_font("RobotoSlab-Black.ttf", font_size*1.1)

    if not isinstance(filenames,list):
        filenames = [filenames]

    for filename in filenames:
        #try:
            with Image.open(filename) as image:
                labeled_image = add_label(image,
                                          400, 60,
                                          "abominable", "black", font1,
                                          "DARKFAN80"     , "red"  , font2,
                                          )

                # generate new file name
                base_name = os.path.basename(filename)
                name_without_ext = os.path.splitext(base_name)[0]
                new_file_name = f"{prefix}_{name_without_ext}.png"

                # save the new image
                labeled_image.save(new_file_name, "PNG")
                print(f"Labeled: {new_file_name}")
        #except Exception as e:
        #    print(f"Error processing {filename}: {str(e)}")


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#

def main():
    parser = argparse.ArgumentParser(description="Draws a label with the workflow name on each image.")
    parser.add_argument("images", nargs="+", help="Image file(s) to process")
    parser.add_argument("--text", default="abominable workflow", help="Text to add to the image")
    parser.add_argument("--prefix", default="labeled", help="Prefix for processed image files")
    parser.add_argument("--font", help="Path to font file")
    parser.add_argument("--font-size", type=int, default=36, help="Font size for the label")

    args = parser.parse_args()
    add_workflow_label(args.images, font_size=args.font_size, prefix=args.prefix)

if __name__ == "__main__":
    main()
