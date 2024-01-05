"""
 File: ecmb_builder_book_config.py
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

import re, os, json
from .ecmb_builder_enums import *
from .ecmb_builder_config import ecmbBuilderConfig
from ecmblib import ecmbUtils, ecmbException, BOOK_TYPE, BASED_ON_TYPE, CONTENT_WARNING, AUTHOR_ROLE, EDITOR_ROLE


class ecmbBuilderBookConfig():

    _builder_config = None
    _source_dir = None

    _is_initialized = None
    _meta_data = None

    _resize_method = None
    _webp_compression = None
    _compress_all = None

    _book_type = None
    _resize_width = None
    _resize_height = None
    _book_language = None
    _book_title = None

    _chapter_list = None
    _volume_list = None
    
    def __init__(self, builder_config: ecmbBuilderConfig, source_dir: str):
        self._builder_config = builder_config
        self._source_dir = source_dir
        self._load_config()

    
    def get_is_initialized(self):
        return self._is_initialized
    is_initialized: bool = property(get_is_initialized) 

    def get_meta_data(self):
        return self._meta_data
    meta_data: dict = property(get_meta_data) 

    def get_resize_method(self):
        return self._resize_method
    resize_method: str = property(get_resize_method) 
    
    def get_webp_compression(self):
        return self._webp_compression
    webp_compression: int = property(get_webp_compression) 

    def get_compress_all(self):
        return self._compress_all
    compress_all: bool = property(get_compress_all) 

    def get_book_type(self):
        return self._book_type
    book_type: str = property(get_book_type) 

    def get_resize_width(self):
        return self._resize_width
    resize_width: int = property(get_resize_width) 

    def get_resize_height(self):
        return self._resize_height
    resize_height: int = property(get_resize_height) 
    
    def get_book_language(self):
        return self._book_language
    book_language: str = property(get_book_language)

    def get_book_title(self):
        return self._book_title
    book_title: str = property(get_book_title)

    def get_volume_list(self):
        return self._volume_list
    volume_list: dict = property(get_volume_list)

    def get_chapter_list(self):
        return self._chapter_list
    chapter_list: list = property(get_chapter_list)


    def _load_config(self) -> None:
        if not os.path.exists(self._source_dir + 'book_config.json'):
            self._is_initialized = False
            return

        try:
            with open(self._source_dir + 'book_config.json', 'r') as f:		
                config = json.load(f)
        except Exception as e:
            ecmbUtils.raise_exception('Load "book_config.json" failed: ' + str(e))

        if type(config) != dict or type(config.get('builder-config')) != dict or type(config.get('required')) != dict or not (
                type(config.get('volumes')) == dict or type(config.get('chapters')) == dict
            ):
                ecmbUtils.raise_exception('Invalid "book_config.json"!')

        try:
            ecmbUtils.validate_in_list(True, 'builder-config -> resize_method', config['builder-config'].get('resize_method'), list(self._builder_config.resize_methods.keys()))
            ecmbUtils.validate_int(True, 'builder-config -> resize_width', config['builder-config'].get('resize_width'), 100, 1800)
            ecmbUtils.validate_int(True, 'builder-config -> resize_height', config['builder-config'].get('resize_height'), 100, 2400)
            ecmbUtils.validate_int(True, 'builder-config -> webp_compression', config['builder-config'].get('webp_compression'), 0, 100)
            ecmbUtils.validate_enum(True, 'required -> type', config['required'].get('type'), BOOK_TYPE)
            ecmbUtils.validate_regex(True, 'required -> language', config['required'].get('language'), r'^[a-z]{2}$')
            ecmbUtils.validate_not_empty_str(True, 'required -> title', config['required'].get('title'))

            if type(config.get('volumes')) == dict:
                self._volume_list = {}
                for volume_key, chapter_list in config.get('volumes').items():
                    volume_dir = self._source_dir + volume_key + '\\'
                    if not os.path.exists(volume_dir):
                        ecmbUtils.raise_exception(f'directory for volume "{volume_key}" is missing!')
                    volume = []

                    for chapter_key, chapter in chapter_list.items():
                        chapter_dir = volume_dir + chapter_key +'\\'
                        if not os.path.exists(chapter_dir):
                            ecmbUtils.raise_exception(f'directory for chapter "{chapter_key}" in volume "{volume_key}" is missing!')
                        ecmbUtils.validate_not_empty_str(True, f'volumes -> {volume_key} -> {chapter_key} -> label', chapter.get('label'))
                        chapter['path'] = chapter_dir
                        # remove default_values
                        chapter['start_with'] = None if chapter.get('start_with') == 'my_image_name.jpg#left' else chapter.get('start_with')
                        volume.append(chapter)

                    self._volume_list[volume_key] = volume
                
                if len(self._volume_list) == 0:
                    ecmbUtils.raise_exception(f'no volumes available!')

            elif type(config.get('chapters')) == dict:
                self._chapter_list = []
                for chapter_key, chapter in config.get('chapters').items():
                        chapter_dir = self._source_dir + chapter_key +'\\'
                        if not os.path.exists(chapter_dir):
                            ecmbUtils.raise_exception(f'directory for chapter "{chapter_key}" is missing!')
                        ecmbUtils.validate_not_empty_str(True, f'chapters -> {chapter_key} -> label', chapter.get('label'))
                        chapter['path'] = chapter_dir
                        # remove default_values
                        chapter['start_with'] = None if chapter.get('start_with') == 'my_image_name.jpg#left' else chapter.get('start_with')
                        self._chapter_list.append(chapter)
        
                if len(self._chapter_list) == 0:
                    ecmbUtils.raise_exception(f'no chapters available!')
        
        except Exception as e:
            raise ecmbException('Your "book_config.json" contains an invalid value or the value is missing:\n' + str(e))


        self._compress_all = True if config['builder-config'].get('compress_all') else False

        self._resize_method = config['builder-config'].get('resize_method') 
        self._resize_width = config['builder-config'].get('resize_width')
        self._resize_height = config['builder-config'].get('resize_height')
        self._webp_compression = config['builder-config'].get('webp_compression')
        self._book_type = config['required'].get('type')
        self._book_language = config['required'].get('language')
        self._book_title = config['required'].get('title')

        # remove default_values
        if type(config.get('optional')) != dict:
            config['optional'] = {}

        if config['optional'].get('pages') == 0:
            config['optional']['pages'] = None

        warnings = ecmbUtils.enum_values(CONTENT_WARNING)
        if config['optional'].get('publishdate') == '0000-00-00|0000':
            config['optional']['publishdate'] = ''
        
        if type(config['optional'].get('warnings')) != list or (
            '|'.join(config['optional'].get('warnings')) == '|'.join(warnings)):
            config['optional']['warnings'] = None

        if type(config['optional'].get('genres')) == list:
            for genre_nr in range(len(config['optional']['genres'])):
                if re.search(r'^Example.*', config['optional']['genres'][genre_nr]):
                    config['optional']['genres'][genre_nr] = None
        else:
            config['optional']['genres'] = {}

        if type(config['optional'].get('original')) == dict:
            if config['optional']['original'].get('publishdate') == '0000-00-00|0000':
                config['optional']['original']['publishdate'] = ''
        else:
            config['optional']['original'] = {}

        if type(config['optional'].get('based_on')) == dict:
            based_on_type = ecmbUtils.enum_values(BASED_ON_TYPE)
            if config['optional']['based_on'].get('type') == '|'.join(based_on_type):
                config['optional']['based_on']['type'] = ''

            if config['optional']['based_on'].get('publishdate') == '0000-00-00|0000':
                config['optional']['based_on']['publishdate'] = ''
        else:
            config['optional']['based_on'] = {}


        self._meta_data = config.get('optional')
        self._is_initialized = True
    

    def init_config(self, init_type: INIT_TYPE, chapter_folders: list, volume_folders: list = None) -> None:
        if self._is_initialized:
            ecmbUtils.raise_exception('Book is allready initialized!')
        
        init_type = ecmbUtils.enum_value(init_type)
        ecmbUtils.validate_enum(True, 'init_type', init_type, INIT_TYPE)

        warnings = ecmbUtils.enum_values(CONTENT_WARNING)
        based_on_type = ecmbUtils.enum_values(BASED_ON_TYPE)
        authors = ecmbUtils.enum_values(AUTHOR_ROLE)
        authors = [{'name': '', 'role': at, 'href': ''} for at in authors]
        editors = ecmbUtils.enum_values(EDITOR_ROLE)
        editors = [{'name': '', 'role': at, 'href': ''} for at in editors]

        book_config = {
            'builder-config': {
                'resize_method': self._builder_config.default_resize_method,
                'resize_width': self._builder_config._default_resize_width,
                'resize_height': self._builder_config._default_resize_height,
                'webp_compression': self._builder_config._default_webp_compression,
                'compress_all': self._builder_config._default_compress_all
            },
            'required': {
                'type': self._builder_config._default_book_type,
                'language': self._builder_config._default_book_language,
                'title':  re.sub(r'[^a-zA-Z0-9]+', ' ', self._source_dir.split('\\')[-2]).strip(),
            },
        }

        match init_type:
            case INIT_TYPE.FULL.value:
                book_config['optional'] = {
                    'isbn': '',
                    'publisher': {
                        'name': '',
                        'href': ''
                    },
                    'publishdate': '0000-00-00|0000',
                    'summary': '',
                    'pages': 0,
                    'notes': '',
                    'genres': ['Example1', 'Example2'],
                    'warnings': warnings,
                    'authors': authors,
                    'editors': editors,
                    'original': {
                        'language': '',
                        'isbn': '',
                        'publisher': {
                            'name': '',
                            'href': ''
                        },
                        'publishdate': '0000-00-00|0000',
                        'title': '',
                        'authors': authors
                    },
                    'based_on': {
                        'type': '|'.join(based_on_type),
                        'language': '',
                        'isbn': '',
                        'publisher': {
                            'name': '',
                            'href': ''
                        },
                        'publishdate': '0000-00-00|0000',
                        'title': '',
                        'authors': authors
                    }
                }
            case INIT_TYPE.TRANSLATED.value:
                book_config['optional'] = {
                    'isbn': '',
                    'publisher': {
                        'name': '',
                        'href': ''
                    },
                    'publishdate': '0000-00-00|0000',
                    'summary': '',
                    'notes': '',
                    'genres': ['Example1', 'Example2'],
                    'warnings': warnings,
                    'editors': editors,
                    'original': {
                        'language': '',
                        'isbn': '',
                        'publisher': {
                            'name': '',
                            'href': ''
                        },
                        'publishdate': '0000-00-00|0000',
                        'title': '',
                        'authors': authors
                    }
                }
            case INIT_TYPE.BASIC.value:
                book_config['optional'] = {
                    'summary': '',
                    'notes': '',
                    'genres': ['Example1', 'Example2'],
                    'warnings': warnings,
                    'authors': authors,
                    'editors': editors,
                }
        

        chapter_cnt = 0
        chapter_template = {
            'label': '',
            'title': '',
            'start_with': 'my_image_name.jpg#left'
        }

        if volume_folders:
            book_config['volumes'] = {}
            for volume in volume_folders:
                book_config['volumes'][volume['name']] = {}
                for chapter in volume['chapters']:
                    label = re.sub(r'^(chapter_)?[0-9_ -]+', '', chapter['name'])
                    chapter_cnt += 1
                    chapter_template.update({'label': label if label else f'Chapter {chapter_cnt}'})
                    book_config['volumes'][volume['name']][chapter['name']] = dict(chapter_template)
        else: 
            book_config['chapters'] = {}
            for chapter in chapter_folders:
                label = re.sub(r'^(chapter_)?[0-9%_. +~-]+', '', chapter['name'], re.IGNORECASE)
                if label:
                    chapter_template.update({'label': label})
                else:
                    chapter_cnt += 1
                    chapter_template.update({'label': f'Chapter {chapter_cnt}'})
                book_config['chapters'][chapter['name']] = dict(chapter_template)

        with open(self._source_dir + 'book_config.json', 'w') as f:
            json.dump( book_config, f, indent=4)


        self._load_config()