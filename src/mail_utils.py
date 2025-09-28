import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

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

def generate_mail_body(subject, all_reports):
    today = datetime.date.today().isoformat()
    body = f"""
    <html>
    <head><meta charset='utf-8'><title>{subject}</title></head>
    <body>
    <h1>{subject}</h1>
    {''.join(all_reports)}
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
