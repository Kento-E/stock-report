"""
AI分析モジュール

Claude SonnetまたはGemini APIを使用して株価・ニュースデータを分析します。
"""

import anthropic
import requests
from config import CLAUDE_API_KEY, GEMINI_API_KEY
from stock_loader import get_currency_for_symbol, calculate_tax


def analyze_with_claude(data, is_ipo=False):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    
    Args:
        data: 株価データと保有情報を含む辞書
        is_ipo: IPO銘柄の場合True（デフォルト: False）
    
    Returns:
        分析結果のテキスト
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        error_msg = "Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    currency = get_currency_for_symbol(data['symbol'], data.get('currency'))
    
    # IPO銘柄用のプロンプト
    if is_ipo:
        prompt = _generate_ipo_prompt(data, currency)
    else:
        # 保有状況に基づいたプロンプトの生成
        holding_status = _generate_holding_status(data, currency)
        
        prompt = f"""
{data['symbol']}の分析をお願いします。

現在の株価: {data['price']}{currency}
{holding_status}

最近のニュース:
{chr(10).join(f"- {news}" for news in data['news'])}

以下の観点から分析してください：
1. 株価とニュースの要約
2. 現在のトレンドと今後の見通し
3. リスク要因とチャンス要因
4. 売買判断（買い/売り/ホールド/様子見）とその理由
5. 推奨する指値価格（買い注文または売り注文）

保有状況を考慮して、具体的な売買アクションを提案してください。
"""
    
    try:
        message = client.messages.create(
            model="claude-3-sonnet-latest",
            max_tokens=1500,
            temperature=0.5,
            system="あなたは株式分析の専門家です。データに基づいて客観的な分析と売買判断を提供してください。",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        error_msg = f"Claude API呼び出し失敗: {str(e)}"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**エラータイプ:** {type(e).__name__}"


def analyze_with_gemini(data, is_ipo=False):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    
    Args:
        data: 株価データと保有情報を含む辞書
        is_ipo: IPO銘柄の場合True（デフォルト: False）
    
    Returns:
        分析結果のテキスト
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        error_msg = "Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    currency = get_currency_for_symbol(data['symbol'], data.get('currency'))
    
    # IPO銘柄用のプロンプト
    if is_ipo:
        prompt = "あなたは株式分析の専門家です。データに基づいて客観的な分析と投資判断を提供してください。\n\n" + _generate_ipo_prompt(data, currency)
    else:
        # 保有状況に基づいたプロンプトの生成
        holding_status = _generate_holding_status(data, currency)
        
        prompt = (
            "あなたは株式分析の専門家です。データに基づいて客観的な分析と売買判断を提供してください。\n\n"
            f"{data['symbol']}の分析をお願いします。\n\n"
            f"現在の株価: {data['price']}{currency}\n"
            f"{holding_status}\n\n"
            f"最近のニュース:\n"
            f"{chr(10).join(f'- {news}' for news in data['news'])}\n\n"
            "以下の観点から分析してください：\n"
            "1. 株価とニュースの要約\n"
            "2. 現在のトレンドと今後の見通し\n"
            "3. リスク要因とチャンス要因\n"
            "4. 売買判断（買い/売り/ホールド/様子見）とその理由\n"
            "5. 推奨する指値価格（買い注文または売り注文）\n\n"
            "保有状況を考慮して、具体的な売買アクションを提案してください。"
        )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = f"Gemini APIエラー: HTTPステータス {resp.status_code}"
            error_detail = resp.text[:500]  # 最初の500文字のみ含める
            print(f"{error_msg}\n応答内容: {error_detail}")
            return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**API応答:** {error_detail}"
    except Exception as e:
        error_msg = f"Gemini API呼び出し失敗: {str(e)}"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}\n\n**エラータイプ:** {type(e).__name__}"


def _generate_holding_status(data, currency):
    """
    保有状況に基づいたプロンプトの文字列を生成する。
    
    Args:
        data: 株価データと保有情報を含む辞書
        currency: 通貨単位（「円」または「ドル」）
    
    Returns:
        保有状況を示す文字列
    """
    holding_status = ""
    account_type = data.get('account_type', '特定')
    
    if data.get('quantity') is not None:
        quantity = data['quantity']
        acquisition_price = data.get('acquisition_price')
        
        if quantity > 0:
            holding_status = f"現在の保有状況: {quantity}株を保有中（口座種別: {account_type}）"
            if acquisition_price:
                holding_status += f"（取得単価: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (data['price'] - acquisition_price) * quantity
                    profit_rate = ((data['price'] - acquisition_price) / acquisition_price) * 100
                    
                    # 税額計算
                    tax_amount = calculate_tax(profit_loss, account_type)
                    after_tax_profit = profit_loss - tax_amount
                    
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
                    
                    # 課税がある場合は税引後損益も表示
                    if tax_amount > 0:
                        holding_status += f"\n税額（約20.315%）: {tax_amount:,.0f}{currency}"
                        holding_status += f"\n税引後損益: {after_tax_profit:,.0f}{currency}"
                    elif account_type in ['NISA', '旧NISA']:
                        holding_status += f"\n税引後損益: {after_tax_profit:,.0f}{currency}（非課税）"
        elif quantity < 0:
            holding_status = f"現在の保有状況: {abs(quantity)}株を空売り中（信用売り、口座種別: {account_type}）"
            if acquisition_price:
                holding_status += f"（空売り価格: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (acquisition_price - data['price']) * abs(quantity)
                    profit_rate = ((acquisition_price - data['price']) / acquisition_price) * 100
                    
                    # 税額計算
                    tax_amount = calculate_tax(profit_loss, account_type)
                    after_tax_profit = profit_loss - tax_amount
                    
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
                    
                    # 課税がある場合は税引後損益も表示
                    if tax_amount > 0:
                        holding_status += f"\n税額（約20.315%）: {tax_amount:,.0f}{currency}"
                        holding_status += f"\n税引後損益: {after_tax_profit:,.0f}{currency}"
                    elif account_type in ['NISA', '旧NISA']:
                        holding_status += f"\n税引後損益: {after_tax_profit:,.0f}{currency}（非課税）"
        else:
            holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    else:
        holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    
    return holding_status


def _generate_ipo_prompt(data, currency):
    """
    IPO銘柄用のプロンプトを生成する。
    
    Args:
        data: IPO銘柄の情報を含む辞書
        currency: 通貨単位（「円」または「ドル」）
    
    Returns:
        IPO分析用のプロンプト文字列
    """
    name = data.get('name', data['symbol'])
    ipo_date = data.get('ipo_date', '未定')
    market = data.get('market', '未定')
    expected_price = data.get('expected_price')
    note = data.get('note', '')
    
    prompt = f"""
{name} ({data['symbol']})の上場予定銘柄について分析をお願いします。

上場予定日: {ipo_date}
上場市場: {market}
"""
    
    if expected_price:
        prompt += f"想定価格・公募価格: {expected_price}{currency}\n"
    
    if note:
        prompt += f"備考: {note}\n"
    
    prompt += """
以下の観点から分析してください：
1. 企業概要と事業内容（可能な範囲で）
2. IPO銘柄としての魅力と期待値
3. 上場後の株価動向の予測
4. 投資判断（購入検討/様子見/見送り）とその理由
5. 公募価格が設定されている場合、その妥当性
6. リスク要因と注意点

上場予定銘柄として、初値や上場後の値動きを考慮した投資判断を提案してください。
"""
    
    return prompt
