"""
AI分析モジュール

Claude SonnetまたはGemini APIを使用して株価・ニュースデータを分析します。
"""

import anthropic
import requests
from config import CLAUDE_API_KEY, GEMINI_API_KEY
from stock_loader import get_currency_for_symbol


def analyze_with_claude(data):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        error_msg = "Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    currency = get_currency_for_symbol(data['symbol'])
    
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


def analyze_with_gemini(data):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        error_msg = "Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    currency = get_currency_for_symbol(data['symbol'])
    
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
    if data.get('quantity') is not None:
        quantity = data['quantity']
        acquisition_price = data.get('acquisition_price')
        
        if quantity > 0:
            holding_status = f"現在の保有状況: {quantity}株を保有中"
            if acquisition_price:
                holding_status += f"（取得単価: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (data['price'] - acquisition_price) * quantity
                    profit_rate = ((data['price'] - acquisition_price) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        elif quantity < 0:
            holding_status = f"現在の保有状況: {abs(quantity)}株を空売り中（信用売り）"
            if acquisition_price:
                holding_status += f"（空売り価格: {acquisition_price}{currency}）"
                if data['price']:
                    profit_loss = (acquisition_price - data['price']) * abs(quantity)
                    profit_rate = ((acquisition_price - data['price']) / acquisition_price) * 100
                    holding_status += f"\n現在の損益: {profit_loss:,.0f}{currency}（{profit_rate:+.2f}%）"
        else:
            holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    else:
        holding_status = "現在の保有状況: 保有なし（購入または空売りを検討中）"
    
    return holding_status
