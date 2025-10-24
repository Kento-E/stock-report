import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import os
import datetime
import markdown

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


def generate_single_category_mail_body(subject, category_name, reports):
    """
    単一カテゴリーのレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        category_name: カテゴリー名（日本語）
        reports: レポートのリスト
    
    Returns:
        HTML形式のメール本文
    """
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #333; border-bottom: 3px solid #007bff; padding-bottom: 15px;">{category_name}</h2>
    {''.join(reports)}
    </body>
    </html>
    """
    return body


def generate_categorized_mail_body(subject, categorized_reports):
    """
    分類別のレポートからHTMLメール本文を生成する。
    
    Args:
        subject: メール件名
        categorized_reports: 分類別のレポート辞書
            {'holding': [...], 'short_selling': [...], 'considering_buy': [...], 'considering_short_sell': [...]}
    
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
