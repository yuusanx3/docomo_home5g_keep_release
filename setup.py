# coding: utf-8
# cx_Freeze 用セットアップファイル
import os
import sys
import shutil
from cx_Freeze import setup, Executable

APP_NAME = "Docomo Home5G Keep"
VERSION = "1.0.0.1"

# 今あるAPP_NAMEのフォルダを削除
if os.path.exists("./build/"+APP_NAME):
    shutil.rmtree("./build/"+APP_NAME)

build_exe_options = {
      # 取り込みたいファイルやフォルダ名を記載します。
      "include_files": [
          "bin",
      ],
}
 
base = None

# GUI=有効, CUI=無効 にする
if sys.platform == 'win32' : base = 'Win32GUI'
 
# exe にしたい python ファイルを指定
exe = Executable(script = 'docomo_home5g_keep.py',
    base = base, icon='')
 
# セットアップ
setup(name = APP_NAME,
    version = VERSION,
    description = APP_NAME,
    options={
    "build_exe": build_exe_options,
    },
    executables = [exe])

# exe の入ったフォルダ名のリネーム
oldpath = "./build/exe.win-amd64-3.9"
newpath = "./build/"+APP_NAME
os.rename(oldpath, newpath)