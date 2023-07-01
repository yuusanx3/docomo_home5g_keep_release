import os
import logging
from .base import randomname

class Log:
    """
    ログの設定と出力を行うクラス
    """

    def __init__(self,log_path:str,level:logging=logging.DEBUG) -> None:
        """
        ログの設定と出力を行うクラス
        log_path : ログのパス
        level : ログの出力レベル
        """
        if False == os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(filename)s %(funcName)s [%(levelname)s]: %(message)s')
        file_handler = logging.FileHandler(log_path, encoding="UTF-8")
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)
        self.__class_id = randomname(10)

    def get_logger(self) -> logging:
        """
        loggerを取得する
        """
        return self.__logger

    def info_start(self) -> None:
        """
        開始ログを出力する
        """
        self.__logger.info("====================================================================================================")
        self.__logger.info("----------------------------------------------------------------------------------------------------")
        self.__logger.info("■ 処理を開始します。 <{}>".format(self.__class_id))
        self.__logger.info("----------------------------------------------------------------------------------------------------")

    def info_end(self) -> None:
        """
        終了ログを出力する
        """
        self.__logger.info("----------------------------------------------------------------------------------------------------")
        self.__logger.info("■ 処理を終了します。 <{}>".format(self.__class_id))
        self.__logger.info("----------------------------------------------------------------------------------------------------")
        self.__logger.info("====================================================================================================")
