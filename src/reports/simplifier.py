"""
レポート簡略化モジュール

売買判断がホールドの場合に、レポートを簡略化する機能を提供します。
"""

import re


def detect_hold_judgment(analysis_text):
    """
    AI分析結果から「ホールド」判断かどうかを検出する。
    
    Args:
        analysis_text: AI分析結果のテキスト
    
    Returns:
        bool: ホールド判断の場合True、それ以外はFalse
    """
    if not analysis_text:
        return False
    
    # 判断キーワードを含む行を検索
    judgment_keywords = [
        'ホールド',
        'hold',
        '保有継続',
        '様子見',
        '現状維持',
        '維持'  # 空売りポジションの維持判断
    ]
    
    # テキストを小文字に変換して検索（英語対応）
    text_lower = analysis_text.lower()
    
    # ホールド関連キーワードが含まれているかチェック
    for keyword in judgment_keywords:
        if keyword.lower() in text_lower:
            # 「売買判断」「判断」「推奨」「アクション」などのセクション付近にキーワードがあるか確認
            # より正確な判定のため、売買判断の文脈でキーワードを探す
            patterns = [
                r'(売買判断|判断|推奨|アクション)[：:\s]*([^\n]*' + re.escape(keyword) + r'[^\n]*)',
                r'(judgment|recommendation|action)[：:\s]*([^\n]*' + re.escape(keyword) + r'[^\n]*)',
            ]
            for pattern in patterns:
                if re.search(pattern, analysis_text, re.IGNORECASE):
                    return True
    
    return False


def simplify_hold_report(symbol, name, analysis_text, current_price, currency):
    """
    ホールド判断または維持判断の場合に簡略化されたレポートを生成する。
    
    Args:
        symbol: 銘柄コード
        name: 企業名
        analysis_text: AI分析結果のテキスト
        current_price: 現在の株価
        currency: 通貨単位
    
    Returns:
        str: 簡略化されたレポートテキスト（マークダウン形式）
    """
    # 理由の抽出（売買判断セクションから）
    reason = _extract_hold_reason(analysis_text)
    
    # 「維持」判断（空売りポジション）かどうかを判定
    text_lower = analysis_text.lower()
    is_maintain_judgment = False
    maintain_pattern = r'(?:売買判断|判断)[：:\s]*維持'
    if re.search(maintain_pattern, analysis_text, re.IGNORECASE):
        is_maintain_judgment = True
    
    # 判断のラベルを決定
    judgment_label = "維持" if is_maintain_judgment else "ホールド"
    
    simplified = f"""## 売買判断: {judgment_label}

**現在の株価**: {current_price}{currency}

{reason}

---
*詳細な分析レポートが必要な場合は、環境変数 `SIMPLIFY_HOLD_REPORTS=false` を設定してください。*
"""
    
    return simplified


def _extract_hold_reason(analysis_text):
    """
    分析テキストからホールド判断の理由を抽出する。
    
    Args:
        analysis_text: AI分析結果のテキスト
    
    Returns:
        str: ホールド判断の理由
    """
    if not analysis_text:
        return "現状の保有状況を維持することを推奨します。"
    
    # 「売買判断」や「理由」のセクションを探す
    patterns = [
        # 理由セクションを探す（日本語）
        r'理由[：:\s]*([^\n]+)',
        # 売買判断の後の説明を探す
        r'(?:売買判断|判断|推奨)[：:\s]*(?:ホールド|hold|保有継続|様子見|現状維持|維持)[^\n]*[\n\s]*([^\n]+)',
        # 英語の理由セクション
        r'reason[：:\s]*([^\n]+)',
        # 英語の判断セクション
        r'(?:judgment|recommendation)[：:\s]*(?:hold)[^\n]*[\n\s]*([^\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis_text, re.IGNORECASE | re.DOTALL)
        if match:
            reason = match.group(1).strip()
            # 長すぎる場合は最初の文のみ抽出
            sentences = re.split(r'[。\.]', reason)
            if sentences and sentences[0] and len(sentences[0]) > 5:
                result = sentences[0].strip()
                if not result.endswith('。') and not result.endswith('.'):
                    result += '。'
                return result
    
    # 理由が見つからない場合、キーワードを含む行を探す
    lines = analysis_text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in ['ホールド', 'hold', '保有継続', '様子見', '現状維持', '維持']):
            # その行またはその次の行から理由を抽出
            for offset in range(0, min(3, len(lines) - i)):
                candidate_line = lines[i + offset].strip()
                if candidate_line and not candidate_line.startswith('#') and len(candidate_line) > 10:
                    # 最初の文を抽出
                    sentences = re.split(r'[。\.]', candidate_line)
                    if sentences and sentences[0]:
                        result = sentences[0].strip()
                        if not result.endswith('。') and not result.endswith('.'):
                            result += '。'
                        return result
    
    return "現状の保有状況を維持することを推奨します。"
