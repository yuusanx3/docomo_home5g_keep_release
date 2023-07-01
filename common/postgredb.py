import logging
import psycopg2
from psycopg2.extras import DictCursor
from .base import randomname

class PostgreDBError(Exception):
    """
    PostgreDBクラスの処理に失敗した場合に発生する例外
    """
    pass

class PostgreDB:
    """
    PostgreDBでのSQL実行などの処理を行うクラスです。
    インスタンス1つにつき、セッションを1つ作成できます。
    """

    def __init__(self,db_host:str,db_port:str,db_database:str,db_user:str,db_password:str
        ,auto_commit=False,auto_rollback=False,auto_close=False,logger:logging=None) -> None:
        """
        PostgreDBでのSQL実行などの処理を行うクラスです。
        インスタンス1つにつき、セッションを1つ作成できます。
        db_host : ホスト
        db_port : ポート
        db_database : データベース
        db_user : ユーザーID
        db_password : パスワード
        auto_commit : 自動コミット（SQL文を実行するたびに自動でコミットします）
        auto_rollback : 自動ロールバック（DB処理中に例外が発生した場合に自動でロールバックします）
        auto_close : 自動クローズ（DB処理中に例外が発生した場合に自動でクローズします（※自動ロールバックもTrueになります））
        logger : ロガー
        """
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_database = db_database
        self.__db_user = db_user
        self.__db_password = db_password
        self.__auto_commit = auto_commit
        if auto_close: self.__auto_rollback = True
        else: self.__auto_rollback = auto_rollback
        self.__auto_close = auto_close
        self.__logger = logger
        # コネクション
        self.__connection = None
        # カーソル
        self.__cursor = None
        # クラスID  ログで同じクラスを特定しやすくします
        self.__class_id = randomname(10)

    def open_session(self) -> None:
        """
        PostgreDBに接続しセッションを開始します
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB セッション開始:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            self.__connection = psycopg2.connect("host={0} port={1} dbname={2} user={3} password={4}"
                .format( 
                    self.__db_host,
                    self.__db_port,
                    self.__db_database,
                    self.__db_user,
                    self.__db_password
            ))
            self.__cursor = self.__connection.cursor(cursor_factory=DictCursor)
            self.__logger.debug("● DBへの接続に成功しました。")
        except Exception:
            self.__logger.error("● DBへの接続に失敗しました。")
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__auto_close: self.close_session()
            raise PostgreDBError("DBへの接続に失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")

    def execute_query(self,sql:str,parameter:tuple=None) -> list:
        """
        SQL（クエリ）を実行します（トランザクション開始）
        sql : SQL文
        parameter : パラメータ
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB SQL実行:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            self.__logger.debug("▼ SQL")
            self.__logger.debug(sql)
            if parameter:
                self.__logger.debug("▼ パラメータ")
                self.__logger.debug(parameter)
            # SQLを実行する
            self.__cursor.execute(sql,parameter)
            results = self.__cursor.fetchall()
            # 汎用の辞書型に入れ替え
            dict_results = []
            for result in results:
                dict_results.append(dict(result))
            self.__logger.debug("● SQLの実行に成功しました。")
            if results:
                self.__logger.debug("▼ 実行結果 件数=[{}]".format(len(dict_results)))
                for dict_result in dict_results:
                    self.__logger.debug(dict(dict_result))
            else:
                self.__logger.debug("▼ 実行結果 件数=[0]")
            return results
        except Exception:
            self.__logger.error("● SQLの実行に失敗しました。")
            # ロールバックする
            if self.__auto_rollback: self.rollback()
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__auto_close: self.close_session()
            raise PostgreDBError("SQL（クエリ）の実行に失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")

    def execute_non_query(self,sql:str,parameter:tuple=None) -> None:
        """
        SQL（ノンクエリ）を実行します（トランザクション開始）
        sql : SQL文
        parameter : パラメータ
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB SQL実行:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            self.__logger.debug("▼ SQL")
            self.__logger.debug(sql)
            if parameter:
                self.__logger.debug("▼ パラメータ")
                self.__logger.debug(parameter)
            # SQLを実行する
            self.__cursor.execute(sql,parameter)
            self.__logger.debug("● SQLの実行に成功しました。")
            # コミットする
            if self.__auto_commit: self.commit()
        except Exception:
            self.__logger.error("● SQLの実行に失敗しました。")
            # ロールバックする
            if self.__auto_rollback: self.rollback()
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__auto_close: self.close_session()
            raise PostgreDBError("SQL（ノンクエリ）の実行に失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")

    def commit(self) -> None:
        """
        トランザクションをコミットします
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB コミット:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            # コミットする
            self.__connection.commit()
            self.__logger.debug("● コミットに成功しました。")
        except Exception:
            self.__logger.error("● コミットに失敗しました。")
            # ロールバックする
            if self.__auto_rollback: self.rollback()
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__auto_close: self.close_session()
            raise PostgreDBError("コミットに失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")

    def rollback(self) -> None:
        """
        トランザクションをロールバックします
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB ロールバック:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            # ロールバックする
            self.__connection.rollback()
            self.__logger.debug("● ロールバックに成功しました。")
            return True
        except Exception:
            self.__logger.error("● ロールバックに失敗しました。")
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__auto_close: self.close_session()
            raise PostgreDBError("ロールバックに失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")

    def close_session(self) -> None:
        """
        PostgreDBセッションを終了し接続を切断します。
        """
        try:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
            self.__logger.debug("■ DB セッション終了:[{}/{}] <{}>".format(self.__db_host,self.__db_database,self.__class_id))
            # トランザクションとセッション終了しDBの接続を切断する
            if self.__cursor: self.__cursor.close()
            if self.__connection: self.__connection.close()
            self.__logger.debug("● DBの切断に成功しました。")
            return True
        except Exception:
            self.__logger.error("● DBの切断に失敗しました。")
            raise PostgreDBError("DBの切断に失敗しました。")
        finally:
            self.__logger.debug("----------------------------------------------------------------------------------------------------")
