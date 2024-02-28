"""
 File: ecmb_builder_resize_stretch.py
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
from .ecmb_builder_resize_base import ecmbBuilderResizeBase

class ecmbBuilderResizeStretch(ecmbBuilderResizeBase):


    def _resize(self, pillow_orig: Image, final_width: int, final_height: int) -> list[Image.Image, bool]:
        orig_width, orig_height = pillow_orig.size

        if orig_width == final_width and orig_height == final_height:
            return (pillow_orig, False)

        pillow_resized = pillow_orig.resize((final_width, final_height))
        
        pillow_orig.close()
        del pillow_orig

        return (pillow_resized, True)