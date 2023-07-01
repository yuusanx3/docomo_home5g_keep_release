import random
import string

def randomname(n:int):
    """
    英文字のランダムな文字列を作成する
    n : 生成する文字列の長さ
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))