"""
 File: ecmb_builder.py
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
from .ecmb_builder_enums import *
from .ecmb_builder_utils import ecmbBuilderUtils
from .ecmb_builder_base import ecmbBuilderBase
from .resize.ecmb_builder_resize_base import ecmbBuilderResizeBase
from ecmblib import ecmbBook, ecmbException


class ecmbBuilder(ecmbBuilderBase):
    
    def initialize(self, init_type: INIT_TYPE) -> None:
        if self._book_config.is_initialized:
            raise ecmbException('Book is allready initialized!')
        
        (chapter_folders, volume_folders) = self._read_folder_structure()        
        for chapter in chapter_folders:
            if len(self._get_image_list(chapter['path'] + chapter['name'])) == 0:
                raise ecmbException('Chapter-folder "' + chapter['path'] + chapter['name'] + '" is empty!')
            
        self._book_config.init_config(init_type, chapter_folders, volume_folders)

        print('\033[1;32;40m  Open "' + self._source_dir + 'book_config.json" and add all the meta-data to your book!\x1b[0m\n')


    def build(self, volumes: int|list[int]) -> None:
        if not self._book_config.is_initialized:
            raise ecmbException('Book is not initialized!')
        
        resize_method = self._load_resize_method()
        
        if self._book_config.chapter_list:
            self._build_book(resize_method, '', self._book_config.chapter_list)
        else:
            if volumes != None:
                volumes = volumes if type(volumes) == list else volumes.split(',')
                volumes = [e.strip() for e in volumes]

            volume_nr = 0
            for volume_dir, chapter_list in self._book_config.volume_list.items():
                volume_nr += 1
                if volumes and str(volume_nr) not in volumes:
                    continue
                self._build_book(resize_method, volume_dir, chapter_list, volume_nr)


    def _build_book(self, resize_method: ecmbBuilderResizeBase, volume_dir: str, chapter_list: list, volume_nr: int = None) -> None:
        config = self._book_config

        file_name = re.sub(r'[^a-zA-Z0-9]+', ' ', config.book_title).strip()
        file_name += f' Vol.{volume_nr}' if volume_nr != None else ''
        file_name += '.ecmb'

        print('  ' + file_name, flush=True)

        book_uid = self._generate_book_uid()
        book = ecmbBook(config.book_type, config.book_language, book_uid, config.resize_width, config.resize_height)

        self._add_meta_data(book, volume_nr)
        self._set_cover(book, resize_method, volume_dir)
        self._add_content(book, resize_method, chapter_list)

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        book.write(self._output_dir + file_name)

        print('', flush=True)


    def _set_cover(self, book: ecmbBook, resize_method: ecmbBuilderResizeBase, volume_dir: str) -> None:
        volume_dir = self._source_dir + volume_dir

        image_list = ecmbBuilderUtils.list_files(volume_dir, None, r'^(f|front|cover_front)[.](jpg|jpeg|png|webp)$', 0)
        if len(image_list):
            image_path = image_list[0]['path'] + image_list[0]['name']
            image = resize_method.process(image_path)
            book.content.set_cover_front(image[0])

        image_list = ecmbBuilderUtils.list_files(volume_dir, None, r'^(r|rear|cover_rear)[.](jpg|jpeg|png|webp)$', 0)
        if len(image_list):
            image_path = image_list[0]['path'] + image_list[0]['name']
            image = resize_method.process(image_path)
            book.content.set_cover_rear(image[0])
            

    
    def _add_content(self, book: ecmbBook, resize_method: ecmbBuilderResizeBase, chapter_list: list) -> None:
        for chapter in tqdm(chapter_list, desc='  add content'):
            folder = book.content.add_folder(chapter['path'])
            image_list = self._get_image_list(chapter['path'])
            for image in image_list:
                image_path = chapter['path'] + image['name']
                image = resize_method.process(image_path)
                if len(image) == 3:
                    folder.add_image(image[0], image[1], image[2], unique_id=image_path)
                else:
                    folder.add_image(image[0], unique_id=image_path)
            
            target = None
            target_side = None
            if chapter.get('start_with'):
                start_with = chapter.get('start_with').split('#')
                target = chapter['path'] + start_with[0]
                target_side = start_with[1] if len(start_with) == 2 else None

            book.navigation.add_chapter(chapter.get('label'), folder, target, target_side, chapter.get('title'))


    def _add_meta_data(self, book: ecmbBook, volume_nr: int = None) -> None:
        config = self._book_config
        meta_data = config.meta_data
        original = meta_data['original']
        based_on = meta_data['based_on']

        # mandatory
        book.metadata.set_title(config.book_title)
        book.metadata.set_volume(volume_nr)

        # meta data
        book.metadata.set_isbn(meta_data.get('isbn'))
        book.metadata.set_publishdate(meta_data.get('publishdate'))
        if type(meta_data.get('publisher')) == dict and meta_data['publisher'].get('name'):
            book.metadata.set_publisher(meta_data['publisher'].get('name'), href = meta_data['publisher'].get('href'))
        book.metadata.set_summary(meta_data.get('summary'))
        book.metadata.set_pages(meta_data.get('pages'))
        book.metadata.set_notes(meta_data.get('notes'))

        if type(meta_data.get('genres')) == list:
            for genre in meta_data.get('genres'):
                if genre:
                    book.metadata.add_genre(genre)

        if type(meta_data.get('warnings')) == list:
            for warning in meta_data.get('warnings'):
                book.metadata.add_content_warning(warning)

        if type(meta_data.get('authors')) == list:
            for author in meta_data.get('authors'):
                if type(author) == dict and author.get('name'):
                    book.metadata.add_author(author.get('name'), author.get('role'), href = author.get('href'))

        if type(meta_data.get('editors')) == list:
            for editor in meta_data.get('editors'):
                if type(editor) == dict and editor.get('name'):
                    book.metadata.add_editor(editor.get('name'), editor.get('role'), href = editor.get('href'))

        # original
        book.original.set_language(original.get('language'))
        book.original.set_isbn(original.get('isbn'))
        book.original.set_publishdate(original.get('publishdate'))
        if type(original.get('publisher')) == dict and original['publisher'].get('name'):
            book.original.set_publisher(original['publisher'].get('name'), href = original['publisher'].get('href'))
        book.original.set_title(original.get('title'))

        if type(original.get('authors')) == list:
            for author in original.get('authors'):
                if type(author) == dict and author.get('name'):
                    book.original.add_author(author.get('name'), author.get('role'), href = author.get('href'))

        # based_on
        book.based_on.set_type(based_on.get('type'))
        book.based_on.set_language(based_on.get('language'))
        book.based_on.set_isbn(based_on.get('isbn'))
        book.based_on.set_publishdate(based_on.get('publishdate'))
        if type(based_on.get('publisher')) == dict and based_on['publisher'].get('name'):
            book.based_on.set_publisher(based_on['publisher'].get('name'), href = based_on['publisher'].get('href'))
        book.based_on.set_title(based_on.get('title'))

        if type(based_on.get('authors')) == list:
            for author in based_on.get('authors'):
                if type(author) == dict and author.get('name'):
                    book.based_on.add_author(author.get('name'), author.get('role'), href = author.get('href'))


    def _generate_book_uid(self) -> str:
        config = self._book_config

        hash = config.book_title + str(datetime.now())

        if type(config.meta_data.get('publisher')) == dict and config.meta_data['publisher'].get('name'):
            prefix = str(config.meta_data['publisher'].get('name'))
        else: 
            prefix = config.book_title

        prefix = re.sub(r'[^a-z0-9]', '', prefix.lower())
        return prefix + '_' + hashlib.md5(hash.encode()).hexdigest()
    
    
    def _load_resize_method(self) -> ecmbBuilderResizeBase:
        config = self._book_config

        resize_methods = self._builder_config.resize_methods
        resize_method = resize_methods[config.resize_method]

        mod = __import__(resize_method[0], globals(), locals(), [resize_method[1]], 0)
        clas = getattr(mod, resize_method[1])

        return clas(config.resize_width, config.resize_height, config.webp_compression, config.compress_all)
