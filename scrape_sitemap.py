import csv
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# 設定項目
START_URL = "https://www.musashino-u.ac.jp/"  # トップページURL
DOMAIN = urlparse(START_URL).netloc  # 同一ドメイン指定
INTERVAL = 1.0  # 1回のアクセスごとの待機時間（秒）
OUTPUT_CSV = "sitemap.csv"  # 出力するCSVファイル名

# 結果を格納する辞書型変数 (key: URL, value: <title>の内容)
sitemap = {}

# 訪問済みURLを記録するセット
visited = set()

# HTTPヘッダー設定
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def crawl(url):
    """指定されたURLとその配下の同一ドメインリンクを再帰的に巡回する関数"""
    if url in visited:
        return

    visited.add(url)
    print(f"Crawling ({len(sitemap)} pages found): {url}")

    try:
        # サーバー負荷軽減のための待機時間
        time.sleep(INTERVAL)

        response = requests.get(url, headers=HEADERS, timeout=10)

        # HTML以外のファイル（PDFや画像等）は除外
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # <title>タグの文字列を取得
        title_tag = soup.find("title")
        title_text = (
            title_tag.get_text(strip=True) if title_tag else "No Title"
        )

        # 辞書型変数に格納
        sitemap[url] = title_text

        # ページ内のすべての <a> タグからリンクを取得して再帰巡回
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href).split("#")[0]  # アンカー除去

            parsed_url = urlparse(full_url)
            if (
                parsed_url.netloc == DOMAIN
                and parsed_url.scheme in ["http", "https"]
                and full_url not in visited
            ):
                crawl(full_url)

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")


def save_to_csv(dictionary, filename):
    """辞書データをCSVファイルに書き出す関数"""
    with open(filename, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        # ヘッダー行の書き込み
        writer.writerow(["URL", "Title"])
        # データの書き込み
        for url, title in dictionary.items():
            writer.writerow([url, title])


if __name__ == "__main__":
    print("--- 巡回を開始します ---")
    crawl(START_URL)

    print(f"\n--- 処理完了: 計 {len(sitemap)} 件のページを抽出し出しました ---")

    # CSVファイルへ保存
    save_to_csv(sitemap, OUTPUT_CSV)
    print(f"CSVファイルを保存しました: {OUTPUT_CSV}")