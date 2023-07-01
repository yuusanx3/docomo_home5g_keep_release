import os
import time
from common import Config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from subprocess import CREATE_NO_WINDOW
from selenium.common.exceptions import SessionNotCreatedException
from selenium_assist import auto_dl_chromedriver, get_driver_version_from_error

CONFIG = "docomo_home5g_keep.ini"
"""設定ファイルパス"""

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

    def main(self) -> None:
        """
        メイン処理
        """
        try:
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
            driver.get(self.__config["home5g"]["index"])

            time.sleep(2)

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
            driver.get(self.__config["home5g"]["network"])

            time.sleep(2)

            # 4Gに変更
            select_mode = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[2]/div[1]/div/select")
            select = Select(select_mode)
            select.select_by_index(1)
            set_apply_btn = driver.find_element(By.XPATH,"/html/body/div/div/div[3]/section/div/div[2]/div/div/div[3]/div/div/button[1]")
            set_apply_btn.click()
            time.sleep(2)
            Alert(driver).accept()

            driver.close()
            
        except SessionNotCreatedException as e:
            version = get_driver_version_from_error(e)
            auto_dl_chromedriver(
                version,
                int(self.__config["selenium"]["target_os"]),
                self.__config["selenium"]["chromedriver_folder"]
                )

# Docomo 5G Keep を止める
import stop

Main().main()