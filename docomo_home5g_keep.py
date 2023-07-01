####################################################################################################
# メイン処理
# プログラムテンプレートですが案件内容に応じて変更してください。
# VScodeの場合、使い方が分からないクラスやメソッドにカーソルを当てると、ヘルプコメントが表示されます。
####################################################################################################
import os
import traceback
import logging
from common import Config, Log
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from subprocess import CREATE_NO_WINDOW
from selenium.common.exceptions import SessionNotCreatedException
from selenium_assist import auto_dl_chromedriver, get_driver_version_from_error
import psutil
psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)

CONFIG = "docomo_home5g_keep.ini"
"""設定ファイルパス"""

class CommonError(Exception):
    """途中でプログラムを終了させたい場合に発生せさせる例外"""
    pass

class Main():
    """
    メイン処理
    """
    
    def __init__(self) -> None:
        """
        メイン処理
        """
        config_path = os.path.join(os.path.dirname(__file__), CONFIG)
        # 設定ファイル
        self.__config = Config(config_path).get_config()
        log_path = self.__config["log"]["file_path"]
        # ログ
        self.__log = Log(log_path,logging.DEBUG)
        self.__logger = self.__log.get_logger()

    def continue_check(self) -> None:
        """
        プログラムの継続判定
        """
        config_path = os.path.join(os.path.dirname(__file__), CONFIG)
        self.__config = Config(config_path).get_config()
        if "0" == self.__config["continue"]["continue"]:
            raise CommonError("継続フラグが無効になりました。処理を終了します。")
    
    def loop_process(self) -> None:
        """
        ループ処理
        """
        try:
            self.__logger.info("----------------------------------------------------------------------------------------------------")
            self.__logger.info(f"■ {self.__count}度目のチェック")

            # Chromeドライバーの設定
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_service = service.Service(executable_path=self.__config["selenium"]["chromedriver_exe"])
            chrome_service.creation_flags = CREATE_NO_WINDOW
            driver = webdriver.Chrome(service=chrome_service, options=options)

            # ホーム画面読み込み
            driver.get(self.__url_index)

            time.sleep(2)

            # ネットワーク状態
            current_network = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div[1]/div[1]/div[2]/div[2]/div/span[2]")

            self.__logger.info(f"現在のネットワーク=[{current_network.text}]")

            # 5Gでない場合は設定しなおす
            if "5G" != current_network.text:

                # ログイン
                login_btn = driver.find_element(By.XPATH,"/html/body/div/div/div[2]/nav/div[2]/ul/li[7]/button")
                login_btn.click()

                time.sleep(2)

                # パスワード入力
                password = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[4]/div/div/div[2]/form/div[1]/input")
                password.send_keys(self.__config["home5g"]["password"])
                password.submit()

                time.sleep(2)

                # 設定画面へ
                driver.get(self.__url_network)

                time.sleep(2)
    
                # 4Gに変更
                select_mode = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[2]/div[1]/div/select")
                select = Select(select_mode)
                select.select_by_index(1)
                set_apply_btn = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[3]/div/div/button[1]")
                set_apply_btn.click()
                time.sleep(2)
                Alert(driver).accept()

                time.sleep(2)

                # 5Gに変更
                select_mode = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[2]/div[1]/div/select")
                select = Select(select_mode)
                select.select_by_index(0)
                set_apply_btn = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[3]/div/div/button[1]")
                set_apply_btn.click()
                time.sleep(2)
                Alert(driver).accept()

                self.__logger.info("● 5Gに変更しました。")

            driver.close()
            self.__count += 1
            self.__error_count = 0
        
        except SessionNotCreatedException as e:
            version = get_driver_version_from_error(e)
            auto_dl_chromedriver(
                version,
                int(self.__config["selenium"]["target_os"]),
                self.__config["selenium"]["chromedriver_folder"]
                )
            print("新しいドライバーをダウンロードしました。")
        except Exception as e:
            self.__logger.error(str(e))
            self.__error_count += 1
            # 5回連続で失敗した場合は終了する
            if 5 <= self.__error_count:
                raise CommonError("5回連続で失敗しました。処理を終了します。")
        finally:
            self.__logger.info("----------------------------------------------------------------------------------------------------")

    def main(self) -> None:
        """
        メイン処理
        """
        try:
            # 開始ログ出力
            self.__log.info_start()

            # HOME5GのURL
            self.__url_index = self.__config["home5g"]["index"]
            self.__url_network = self.__config["home5g"]["network"]

            # 累計処理回数
            self.__count = 1
            # 連続エラー回数
            self.__error_count = 0

            while True:
                # 継続チェック
                self.continue_check()
                # ループ処理
                self.loop_process()
                # 60秒に1度処理
                time.sleep(60)        
            
        except CommonError as e:
            self.__logger.error(str(e))
        except Exception:
            self.__logger.error(traceback.format_exc())
        finally:
            # 終了ログ出力
            self.__log.info_end()

Main().main()