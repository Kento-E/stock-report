import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import os
import datetime
import markdown
import re
import html

def get_smtp_config():
    """
    環境変数からSMTP設定を取得
    """
    return {
        'MAIL_FROM': os.getenv('MAIL_FROM'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASS': os.getenv('SMTP_PASS'),
    }

def markdown_to_html(markdown_text):
    """
    マークダウンテキストをHTMLに変換
    """
    return markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])

def create_collapsible_section(content, title="詳細レポート", collapsed=True):
    """
    レポートセクションを生成する。
    
    注意: メールクライアントの制限により、コンテンツは常に表示されます。
    
    Args:
        content: 表示対象のHTMLコンテンツ
        title: セクションのタイトル
        collapsed: 未使用（後方互換性のため保持）
    
    Returns:
        HTMLセクション
    """
    html = f"""
<div style="margin-top: 15px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">
    <h3 style="margin: 0 0 10px 0; color: #007bff; font-size: 16px;">{title}</h3>
    <div style="padding-left: 10px;">
{content}
    </div>
</div>
"""
    return html

def extract_judgment_from_analysis(analysis_text):
    """
    AI分析結果から売買判断を抽出する
    
    AIプロンプトで構造化された出力を要求しているため、シンプルなパターンマッチで対応。
    フォールバックとして複雑なパターンも保持。
    
    Args:
        analysis_text: AI分析結果のテキスト（マークダウン形式）
    
    Returns:
        str: 抽出された売買判断（見つからない場合は「-」）
    """
    if not analysis_text:
        return "-"
    
    # 基本パターン: AIに要求している「売買判断: 買い」形式を最優先
    # [：:\s] は全角コロン（：）、半角コロン（:）、空白文字をマッチ
    simple_patterns = [
        r'(?:売買判断|判断)[：:\s]+([^\n。、\.,、（(を]+)',  # 「売買判断: 買い」（区切り文字まで）
        r'(?:judgment|action)[：:\s]+([^\n\s。、\.,]+)',  # 英語版
    ]
    
    for pattern in simple_patterns:
        match = re.search(pattern, analysis_text, re.IGNORECASE)
        if match:
            judgment = match.group(1).strip()
            # マークダウン記号を削除
            judgment = re.sub(r'[*#]', '', judgment).strip()
            
            if judgment and len(judgment) <= 10:  # 短い判断のみ受け入れ
                return judgment
    
    # フォールバック: 複雑なパターン（AIが指示に従わなかった場合）
    fallback_patterns = [
        r'(?:推奨|アクション)[：:\s]+([^\n]+)',
        r'##?\s*(?:売買判断|判断)[：:\s]+([^\n]+)',
        r'\*\*(?:売買判断|判断|推奨|アクション)\*\*[：:\s]+([^\n]+)',
    ]
    
    for pattern in fallback_patterns:
        match = re.search(pattern, analysis_text, re.IGNORECASE)
        if match:
            judgment = match.group(1).strip()
            # クリーンアップ処理
            judgment = re.sub(r'[*#]', '', judgment).strip()
            judgment = re.sub(r'^[：:\s]+', '', judgment)
            judgment = re.sub(r'^(売買判断|判断|推奨|アクション)[：:\s]*', '', judgment)
            judgment = re.split(r'[。、\.,]', judgment)[0].strip()
            # 動詞・助詞を除去
            judgment = re.split(r'[をがはに](推奨|提供|維持|継続)', judgment)[0].strip()
            judgment = re.split(r'が(良い|おすすめ|望ましい)', judgment)[0].strip()
            judgment = re.split(r'[（(]', judgment)[0].strip()
            
            if judgment and len(judgment) > 0:
                return judgment[:30]
    
    # 最終フォールバック: キーワードを含む行を探す
    lines = analysis_text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in ['買い', 'buy', '売り', 'sell', 'ホールド', 'hold', '様子見']):
            clean_line = re.sub(r'[*#:\-]', '', line).strip()
            if 5 < len(clean_line) <= 30:
                clean_line = re.split(r'[をがはに](推奨|提供|維持|継続)', clean_line)[0].strip()
                clean_line = re.split(r'が(良い|おすすめ|望ましい)', clean_line)[0].strip()
                clean_line = re.split(r'[（(。、]', clean_line)[0].strip()
                if len(clean_line) <= 10:
                    return clean_line
    
    return "-"

def generate_toc(stock_reports_info):
    """
    銘柄レポートの目次（TOC）をHTML形式で生成する
    
    Args:
        stock_reports_info: 銘柄レポート情報のリスト
            [{'symbol': '7203.T', 'name': 'トヨタ自動車', 'judgment': '買い', 'id': 'stock-7203-T'}, ...]
    
    Returns:
        str: HTML形式の目次
    """
    if not stock_reports_info:
        return ""
    
    toc_html = """
    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin-bottom: 30px;">
        <h2 style="color: #333; margin-top: 0; font-size: 20px;">📊 銘柄一覧</h2>
        <table style="width: 100%; border-collapse: collapse; background-color: white;">
            <thead>
                <tr style="background-color: #007bff; color: white;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">銘柄名</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">銘柄コード</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">売買判断</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for i, info in enumerate(stock_reports_info):
        # HTMLエスケープを適用してXSS対策
        escaped_name = html.escape(info['name'])
        escaped_symbol = html.escape(info['symbol'])
        escaped_judgment = html.escape(info['judgment'])
        
        # 行の背景色を交互に変更
        bg_color = "#f8f9fa" if i % 2 == 0 else "white"
        toc_html += f"""
                <tr style="background-color: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold; color: #333;">
                        {escaped_name}
                    </td>
                    <td style="padding: 10px; border: 1px solid #dee2e6; color: #666;">
                        {escaped_symbol}
                    </td>
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">
                        {escaped_judgment}
                    </td>
                </tr>
"""
    
    toc_html += """
            </tbody>
        </table>
    </div>
"""
    
    return toc_html

def generate_mail_body(subject, all_reports):
    today = datetime.date.today().isoformat()
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body>
    {''.join(all_reports)}
    </body>
    </html>
    """
    return body


def generate_single_category_mail_body(subject, reports, toc_html=""):
    """
    単一カテゴリーのレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        reports: レポートのリスト
        toc_html: 目次のHTML（省略可能）
    
    Returns:
        HTML形式のメール本文
    """
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
    {toc_html}
    {''.join(reports)}
    </body>
    </html>
    """
    return body


def generate_categorized_mail_body(subject, categorized_reports, toc_html=""):
    """
    分類別のレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        categorized_reports: 分類別のレポート辞書
            {'holding': [...], 'short_selling': [...], 'considering_buy': [...], 'considering_short_sell': [...]}
        toc_html: 目次のHTML（省略可能）
    
    Returns:
        HTML形式のメール本文
    """
    category_names = {
        'holding': '保有銘柄',
        'short_selling': '空売り銘柄',
        'considering_buy': '購入検討中の銘柄',
        'considering_short_sell': '空売り検討中の銘柄'
    }
    
    sections = []
    
    # 各分類のセクションを生成
    for category in ['holding', 'short_selling', 'considering_buy', 'considering_short_sell']:
        reports = categorized_reports.get(category, [])
        if reports:
            section_title = category_names[category]
            section_html = f'<h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 30px;">{section_title}</h2>\n'
            section_html += ''.join(reports)
            sections.append(section_html)
    
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
    {toc_html}
    {''.join(sections)}
    </body>
    </html>
    """
    return body

def send_report_via_mail(subject, html_body, to_addrs, mail_from, smtp_server, smtp_port, smtp_user, smtp_pass):
    """
    to_addrs: カンマまたはセミコロン区切りの文字列、またはリスト
    その他の引数は全てmain.pyから渡す
    """
    if isinstance(to_addrs, str):
        to_list = [addr.strip() for addr in to_addrs.replace(';', ',').split(',') if addr.strip()]
    else:
        to_list = list(to_addrs)
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = mail_from  # 送信者自身をToに
    msg["Bcc"] = ", ".join(to_list)
    msg["Date"] = formatdate(localtime=True)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(mail_from, to_list, msg.as_string())
        print(f"メール送信成功: {to_list}")
    except Exception as e:
        print(f"メール送信失敗: {e}")
