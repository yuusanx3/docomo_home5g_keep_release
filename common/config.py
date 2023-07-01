import configparser

class Config:
    """
    設定ファイル関連の処理を行うクラス
    """ 

    def __init__(self,file_path:str) -> None:
        """
        設定ファイル関連の処理を行うクラス
        file_path : 設定ファイルのパス
        """        
        # 設定情報取得
        self.__config = configparser.ConfigParser()
        self.__config.read(file_path, 'UTF-8')

    def get_config(self) -> configparser:
        """
        設定ファイルの情報を取得する
        """
        return self.__config