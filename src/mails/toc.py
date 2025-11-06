"""
目次（TOC）生成モジュール

AI分析結果から売買判断を抽出し、銘柄一覧の目次をHTML形式で生成します。
"""

import re
import html


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
            [{'symbol': '7203.T', 'name': 'トヨタ自動車', 'judgment': '買い'}, ...]
    
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
        
        # 売買判断に応じたスタイルを設定
        # 「売り」の場合は赤字、「ホールド」の場合は太字にしない
        judgment_style = "padding: 10px; border: 1px solid #dee2e6;"
        if '売り' in info['judgment']:
            # 売り判断は赤字で表示
            judgment_style += " font-weight: bold; color: #dc3545;"
        elif 'ホールド' in info['judgment']:
            # ホールド判断は太字にしない
            judgment_style += " color: #666;"
        else:
            # その他の判断（買い、買い増し、様子見など）は太字で表示
            judgment_style += " font-weight: bold;"
        
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
                    <td style="{judgment_style}">
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
