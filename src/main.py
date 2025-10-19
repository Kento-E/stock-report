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
6. IPO銘柄の処理（ipo_loader）
"""

import sys
import datetime
import yaml
from config import USE_CLAUDE, MAIL_TO
from stock_loader import load_stock_symbols, categorize_stocks, get_currency_for_symbol
from ipo_loader import load_ipo_stocks, filter_upcoming_ipos
from data_fetcher import fetch_stock_data
from ai_analyzer import analyze_with_claude, analyze_with_gemini
from report_generator import generate_report_html
from mail_utils import send_report_via_mail, get_smtp_config, generate_single_category_mail_body, markdown_to_html

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
        'considering_buy': [],
        'considering_short_sell': []
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

    # 分類別に個別のメールを送信
    smtp_conf = get_smtp_config()
    if MAIL_TO and all(smtp_conf.values()):
        today = datetime.date.today().isoformat()
        
        # カテゴリー名の定義
        category_names = {
            'holding': '保有銘柄',
            'short_selling': '空売り銘柄',
            'considering_buy': '購入検討中の銘柄',
            'considering_short_sell': '空売り検討中の銘柄'
        }
        
        # 各カテゴリーごとに個別のメールを送信
        for category in ['holding', 'short_selling', 'considering_buy', 'considering_short_sell']:
            reports = categorized_reports.get(category, [])
            if reports:  # 銘柄が存在する場合のみメール送信
                category_name = category_names[category]
                subject = f"株式日次レポート - {category_name} ({today})"
                body = generate_single_category_mail_body(subject, category_name, reports)
                send_report_via_mail(
                    subject, body, MAIL_TO,
                    smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
                )
                print(f"メール送信完了: {category_name}")
    
    # 上場予定銘柄の処理
    print("\n=== 上場予定銘柄のレポート処理 ===")
    try:
        ipo_stocks = load_ipo_stocks()
        if not ipo_stocks:
            print("上場予定銘柄はありません。")
        else:
            # 近日中（7日以内）に上場予定の銘柄をフィルタリング
            upcoming_ipos = filter_upcoming_ipos(ipo_stocks, days_ahead=7)
            if not upcoming_ipos:
                print(f"7日以内に上場予定の銘柄はありません（登録銘柄数: {len(ipo_stocks)}）")
            else:
                print(f"7日以内に上場予定の銘柄: {[s['name'] for s in upcoming_ipos]}")
                
                ipo_reports = []
                for ipo_stock in upcoming_ipos:
                    symbol = ipo_stock['symbol']
                    name = ipo_stock['name']
                    
                    # IPO銘柄用のプロンプトデータを作成
                    ipo_date = ipo_stock.get('ipo_date', '未定')
                    market = ipo_stock.get('market', '未定')
                    expected_price = ipo_stock.get('expected_price')
                    currency = get_currency_for_symbol(symbol, ipo_stock.get('currency'))
                    note = ipo_stock.get('note', '')
                    
                    # IPO銘柄は株価データを取得せず、公開情報のみで分析
                    ipo_data = {
                        'symbol': symbol,
                        'name': name,
                        'price': None,
                        'news': [f"上場予定日: {ipo_date}", f"上場市場: {market}"],
                        'currency': currency,
                        'ipo_date': ipo_date,
                        'market': market,
                        'expected_price': expected_price,
                        'note': note
                    }
                    
                    # 想定価格が設定されている場合はニュースに追加
                    if expected_price:
                        ipo_data['news'].append(f"想定価格: {expected_price}{currency}")
                    if note:
                        ipo_data['news'].append(f"備考: {note}")
                    
                    # AI分析（IPO専用のプロンプトを使用）
                    if USE_CLAUDE:
                        analysis = analyze_with_claude(ipo_data, is_ipo=True)
                    else:
                        analysis = analyze_with_gemini(ipo_data, is_ipo=True)
                    
                    # レポート生成
                    html, filename = generate_report_html(symbol, name, analysis, is_ipo=True)
                    print(f"IPOレポート生成: {filename}")
                    
                    # メール本文用HTML
                    analysis_html = markdown_to_html(analysis)
                    report_html = f"<h3>{name} ({symbol})</h3>\n<p style=\"color: #666; font-size: 14px;\">上場予定日: {ipo_date}</p>\n{analysis_html}"
                    ipo_reports.append(report_html)
                
                # IPO銘柄専用のメールを送信
                if ipo_reports and MAIL_TO and all(smtp_conf.values()):
                    today = datetime.date.today().isoformat()
                    subject = f"上場予定銘柄レポート ({today})"
                    body = generate_single_category_mail_body(subject, "上場予定銘柄（7日以内）", ipo_reports)
                    send_report_via_mail(
                        subject, body, MAIL_TO,
                        smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
                    )
                    print(f"メール送信完了: 上場予定銘柄レポート")
    except Exception as e:
        print(f"上場予定銘柄の処理中にエラーが発生しました: {e}")
        # IPOレポートの失敗は全体の処理を止めない

