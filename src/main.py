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
import re
from config import USE_CLAUDE, MAIL_TO, SIMPLIFY_HOLD_REPORTS
from stock_loader import load_stock_symbols, categorize_stocks, get_currency_for_symbol
from data_fetcher import fetch_stock_data
from ai_analyzer import analyze_with_claude, analyze_with_gemini
from report_generator import generate_report_html
from mail_utils import send_report_via_mail, get_smtp_config, generate_single_category_mail_body, markdown_to_html, extract_judgment_from_analysis, generate_toc, create_collapsible_section
from report_simplifier import detect_hold_judgment, simplify_hold_report
from preference_loader import generate_preference_prompt

def sanitize_id(text):
    """
    テキストをHTML IDとして使用可能な形式にサニタイズする
    
    Args:
        text: 元のテキスト
    
    Returns:
        str: サニタイズされたID
    """
    # 英数字とハイフン以外を削除し、ハイフンに置換
    sanitized = re.sub(r'[^\w\-]', '-', text)
    # 連続するハイフンを1つにまとめる
    sanitized = re.sub(r'-+', '-', sanitized)
    # 先頭と末尾のハイフンを削除
    sanitized = sanitized.strip('-')
    return sanitized

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
    
    # 投資志向性プロンプトを1回だけ生成（全銘柄で共通利用）
    preference_prompt = generate_preference_prompt()
    
    # 分類別のレポート
    categorized_reports = {
        'holding': [],
        'short_selling': [],
        'considering_buy': [],
        'considering_short_sell': []
    }
    
    # 分類別の銘柄情報（目次用）
    categorized_stock_info = {
        'holding': [],
        'short_selling': [],
        'considering_buy': [],
        'considering_short_sell': []
    }
    
    # 各分類の銘柄を処理
    for category, stock_list in categorized.items():
        for stock_info in stock_list:
            symbol = stock_info['symbol']
            company_name = stock_info.get('name', symbol)  # 企業名がなければ銘柄コードを使用
            data = fetch_stock_data(symbol, stock_info)
            if USE_CLAUDE:
                analysis = analyze_with_claude(data, preference_prompt)
            else:
                analysis = analyze_with_gemini(data, preference_prompt)
            
            # 通貨情報を取得
            currency = get_currency_for_symbol(symbol, stock_info.get('currency'))
            data['currency'] = currency
            
            # レポート生成（stock_dataを渡す）
            html, filename = generate_report_html(symbol, company_name, analysis, data)
            print(f"レポート生成: {filename} (分類: {category})")
            
            # 売買判断を抽出
            judgment = extract_judgment_from_analysis(analysis)
            
            # 銘柄IDを生成（リンク用）
            stock_id = f"stock-{sanitize_id(symbol)}"
            
            # 目次用の銘柄情報を記録
            categorized_stock_info[category].append({
                'symbol': symbol,
                'name': company_name,
                'judgment': judgment,
                'id': stock_id
            })
            
            # メール本文用のHTML生成（簡略化を適用）
            if SIMPLIFY_HOLD_REPORTS and detect_hold_judgment(analysis):
                # ホールド判断の場合は簡略化
                simplified_analysis = simplify_hold_report(symbol, company_name, analysis, data['price'], currency)
                analysis_html = markdown_to_html(simplified_analysis)
            else:
                analysis_html = markdown_to_html(analysis)
            
            # メール本文で企業名を見出しとして使用（IDを追加してリンク可能に）
            # 詳細レポートを折りたたみ可能にする
            report_html = f"""<h1 id="{stock_id}" style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">{company_name}</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: {symbol}</p>
<details>
<summary style="cursor: pointer; font-weight: bold; color: #007bff; padding: 10px 0;">詳細レポートを表示</summary>
<div style="margin-top: 15px; padding-left: 20px; border-left: 3px solid #007bff;">
{analysis_html}
</div>
</details>"""
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
            stock_info_list = categorized_stock_info.get(category, [])
            if reports:  # 銘柄が存在する場合のみメール送信
                category_name = category_names[category]
                subject = f"株式日次レポート - {category_name} ({today})"
                
                # 目次を生成
                toc_html = generate_toc(stock_info_list)
                
                # メール本文を生成（目次を含む）
                body = generate_single_category_mail_body(subject, reports, toc_html)
                send_report_via_mail(
                    subject, body, MAIL_TO,
                    smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
                )
                print(f"メール送信完了: {category_name}")

