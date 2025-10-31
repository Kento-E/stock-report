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
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import USE_CLAUDE, MAIL_TO, SIMPLIFY_HOLD_REPORTS
from loaders import load_stock_symbols, categorize_stocks, get_currency_for_symbol
from analyzers import fetch_stock_data, analyze_with_claude, analyze_with_gemini
from reports import detect_hold_judgment, simplify_hold_report
from mails import send_report_via_mail, get_smtp_config, generate_single_category_mail_body
from mails.formatter import markdown_to_html
from mails.toc import extract_judgment_from_analysis, generate_toc
from loaders import generate_preference_prompt

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
    
    def process_single_stock(category, stock_info):
        """単一の銘柄を処理する関数（並列処理用）"""
        try:
            symbol = stock_info['symbol']
            company_name = stock_info.get('name', symbol)
            data = fetch_stock_data(symbol, stock_info)
            if USE_CLAUDE:
                analysis = analyze_with_claude(data, preference_prompt)
            else:
                analysis = analyze_with_gemini(data, preference_prompt)
            
            # 通貨情報を取得
            currency = get_currency_for_symbol(symbol, stock_info.get('currency'))
            data['currency'] = currency
            
            # 売買判断を抽出
            judgment = extract_judgment_from_analysis(analysis)
            
            # 目次用の銘柄情報
            stock_info_data = {
                'symbol': symbol,
                'name': company_name,
                'judgment': judgment
            }
            
            # メール本文用のHTML生成（簡略化を適用）
            if SIMPLIFY_HOLD_REPORTS and detect_hold_judgment(analysis):
                # ホールド判断の場合は簡略化
                simplified_analysis = simplify_hold_report(symbol, company_name, analysis, data['price'], currency)
                analysis_html = markdown_to_html(simplified_analysis)
            else:
                analysis_html = markdown_to_html(analysis)
            
            print(f"レポート生成完了: {symbol} (分類: {category})")
            
            # メール本文で企業名と銘柄コードを1つの見出しとして使用
            report_html = f"""<h1 style="margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #ddd;">{company_name}（{symbol}）</h1>
<div style="margin-top: 15px; padding-left: 20px; border-left: 3px solid #007bff;">
{analysis_html}
</div>"""
            
            return category, report_html, stock_info_data
        except Exception as e:
            print(f"エラー: {stock_info['symbol']}の処理中に問題が発生しました: {e}")
            return None
    
    # 並列処理で各銘柄を処理（最大10スレッド）
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 全銘柄の処理タスクを作成
        futures = []
        for category, stock_list in categorized.items():
            for stock_info in stock_list:
                future = executor.submit(process_single_stock, category, stock_info)
                futures.append(future)
        
        # 処理結果を収集
        for future in as_completed(futures):
            result = future.result()
            if result:
                category, report_html, stock_info_data = result
                categorized_reports[category].append(report_html)
                categorized_stock_info[category].append(stock_info_data)

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

