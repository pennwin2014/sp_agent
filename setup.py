# -*- coding: utf-8 -*-
'''
Created on 2012-4-20

@author: cheng.tang
'''

from cx_Freeze import setup, Executable
import os
import sys
from tcutils.disttools import make_dist

if sys.platform != 'win32':
    print u"只能在window平台打包"
    sys.exit(1)

dll_files = ['penn.dll']


buildOptions = {"includes": [],
                    "include_files": dll_files,
                    "optimize": 2,
                    "create_shared_zip": True,
                    "packages": []}

VERSION = "1.0.0"

setup(name="sp_can_reciever",
  version=VERSION,
  description=u"汇多pos机接收can数据程序",
  options={"build_exe": buildOptions},
  executables=[Executable('socket_svr.py',
                          targetName="socket_svr.exe",
                          copyDependentFiles=True,
                          appendScriptToExe=False,
                          appendScriptToLibrary=True)])


make_dist('sp_can_reciever', VERSION)

