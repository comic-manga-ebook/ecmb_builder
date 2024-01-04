"""
 File: ecmb_builder_config.py
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

import re, os, yaml, path
from .ecmb_builder_utils import ecmbBuilderUtils
from ecmblib import ecmbUtils, ecmbException, BOOK_TYPE



class ecmbBuilderConfig():

    _resize_methods = None

    _source_dir = None
    _output_dir = None

    _default_resize_method = None
    _default_webp_compression = None
    _default_compress_all = None
    _default_book_type = None
    _default_resize_width = None
    _default_resize_height = None
    _default_book_language = None

    def __init__(self):
        self._load_resize_methods()
        self._load_config()


    def get_resize_methods(self):
        return self._resize_methods
    resize_methods: list = property(get_resize_methods)

    def get_source_dir(self):
        return self._source_dir
    source_dir: str = property(get_source_dir) 

    def get_output_dir(self):
        return self._output_dir
    output_dir: str = property(get_output_dir) 

    def get_default_resize_method(self):
        return self._default_resize_method
    default_resize_method: str = property(get_default_resize_method) 
    
    def get_default_webp_compression(self):
        return self._default_webp_compression
    default_webp_compression: int = property(get_default_webp_compression) 

    def get_compress_all(self):
        return self._compress_all
    compress_all: bool = property(get_compress_all) 

    def get_default_book_type(self):
        return self._default_book_type
    default_book_type: str = property(get_default_book_type) 

    def get_default_resize_width(self):
        return self._default_resize_width
    default_resize_width: int = property(get_default_resize_width) 

    def get_default_resize_height(self):
        return self._default_resize_height
    default_resize_height: int = property(get_default_resize_height) 
    
    def get_default_book_language(self):
        return self._default_book_language
    default_book_language: str = property(get_default_book_language)



    def _load_config(self) -> None:
        builder_path = str(path.Path(__file__).abspath().parent.parent) + '\\'

        try: 
            with open(builder_path + 'ecmb_builder_config.yml', 'r') as file:
                config = yaml.safe_load(file)
        except:
            ecmbUtils.raise_exception('Builder-Config "ecmb_builder_config.yml" not found or invalid!')
        
        try:
            # working-dir
            source_dir = config.get('source_dir')
            if not source_dir:
                ecmbUtils.raise_exception('source-dir is not defined!')

            if not re.search(r'[:]', source_dir):
                source_dir = builder_path + source_dir

            self._source_dir = str(path.Path(source_dir).abspath()) +  '\\'
            
            if not os.path.isdir(self._source_dir):
                ecmbUtils.raise_exception('source-dir was not found!')

            output_dir = config.get('output_dir')
            if not output_dir:
                ecmbUtils.raise_exception('output-dir is not defined!')

            if not re.search(r'[:]', output_dir):
                output_dir = builder_path + output_dir

            self._output_dir = str(path.Path(output_dir).abspath()) +  '\\'
            
            if not os.path.isdir(self._output_dir):
                ecmbUtils.raise_exception('output-dir was not found!')

            ecmbUtils.validate_in_list(True, 'default_resize_method', config.get('default_resize_method'), list(self._resize_methods.keys()), 1)
            ecmbUtils.validate_int(True, 'default_webp_compression', config.get('default_webp_compression'), 0, 100, 1)
            ecmbUtils.validate_enum(True, 'default_book_type', config.get('default_book_type'), BOOK_TYPE, 1)
            ecmbUtils.validate_int(True, 'default_resize_width', config.get('default_resize_width'), 100, 1800, 1)
            ecmbUtils.validate_int(True, 'default_resize_height', config.get('default_resize_height'), 100, 2400, 1)
            ecmbUtils.validate_regex(True, 'default_book_language', config.get('default_book_language'), r'^[a-z]{2}$', 1)
        except Exception as e:
            raise ecmbException('Your Builder-Config "ecmb_builder_config.yml" contains an invalid value or the value is missing:\n' + str(e))
        
        
        self._default_compress_all = True if config.get('default_compress_all') else False
        self._default_resize_method = config.get('default_resize_method') 
        self._default_webp_compression = config.get('default_webp_compression')
        self._default_book_type = config.get('default_book_type')
        self._default_resize_width = config.get('default_resize_width')
        self._default_resize_height = config.get('default_resize_height')
        self._default_book_language = config.get('default_book_language')

    

    def _load_resize_methods(self) -> None:
        resize_path = str(path.Path(__file__).abspath().parent) + '\\resize'
        file_list = ecmbBuilderUtils.list_files(resize_path, None, r'^ecmb_builder_resize_(?!base)[a-z]+\.py$', 0)
        
        self._resize_methods = {}
        for file in file_list:
            key = re.search(r'ecmb_builder_resize_([a-z]+)\.py', file['name']).group(1)
            mod = ('lib.resize.ecmb_builder_resize_' + key, 'ecmbBuilderResize' + (key.title()))
            self._resize_methods[key] = mod