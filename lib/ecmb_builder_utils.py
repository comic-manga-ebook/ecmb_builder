"""
 File: ecmb_builder_utils.py
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

import re, os
from functools import cmp_to_key


class ecmbBuilderUtils():
    
    @staticmethod
    def list_files(dirname: str, dir_pattern: str = None, file_pattern: str = None, max_level: int = None, level: int = 0) -> list:
        if type(max_level) == int:
            if max_level == -1:
                return []
            max_level -= 1
        
        file_list = []
        dirname = (dirname if dirname[-1] in ["/", "\\"] else dirname + "\\")

        tmp_list = [ele for ele in os.scandir(dirname)]        
        tmp_list.sort(key=cmp_to_key(ecmbBuilderUtils.sort_dir_elements))

        for ele in tmp_list:
            if ele.name in [".", ".."]:
                continue
            if ele.is_dir(follow_symlinks=False):
                if not isinstance(dir_pattern, str) or (dir_pattern and re.search(dir_pattern, ele.name, re.IGNORECASE)):
                    file_list += ecmbBuilderUtils.list_files(
                        dirname + ele.name, dir_pattern, file_pattern, max_level, level + 1
                    )
            elif ele.is_file(follow_symlinks=False):
                if not isinstance(file_pattern, str) or (file_pattern and re.search(file_pattern, ele.name, re.IGNORECASE)):
                    extension = re.search(r'\.([a-z0-9]+)$', ele.name, re.IGNORECASE)
                    extension = extension.group(1).lower() if extension else None
                    file_list.append({'path': str(dirname), 'name': ele.name, 'level': level, 'extension': extension})

        return file_list
    
    
    @staticmethod
    def list_dirs(dirname:str, dir_pattern: str = None, max_level: int = None, level: int = 0) -> list:
        if type(max_level) == int:
            if max_level == -1:
                return []
            max_level -= 1

        dir_list = []
        dirname = (dirname if dirname[-1] in ["/", "\\"] else dirname + "\\")

        tmp_list = [ele for ele in os.scandir(dirname)]        
        tmp_list.sort(key=cmp_to_key(ecmbBuilderUtils.sort_dir_elements))

        for ele in tmp_list:
            if ele.name in [".", ".."]:
                continue
            if ele.is_dir(follow_symlinks=False):
                if not isinstance(dir_pattern, str) or (dir_pattern and re.search(dir_pattern, ele.name, re.IGNORECASE)):  
                    dir_list.append({'path': str(dirname), 'name': ele.name, 'level': level})
                    dir_list += ecmbBuilderUtils.list_dirs(
                        dirname + ele.name, dir_pattern, max_level, level + 1
                    )

        return dir_list
    
    @staticmethod
    def list_dirs_recursive(dirname:str, dir_pattern: str = None, max_level: int = None, level: int = 0) -> list:
        if type(max_level) == int:
            if max_level == -1:
                return []
            max_level -= 1

        dir_list = []
        dirname = (dirname if dirname[-1] in ["/", "\\"] else dirname + "\\")

        tmp_list = [ele for ele in os.scandir(dirname)]        
        tmp_list.sort(key=cmp_to_key(ecmbBuilderUtils.sort_dir_elements))

        for ele in tmp_list:
            if ele.name in [".", ".."]:
                continue
            if ele.is_dir(follow_symlinks=False):
                if not isinstance(dir_pattern, str) or (dir_pattern and re.search(dir_pattern, ele.name, re.IGNORECASE)):  
                    dir_list.append({
                        'path': str(dirname),
                        'name': ele.name,
                        'level': level,
                        'children': ecmbBuilderUtils.list_dirs_recursive(
                            dirname + ele.name, dir_pattern, max_level, level + 1
                        )})

        return dir_list
    
    @staticmethod
    def list_tree_recursive(dirname: str, dir_pattern: str = None, file_pattern: str = None, max_level: int = None, level: int = 0) -> list:
        if type(max_level) == int:
            if max_level == -1:
                return []
            max_level -= 1
        
        tree_list = []
        dirname = (dirname if dirname[-1] in ["/", "\\"] else dirname + "\\")

        tmp_list = [ele for ele in os.scandir(dirname)]        
        tmp_list.sort(key=cmp_to_key(ecmbBuilderUtils.sort_dir_elements))

        for ele in tmp_list:
            if ele.name in [".", ".."]:
                continue
            if ele.is_dir(follow_symlinks=False):
                if not isinstance(dir_pattern, str) or (dir_pattern and re.search(dir_pattern, ele.name, re.IGNORECASE)):
                    tree_list.append({
                        'type': 'dir', 
                        'path': str(dirname),
                        'name': ele.name, 
                        'level': level, 
                        'children': ecmbBuilderUtils.list_tree_recursive(
                            dirname + ele.name, dir_pattern, file_pattern, max_level, level + 1
                        )})
            elif ele.is_file(follow_symlinks=False):
                if not isinstance(file_pattern, str) or (file_pattern and re.search(file_pattern, ele.name, re.IGNORECASE)):
                    extension = re.search(r'\.([a-z0-9]+)$', ele.name, re.IGNORECASE)
                    extension = extension.group(1).lower() if extension else None
                    tree_list.append({'type': 'file', 'path': str(dirname), 'name': ele.name, 'level': level, 'extension': extension})

        return tree_list
    
    @staticmethod
    def sort_dir_elements(ele1, ele2):
        return 1 if ele1.name > ele2.name else -1