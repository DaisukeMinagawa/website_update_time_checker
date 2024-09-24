import requests
from bs4 import BeautifulSoup
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def setup_google_sheets():
    """Google Sheetsの設定を行い、スプレッドシートを開く"""
    # ユーザーから認証情報ファイルのパスを取得
    creds_path = input("Google Cloud Platformの認証情報JSONファイルのパスを入力してください: ")

    # ユーザーからスプレッドシートIDを取得
    spreadsheet_id = input("使用するGoogleスプレッドシートのIDを入力してください: ")

    # Google Sheets APIの設定
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # スプレッドシートを開く
    sheet = client.open_by_key(spreadsheet_id).sheet1
    return sheet


def get_website_content(url):
    """指定されたURLからウェブサイトの内容を取得する"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.prettify()


def compare_content(old_content, new_content):
    """2つのHTML内容を比較し、変更箇所を特定する"""
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    changes = []
    for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
        if old_line != new_line:
            changes.append(f"Line {i + 1}: {new_line}")

    return "\n".join(changes)


def main():
    # Google Sheetsの設定
    sheet = setup_google_sheets()

    # ユーザーからURLを取得
    url = input("監視するウェブサイトのURLを入力してください: ")

    # 監視間隔を取得（デフォルトは30分）
    interval = int(input("監視間隔を分単位で入力してください（デフォルト: 30）: ") or 30)

    # 初期コンテンツを取得
    old_content = get_website_content(url)

    print(f"{url} の監視を開始します。{interval}分ごとに確認します。")

    while True:
        # 指定された間隔待機
        time.sleep(interval * 60)

        # 新しいコンテンツを取得
        new_content = get_website_content(url)

        # コンテンツを比較
        if old_content != new_content:
            changes = compare_content(old_content, new_content)

            # 変更時刻を取得
            change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # スプレッドシートに記録
            sheet.append_row([change_time, url, changes])

            # 古いコンテンツを更新
            old_content = new_content

            print(f"変更が検出されました。時刻: {change_time}")
        else:
            print(f"変更はありません。次の確認は {interval} 分後です。")


if __name__ == "__main__":
    main()