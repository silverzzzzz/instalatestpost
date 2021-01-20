import os
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
import time
import random
import logging
import traceback
import sys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from getenc import getEncode
import signal

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)


# テキストをゆっくり入力


def input_text_slowly(path, text, time_a, time_b):
    for word in text:
        slp_time = random.uniform(time_a, time_b)
        path.send_keys(word)
        time.sleep(slp_time)

# CSV読み込み


def read_csv(csvname):
    # 文字コードの取得
    enc = getEncode(csvname)
    # CSVの読み込み
    df = pd.read_csv(csvname, dtype=object, encoding=enc)
    return df

# エラー発生時スクリーンショットを取る＆HTMLを出力


def save_screen(driver, fname):
    fname = "error/"+fname + str(int(time.time()))+".jpg"
    # パスを指定
    FILENAME = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), fname)
    # サイズ調整
    w = driver.execute_script("return document.body.scrollWidth;")
    h = driver.execute_script("return document.body.scrollHeight;")
    driver.set_window_size(w, h)
    driver.save_screenshot(FILENAME)


def save_html(driver, fname):
    fname = "error/" + fname + str(int(time.time())) + ".html"
    # パスを指定
    FILENAME = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), fname)
    html = driver.page_source
    with open(FILENAME, 'w', encoding='utf-8_sig') as f:
        f.write(html)


def login_action(driver, userid, password):
    ######
    # Webサイトを開く
    ######
    driver.get("https://www.instagram.com/")
    time.sleep(2)

    # リダイレクトされた場合
    cur_url = str(driver.current_url)
    login_url = "https://www.instagram.com/"
    print(cur_url)
    # ログイン画面だったらログイン
    if cur_url == login_url:
        # ID,PASSの入力
        time.sleep(1)
        logid_area = driver.find_element_by_name('username')
        logpass_area = driver.find_element_by_name('password')
        input_text_slowly(logid_area, userid, 0.2, 0.5)
        input_text_slowly(logpass_area, password, 0.2, 0.5)
        # ログインボタンクリック
        time.sleep(3)
        driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div').click()

# 投稿日取得の関数


def get_latest_date(driver, url):
    try:
        acname = "取得できませんでした"
        postdata = "取得できませんでした"
        driver.get(url)
        time.sleep(2)
    except:
        save_screen(driver, 'notfound')
        save_html(driver, 'notfound')
    else:
        try:
            # アカウント名を取得
            acname = driver.find_element_by_tag_name("h1").text
            # 最新の投稿をクリック
            driver.find_element_by_css_selector(
                "article>div:nth-of-type(1)>div:nth-of-type(1)>div:nth-of-type(1)>div:nth-of-type(1)").click()
            time.sleep(1)
        except:
            save_screen(driver, 'accounterror')
            save_html(driver, 'accounterror')
        else:
            try:
                # リロード
                driver.refresh()
                postdata = driver.find_element_by_xpath(
                    "/html/body/div[1]/section/main/div/div/article/div[3]/div[2]/a/time").get_attribute('title')
                time.sleep(2)
            except:
                save_screen(driver, 'postdateerror')
                save_html(driver, 'postdateerror')
    finally:
        return [acname, postdata]


def main():
    result_l = []
    # CSV読み込み
    login = read_csv("logininfo.csv")
    target_list = read_csv("target.csv")

    # driverを起動
    if os.name == 'nt':  # Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix':  # Mac
        driver = set_driver("chromedriver", False)

    # ページにアクセス
    try:
        # ログイン処理
        login_action(driver, login["ログインID"], login["パスワード"])
        time.sleep(3)
        # ポップアップを閉じる
        driver.execute_script(
            'document.querySelector("#react-root > section > main > div > div > div > div > button").click()')
        time.sleep(2)
    except:
        # エラーを出力
        save_screen(driver, 'loginerorr')
        save_html(driver, 'loginerorr')
    else:
        # 投稿日を取得
        for tg in target_list["取得したいアカウントのプロフィールURL"]:
            result = get_latest_date(driver, tg)
            result_l.append([result[0], result[1], tg])
    finally:
        # csv出力
        df = pd.DataFrame(result_l, columns=['アカウント名', '最新投稿日', 'プロフィールURL'])
        df.to_csv("result.csv", encoding="utf-8_sig")
        # ブラウザを開いたまま終了する
        #os.kill(driver.service.process.pid, signal.SIGTERM)


main()
