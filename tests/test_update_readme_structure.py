"""
scripts/update_readme_structure.py のテスト
"""
import pytest
import sys
from pathlib import Path

# スクリプトのディレクトリをパスに追加
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

import update_readme_structure


class TestGenerateFileStructure:
    """generate_file_structure関数のテスト"""
    
    def test_generate_file_structure_returns_string(self):
        """ファイル構造が文字列として生成されることを確認"""
        result = update_readme_structure.generate_file_structure()
        assert isinstance(result, str)
        assert "src/" in result
        assert "```" in result
    
    def test_generate_file_structure_includes_main_py_at_end(self):
        """main.pyが最後に配置されることを確認"""
        result = update_readme_structure.generate_file_structure()
        lines = result.split("\n")
        # 最後のファイル行を取得（```の前）
        file_lines = [line for line in lines if line.startswith("├──") or line.startswith("└──")]
        if file_lines:
            last_line = file_lines[-1]
            assert "main.py" in last_line
            assert "└──" in last_line  # 最後のファイルは└──を使用
    
    def test_generate_file_structure_includes_all_py_files(self):
        """すべての.pyファイルが含まれることを確認"""
        src_dir = Path("src")
        actual_py_files = sorted([f.name for f in src_dir.glob("*.py") if f.is_file()])
        
        result = update_readme_structure.generate_file_structure()
        
        for py_file in actual_py_files:
            assert py_file in result, f"{py_file} がファイル構造に含まれていません"
    
    def test_generate_file_structure_has_proper_format(self):
        """生成されたファイル構造が正しいフォーマットを持つことを確認"""
        result = update_readme_structure.generate_file_structure()
        lines = result.split("\n")
        
        # コードブロックで囲まれていることを確認
        assert lines[0] == "```"
        assert lines[-1] == "```"
        
        # src/ から始まることを確認
        assert lines[1] == "src/"
        
        # ツリー構造の記号が含まれることを確認
        tree_symbols_found = any("├──" in line or "└──" in line for line in lines)
        assert tree_symbols_found


class TestUpdateReadme:
    """update_readme関数のテスト"""
    
    def test_update_readme_detects_no_change(self):
        """変更がない場合にFalseを返すことを確認"""
        # 現在の構造を生成
        current_structure = update_readme_structure.generate_file_structure()
        
        # 同じ構造で更新を試みる
        result = update_readme_structure.update_readme(current_structure)
        
        # 変更がないのでFalseが返されるはず
        assert result is False
    
    def test_readme_file_exists(self):
        """README.mdファイルが存在することを確認"""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md ファイルが見つかりません"
    
    def test_readme_contains_structure_section(self):
        """README.mdにファイル構造セクションが存在することを確認"""
        readme_path = Path("README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # src/を含むコードブロックが存在することを確認
        import re
        pattern = r"```\nsrc/\n(?:.*\n)*?```"
        match = re.search(pattern, content)
        
        assert match is not None, "README.mdにファイル構造セクションが見つかりません"
