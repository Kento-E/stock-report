"""
mail.bodyモジュールのテスト
"""

import os
import sys

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from mails.body import generate_single_category_mail_body


class TestGenerateSingleCategoryMailBody:
    """generate_single_category_mail_body関数のテスト"""

    def test_single_category_mail(self):
        """単一カテゴリーのメール生成"""
        subject = "テスト件名"
        reports = ["<h1>銘柄1</h1><p>分析1</p>", "<h1>銘柄2</h1><p>分析2</p>"]

        body = generate_single_category_mail_body(subject, reports)

        assert "<html>" in body
        assert "</html>" in body
        assert subject in body
        assert "銘柄1" in body
        assert "銘柄2" in body

    def test_single_category_empty_reports(self):
        """レポートが空でもエラーが発生しない"""
        subject = "テスト件名"
        reports = []

        body = generate_single_category_mail_body(subject, reports)

        assert "<html>" in body

    def test_single_category_no_category_heading_in_body(self):
        """本文にカテゴリー見出しが表示されないことを確認"""
        subject = "株式日次レポート - 保有銘柄"
        reports = ["<h1>トヨタ自動車</h1><p>分析内容</p>"]

        body = generate_single_category_mail_body(subject, reports)

        # タイトルタグにはカテゴリー名が含まれる
        assert f"<title>{subject}</title>" in body
        # bodyタグ内の最初の見出しは銘柄名であり、カテゴリー名ではない
        body_start = body.find("<body")
        body_end = body.find("</body>")
        if body_start != -1 and body_end != -1:
            body_content = body[body_start:body_end]
            # 最初のh1は銘柄名
            assert "<h1>トヨタ自動車</h1>" in body_content

    def test_single_category_with_toc(self):
        """目次付きメール本文の生成"""
        subject = "テスト件名"
        reports = ['<h1 id="stock-TEST">テスト銘柄</h1><p>分析内容</p>']
        toc = "<div>目次HTML</div>"

        body = generate_single_category_mail_body(subject, reports, toc)

        assert "<html>" in body
        assert "目次HTML" in body
        assert "テスト銘柄" in body

    def test_single_category_without_toc(self):
        """目次なしメール本文の生成（後方互換性）"""
        subject = "テスト件名"
        reports = ["<h1>テスト銘柄</h1><p>分析内容</p>"]

        body = generate_single_category_mail_body(subject, reports)

        assert "<html>" in body
        assert "テスト銘柄" in body
