"""
 File: ecmb_builder_base.py
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

import re, os, path, hashlib
from tqdm import tqdm
from datetime import datetime
from .ecmb_builder_utils import ecmbBuilderUtils
from .ecmb_builder_config import ecmbBuilderConfig
from .ecmb_builder_book_config import ecmbBuilderBookConfig
from .resize.ecmb_builder_resize_base import ecmbBuilderResizeBase
from ecmblib import ecmbBook, ecmbException


class ecmbBuilderBase():
    
    _builder_config = None
    _book_config = None

    _folder_name = None
    _source_dir = None
    _output_dir = None


    def __init__(self, folder_name:str):
        self._builder_config = ecmbBuilderConfig()
        self._set_dirs(folder_name)
        self._book_config = ecmbBuilderBookConfig(self._builder_config, self._source_dir)


    def _read_folder_structure(self) -> None:
        folder_list = ecmbBuilderUtils.list_dirs(self._source_dir, r'^(?!__).+$', 2)
        level0_folders = []
        level1_folders = []
        for folder in folder_list:
            if folder['level'] == 0:
                level0_folders.append(folder)
            else:
                level1_folders.append(folder)

        if len(level0_folders) > len(level1_folders):  
            if len(level0_folders) == 0:
                raise ecmbException('No chapter-folders available!')
            return (level0_folders, None)
        else:
            for volume in level0_folders:
                volume_path = volume['path'] + volume['name'] + '\\'
                volume['chapters'] = []
                for chapter in level1_folders:
                    if chapter['path'] == volume_path:
                        volume['chapters'].append(chapter)

                if len(volume['chapters']) == 0:
                    raise ecmbException('"'+ volume['name'] + '" has no chapters!')

            return (level1_folders, level0_folders)
        
    
    def _get_image_list(self, path: str) -> list:
        return ecmbBuilderUtils.list_files(path, None, r'^(?!__).+[.](jpg|jpeg|png|webp)$', 0)


    def _set_dirs(self, folder_name: str) -> None:
        source_dir = str(path.Path(self._builder_config.source_dir + folder_name).abspath()) + '\\'
        if not os.path.isdir(source_dir):
            raise ecmbException(f'Comic/Manga folder "{folder_name}" was not found!')
        
        output_dir = str(path.Path(self._builder_config.output_dir + folder_name).abspath()) + '\\'
        output_dir = str(path.Path(output_dir + '..\\').abspath()) + '\\'

        self._folder_name = folder_name
        self._source_dir = source_dir
        self._output_dir = output_dir
        
