import os
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
import time
import datetime
import random
import logging
import traceback
import sys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from getenc import getEncode
from bs4 import BeautifulSoup
import re
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
    fname = "error/"+fname + str(int(time.time()))+".png"
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
    # ID,PASSの入力
    time.sleep(1)
    logid_area = driver.find_element_by_name('username')
    logpass_area = driver.find_element_by_name('password')
    input_text_slowly(logid_area, userid, 0.2, 0.5)
    input_text_slowly(logpass_area, password, 0.2, 0.5)
    # ログインボタンクリック
    time.sleep(1)
    driver.find_element_by_xpath(
        '/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[3]/button').click()
    time.sleep(3)


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

    # 投稿日を取得
    for tg in target_list["日時を取得したいアカウントid"]:
        url = "https://www.instagram.com/"+tg
        driver.get(url)
        time.sleep(1)
        # ログイン画面だったらログイン
        if driver.current_url == "https://www.instagram.com/accounts/login/":
            login_action(driver, login["ログインID"], login["パスワード"])
            if driver.current_url == "https://www.instagram.com/accounts/login/":
                save_screen(driver, 'loginerorr')
                save_html(driver, 'loginerorr')
                break
            driver.get("https://www.instagram.com/" + tg)
            time.sleep(2)
        source = driver.page_source
        soup = BeautifulSoup(source, 'lxml')
        #print(soup.select('body > script')[0].string)
        # 最新の投稿日
        unixt = re.search(r'(taken_at_timestamp)\D+\d+',
                          soup.select('body > script')[0].string)
        try:
            # 最新の投稿日
            latest_time = datetime.datetime.fromtimestamp(
                int(unixt.group()[-10:]))
        except:
            latest_time = "取得できませんでした"
            save_screen(driver, 'postdateerror')
            save_html(driver, 'postdateerror')
        finally:
            result_l.append([tg, latest_time, url])
    # csv出力
    df = pd.DataFrame(result_l, columns=['アカウントId', '最新投稿日', 'プロフィールURL'])
    try:
        df.to_csv("result.csv", encoding="utf-8_sig")
    except Exception as e:
        print(e + "csv書き込み時にエラーが発生しました")


main()
