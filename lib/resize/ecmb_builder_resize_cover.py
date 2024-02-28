"""
 File: ecmb_builder_resize_cover.py
 Copyright (c) 2023 Clemens K. (https://github.com/metacreature)
 
 MIT License
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""

from PIL import Image
from math import ceil
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeCover(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> list[Image.Image, bool]:
        orig_width, orig_height = pillow_orig.size

        if orig_width == final_width and orig_height == final_height:
            return (pillow_orig, False)

        offset_x = 0
        offset_y = 0

        if (final_width / final_height) > (orig_width / orig_height):
            target_width = final_width
            target_height = ceil(final_width * (orig_height / orig_width))

            if (final_height - target_height) != 0:
                offset_y = ceil((target_height - final_height) / 2)
        else:
            target_width = ceil(final_height * (orig_width / orig_height))
            target_height = final_height

            if (final_width - target_width) != 0:
                offset_x = ceil((target_width - final_width) / 2)
        
        if offset_x or offset_y:
            pillow_tmp = pillow_orig.resize((target_width, target_height))
            pillow_resized = pillow_tmp.crop((offset_x, offset_y, offset_x + final_width, offset_y + final_height))    
        else:
            pillow_resized = pillow_orig.resize((final_width, final_height))
        
        pillow_orig.close()
        del pillow_orig
        
        return (pillow_resized, True)