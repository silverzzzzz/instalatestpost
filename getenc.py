# 文字コードの自動判定関数
def getEncode(filepath):
    encs = "iso-2022-jp euc-jp shift_jis utf-8".split()
    for enc in encs:
        with open(filepath, encoding=enc) as fr:
            try:
                fr = fr.read()
            except UnicodeDecodeError:
                continue
        return enc


if __name__ == '__main__':

    import sys

    argv = sys.argv
    argc = len(argv)
    hikisuu = 1

    if argc <= hikisuu:
        print("文字エンコードを調べるテキストファイル名を１つを引数として指定します。")
        print("使い方")
        print("$ ./getenc.py テキストファイル.CSV(txt)")
    else:
        FR = argv[1]
        print(getEncode(FR))
