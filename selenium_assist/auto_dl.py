#######################################################################################################################
# 名称 : WEBドライバーを自動でダウンロードするモジュール
# 概要 : 指定したパスに、指定した種類のChromeドライバーをダウンロードします。
#----------------------------------------------------------------------------------------------------------------------
# v1.0.0.0 : 2023/06/07 友木 新規作成
#######################################################################################################################
import os
import requests
import shutil
import re

TARGET_OS_OPTION_NUM = [0,1,2,3]
TARGET_OS_OPTION = [
    "chromedriver_linux64.zip",
    "chromedriver_mac64.zip",
    "chromedriver_mac_arm64.zip",
    "chromedriver_win32.zip"
    ]

LATEST_RELEASE_URL = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}"
DOWNLOAD_URL = "https://chromedriver.storage.googleapis.com/{}/{}"

VERSION_REGEX = r"Current\x20browser\x20version\x20is\x20(.*)\x20with"

def auto_dl_chromedriver(version:int,target_os:int,folder_path:str) -> None:
    """
    Chromeドライバーを自動でダウンロードします。
    version     : Chromeドライバーのバージョン \\
    target_os   : 
    linux 64bit   -> 0 ,
    mac 64bit     -> 1 ,
    mac arm 64bit -> 2 ,
    windows 32bit -> 3 
    folder_path : ダウンロードするフォルダパス
    """
    # 引数のOSの値が正常かチェック
    if target_os not in TARGET_OS_OPTION_NUM:
        raise Exception("指定したOSのドライバーがありません。")
    # 指定したフォルダパスが無ければ作成
    if False == os.path.exists(os.path.dirname(folder_path)):
        os.makedirs(os.path.dirname(folder_path))

    # 指定したバージョンの最新のドライバーバージョンを取得
    response = requests.get(LATEST_RELEASE_URL.format(version))
    # バージョンが存在しない場合エラー
    if not response.ok:
        raise Exception("指定したバージョンのドライバーがありません。")
    
    # ドライバーのダウンロード
    response = requests.get(DOWNLOAD_URL.format(response.text,TARGET_OS_OPTION[target_os]))
    # ダウンロードするファイル名を決定
    file_name = os.path.join(folder_path,TARGET_OS_OPTION[target_os])
    with open(file_name ,mode='wb') as f:
        f.write(response.content)
    
    # zipファイルの解凍
    shutil.unpack_archive(file_name,folder_path)

    # zipファイルの削除
    os.remove(file_name)

def get_driver_version_from_error(e:str) -> int:
    """
    SessionNotCreatedExceptionのインスタンスから
    必要なドライバーのバージョンを特定する \\
    e : エラー
    """
    version = re.findall(VERSION_REGEX, e.msg)[0]
    version = version.split('.')[0]
    return int(version)