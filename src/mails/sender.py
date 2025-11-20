"""
メール送信モジュール

SMTPを使用してHTMLメールを送信します。
複数の宛先に対応し、BCCで送信することでプライバシーを保護します。
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


def send_report_via_mail(
    subject, html_body, to_addrs, mail_from, smtp_server, smtp_port, smtp_user, smtp_pass
):
    """
    HTMLメールを送信する

    Args:
        subject: メール件名
        html_body: HTML形式のメール本文
        to_addrs: 宛先アドレス（カンマまたはセミコロン区切りの文字列、またはリスト）
        mail_from: 送信元メールアドレス
        smtp_server: SMTPサーバーアドレス
        smtp_port: SMTPポート番号
        smtp_user: SMTP認証ユーザー名
        smtp_pass: SMTP認証パスワード

    Raises:
        Exception: メール送信に失敗した場合
    """
    # 宛先アドレスをリストに変換
    if isinstance(to_addrs, str):
        to_list = [addr.strip() for addr in to_addrs.replace(";", ",").split(",") if addr.strip()]
    else:
        to_list = list(to_addrs)

    # メッセージを作成
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = mail_from  # 送信者自身をToに
    msg["Bcc"] = ", ".join(to_list)  # 受信者はBCCに
    msg["Date"] = formatdate(localtime=True)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(mail_from, to_list, msg.as_string())
        print(f"メール送信成功: {to_list}")
    except Exception as e:
        print(f"メール送信失敗: {e}")
        raise
