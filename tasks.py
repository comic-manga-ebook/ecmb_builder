"""
 File: tasks.py
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

from invoke import task
from lib.ecmb_builder_enums import *
from lib.ecmb_renamer import ecmbRenamer
from lib.ecmb_builder import ecmbBuilder
from ecmblib import ecmbException



@task()
def zeropad(ctx, rename_items: RENAME_ITEMS, folder_name):
	renameservice(ctx, RENAME_TYPE.ZEROPAD, rename_items, folder_name)

@task()
def prefix(ctx, rename_items: RENAME_ITEMS, folder_name):
	renameservice(ctx, RENAME_TYPE.PREFIX, rename_items, folder_name)

@task()
def reverse(ctx, rename_items: RENAME_ITEMS, folder_name):
	renameservice(ctx, RENAME_TYPE.REVERSE, rename_items, folder_name)

@task()
def rename(ctx, rename_items: RENAME_ITEMS, folder_name):
	renameservice(ctx, RENAME_TYPE.RENAME, rename_items, folder_name)


def renameservice(ctx, rename_type: RENAME_TYPE, rename_items: RENAME_ITEMS, folder_name: str):
	print(' ', flush=True)
	try:
		renamer = ecmbRenamer(folder_name)
		renamer.rename(rename_type, rename_items)
		print('\033[1;32;40m  SUCCESS!\x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)

@task()
def parse(ctx, rename_items: RENAME_ITEMS, folder_name: str):
	print(' ', flush=True)
	try:
		renamer = ecmbRenamer(folder_name)
		renamer.parse(rename_items)
		print('\033[1;32;40m  SUCCESS!\x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)

@task()
def group(ctx, rename_items: RENAME_ITEMS, volumes: int, folder_name: str):
	print(' ', flush=True)
	try:
		renamer = ecmbRenamer(folder_name)
		renamer.group(rename_items, volumes)
		print('\033[1;32;40m  SUCCESS!\x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)


@task()
def init(ctx, init_type: INIT_TYPE, folder_name: str):
	print(' ', flush=True)
	try:
		builder = ecmbBuilder(folder_name)
		builder.initialize(init_type)
		print('\033[1;32;40m  SUCCESS!\x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)
	

@task(optional=["volumes"])
def build(ctx, folder_name: str, volumes: str = None):
	print(' ', flush=True)
	try:
		builder = ecmbBuilder(folder_name)
		builder.build(volumes)
		print('\033[1;32;40m  SUCCESS! \x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)
	

