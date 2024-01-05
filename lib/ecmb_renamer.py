"""
 File: ecmb_renamer.py
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
from datetime import datetime
from.ecmb_builder_enums import *
from .ecmb_builder_base import ecmbBuilderBase
from ecmblib import ecmbException, ecmbUtils


class ecmbRenamer(ecmbBuilderBase):
    
    def rename(self, rename_type: RENAME_TYPE, rename_items: RENAME_ITEMS) -> None:
        
        rename_items = ecmbUtils.enum_value(rename_items)
        rename_type = ecmbUtils.enum_value(rename_type)
        ecmbUtils.validate_enum(True, 'rename_items', rename_items, RENAME_ITEMS)
        ecmbUtils.validate_enum(True, 'rename_type', rename_type, RENAME_TYPE)

        if rename_items != RENAME_ITEMS.IMAGES.value:
            if self._book_config.is_initialized:
                raise ecmbException('Book is allready initialized!')
            
        self._rename_volumes(rename_items, rename_type)
        self._rename_chapters(rename_items, rename_type)
        self._rename_images(rename_items, rename_type)

        print('', flush=True)

    
    def parse(self) -> None:
        if self._book_config.is_initialized:
            raise ecmbException('Book is allready initialized!')
        if self._rename_chapters(RENAME_ITEMS.CHAPTERS.value, 'parse'):
            self._rename_chapters(RENAME_ITEMS.CHAPTERS.value, RENAME_TYPE.PREFIX.value)
        
        print('', flush=True)


    def split(self, volumes: int) -> None:
        if self._book_config.is_initialized:
            raise ecmbException('Book is allready initialized!')
        
        (chapter_folders, volume_folders) = self._read_folder_structure()
        if volume_folders:
            raise ecmbException('Book has allready volumes!')
        
        chapter_cnt = len(chapter_folders)
        if chapter_cnt == 1:
            raise ecmbException('Book has only one chapter!')
        
        if volumes.isnumeric():
            volumes = int(volumes)

        ecmbUtils.validate_int(True, 'volumes', volumes, 1, chapter_cnt-1)
        volumes = int(volumes) if volumes else 0
		
        total_images = 0
        for chapter in chapter_folders:
            image_list = self._get_image_list(chapter['path'] + chapter['name'])
            chapter['images'] = len(image_list)
            if chapter['images'] == 0:
                raise ecmbException('"'+ chapter['name'] + '" has no images!')
            total_images += chapter['images']
            
        avg_pages = round(total_images / volumes)
		
        volume_nr = 0 
        while volume_nr < volumes:
            volume_nr += 1
            volume_dir = self._source_dir + 'ecmbbuilder_tmpname_' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + ('_{}'.format(str(volume_nr).zfill(3)))
            os.mkdir(volume_dir)

            found = False
            page_count = 0
            for chapter in chapter_folders.copy():
                dif_with = abs(page_count + chapter['images'] - avg_pages)
                div_without = abs(page_count - avg_pages)

                if page_count and volume_nr < volumes and (dif_with > div_without and len(chapter_folders) > 1):
                    break
                
                found = True
                page_count += chapter['images']
                os.rename(chapter['path'] + chapter['name'], volume_dir + '\\' + chapter['name'])
                chapter_folders.remove(chapter)

            if not found:
                os.remove(volume_dir)
        
        (chapter_folders, volume_folders) = self._read_folder_structure()
        if volume_folders:
            self._rename_path(RENAME_ITEMS.VOLUMES.value, RENAME_TYPE.RENAME.value, volume_folders)

        print('  created '+ str(len(volume_folders)) + ' volumes', flush=True)
        print('', flush=True)


        
        

    def _rename_volumes(self, rename_items: RENAME_ITEMS, rename_type :RENAME_TYPE) -> int:
        if rename_items in [RENAME_ITEMS.VOLUMES.value, RENAME_ITEMS.ALL.value]:
            (chapter_folders, volume_folders) = self._read_folder_structure()
            volumes = 0
            if volume_folders:
                volumes = self._rename_path(RENAME_ITEMS.VOLUMES.value, rename_type, volume_folders)
            print(f'  {rename_type} {volumes} volumes', flush=True)
            return volumes


    def _rename_chapters(self, rename_items: RENAME_ITEMS, rename_type :RENAME_TYPE) -> int:
        if rename_items in [RENAME_ITEMS.CHAPTERS.value, RENAME_ITEMS.ALL.value]:
            (chapter_folders, volume_folders) = self._read_folder_structure()
            if volume_folders:
                chapter_nr = 0
                for volume in volume_folders:
                    chapter_nr = self._rename_path(RENAME_ITEMS.CHAPTERS.value, rename_type, volume['chapters'], chapter_nr)
            else: 
                chapter_nr = self._rename_path(RENAME_ITEMS.CHAPTERS.value, rename_type, chapter_folders)
            print(f'  {rename_type} {chapter_nr} chapters', flush=True)
            return chapter_nr


    def _rename_images(self, rename_items: RENAME_ITEMS, rename_type :RENAME_TYPE) -> int:
        if rename_items in [RENAME_ITEMS.IMAGES.value, RENAME_ITEMS.ALL.value]:
            (chapter_folders, volume_folders) = self._read_folder_structure()
            image_nr = 0
            for folder in chapter_folders:
                image_list = self._get_image_list(folder['path'] + folder['name'])
                image_nr = self._rename_path(RENAME_ITEMS.IMAGES.value, rename_type, image_list, image_nr)
                
            print(f'  {rename_type} {image_nr} images', flush=True)
            return image_nr


    def _rename_path(self, rename_items: RENAME_ITEMS, rename_type :RENAME_TYPE, path_list: list, start_at: int = 0) -> int:
        tmp_name = '__ecmbbuilder_tmpname_' + hashlib.md5(str(datetime.now()).encode()).hexdigest() + '_'

        if rename_type == RENAME_TYPE.REVERSE.value:
            path_list.reverse()
            rename_type = RENAME_TYPE.PREFIX.value

        if rename_items == RENAME_ITEMS.VOLUMES.value:
            prefix = 'volume_'
            zfill = 3
        if rename_items == RENAME_ITEMS.CHAPTERS.value:
            prefix = 'chapter_'
            zfill = 4
        if rename_items == RENAME_ITEMS.IMAGES.value:
            prefix = 'img_'
            zfill = 6

        if rename_type in [RENAME_TYPE.PREFIX.value, RENAME_TYPE.ZEROPAD.value, 'parse']:
            if rename_items == RENAME_ITEMS.VOLUMES.value:
                regex = r'^volume_[0-9]+(_)?'
            if rename_items == RENAME_ITEMS.CHAPTERS.value:
                regex = r'^chapter_[0-9]+(_)?'
            if rename_items == RENAME_ITEMS.IMAGES.value:
                regex = r'^img_[0-9]+(_)?'

        if rename_type == RENAME_TYPE.RENAME.value:
            regex = r'.*'
        
        if rename_type == RENAME_TYPE.ZEROPAD.value or rename_type == 'parse':
            for item in path_list:
                if re.search(regex, item['name']):
                    return start_at
        
        try:
            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = item['name'] + tmp_name + (str(cnt).zfill(zfill))
                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['name'], item['path'] + new_name)
                item['tmp_name'] = new_name

            cnt = start_at
            for item in path_list:
                cnt += 1
                new_name = re.sub(regex, '', item['name'])
                if item.get('extension'):
                    new_name = re.sub('[.]' + item.get('extension') + '$', '', new_name)
                
                if rename_type == 'parse':
                    match = re.search(r'c[^0-9]*([0-9]+)([^0-9a-z]+([0-9]+))?[^0-9]*$', new_name, re.IGNORECASE)
                    if match:
                        new_name_tmp = prefix + (str(match.group(1)).zfill(zfill))
                        if match.group(3):
                            new_name = new_name_tmp + str(match.group(3)).zfill(3) + ('_'+ new_name if new_name else '')
                        else:
                            new_name = new_name_tmp + '000' + ('_'+ new_name if new_name else '')
                    else:
                        new_name = prefix + (str(0).zfill(zfill)) + '000' + ('_'+ new_name if new_name else '')

                elif rename_type == RENAME_TYPE.ZEROPAD.value:
                    new_name = prefix + (str(0).zfill(zfill)) + '0' + ('_'+ new_name if new_name else '')
                else:
                    new_name = prefix + (str(cnt).zfill(zfill)) + '0' + ('_'+ new_name if new_name else '')

                new_name += '.' + item.get('extension') if item.get('extension') else ''
                os.rename(item['path'] + item['tmp_name'], item['path'] + new_name)
        except PermissionError:
            try:
                for item in path_list:
                    if item.get('tmp_name'):
                        os.rename(item['path'] + item['tmp_name'], item['path'] + item['name'])
            except:
                pass
            
            raise ecmbException('Permission denied for rename folders/images. Please close opened files and folders!')

        return cnt


        
    



        
