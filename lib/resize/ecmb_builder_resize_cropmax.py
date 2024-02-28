"""
 File: ecmb_builder_resize_cropmax.py
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

from PIL import Image, ImageEnhance, ImageOps
from math import ceil
from .ecmb_builder_resize_max import ecmbBuilderResizeMax

class ecmbBuilderResizeCropmax(ecmbBuilderResizeMax):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> list[Image.Image, bool]:
        orig_width, orig_height = pillow_orig.size
        
        pillow_tmp = ImageEnhance.Contrast(pillow_orig.convert('RGB')).enhance(5)
        pillow_tmp = ImageOps.invert(pillow_tmp)
        
        box = pillow_tmp.getbbox()
        box_width = box[2] - box[0]

        if not (box_width < orig_width * 0.99 and box_width > orig_width * 0.85):
            return super()._resize(pillow_orig, final_width, final_height)

        pillow_resized = pillow_orig.crop((box[0], 0, box[2], orig_height))
        
        pillow_orig.close()
        del pillow_orig

        if orig_width <= final_width and orig_height <= final_height:
            return (pillow_resized, True)
        else:
            return super()._resize(pillow_resized, final_width, final_height)