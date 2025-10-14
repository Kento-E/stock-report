"""
株式レポートシステム - メインエントリーポイント

Github Actions上で定期実行可能。APIキーや設定値はSecrets/環境変数で管理。
レポートはHTML形式で生成し、メール配信処理の雛形も含む。

主な処理フロー：
1. 銘柄リストの読み込み（stock_loader）
2. データ収集（data_fetcher）
3. AI分析（ai_analyzer）
4. レポート生成（report_generator）
5. メール配信（mail_utils）
"""

import sys
import datetime
import yaml
from config import USE_CLAUDE, MAIL_TO
from stock_loader import load_stock_symbols, categorize_stocks
from data_fetcher import fetch_stock_data
from ai_analyzer import analyze_with_claude, analyze_with_gemini
from report_generator import generate_report_html
from mail_utils import send_report_via_mail, get_smtp_config, generate_categorized_mail_body, markdown_to_html

if __name__ == "__main__":
    try:
        # 対象銘柄リスト（data/stocks.yamlから読み込み）
        stocks = load_stock_symbols()
        print(f"分析対象銘柄: {[s['symbol'] for s in stocks]}")
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        print(f"\n{str(e)}")
        print("\n処理を終了します。")
        sys.exit(1)
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        print("\n処理を終了します。")
        sys.exit(1)
    
    # 銘柄を分類
    categorized = categorize_stocks(stocks)
    
    # 分類別のレポート
    categorized_reports = {
        'holding': [],
        'short_selling': [],
        'considering_buy': []
    }
    
    # 各分類の銘柄を処理
    for category, stock_list in categorized.items():
        for stock_info in stock_list:
            symbol = stock_info['symbol']
            name = stock_info.get('name', symbol)  # 企業名がなければ銘柄コードを使用
            data = fetch_stock_data(symbol, stock_info)
            if USE_CLAUDE:
                analysis = analyze_with_claude(data)
            else:
                analysis = analyze_with_gemini(data)
            html, filename = generate_report_html(symbol, name, analysis)
            print(f"レポート生成: {filename} (分類: {category})")
            analysis_html = markdown_to_html(analysis)
            # メール本文でも企業名を見出しに使用
            report_html = f"<h3>{name}</h3>\n<p style=\"color: #666; font-size: 14px;\">銘柄コード: {symbol}</p>\n{analysis_html}"
            categorized_reports[category].append(report_html)

    # 全銘柄分まとめてメール送信
    smtp_conf = get_smtp_config()
    if MAIL_TO and all(smtp_conf.values()):
        today = datetime.date.today().isoformat()
        subject = f"株式日次レポート ({today})"
        body = generate_categorized_mail_body(subject, categorized_reports)
        send_report_via_mail(
            subject, body, MAIL_TO,
            smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
        )
