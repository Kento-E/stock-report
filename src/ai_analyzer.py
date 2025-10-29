"""
AI分析モジュール

Claude SonnetまたはGemini APIを使用して株価・ニュースデータを分析します。
"""

import anthropic
import requests
from config import CLAUDE_API_KEY, GEMINI_API_KEY
from stock_loader import get_currency_for_symbol, calculate_tax
from preference_loader import generate_preference_prompt


# AI分析の観点（共通）
ANALYSIS_VIEWPOINTS = """以下の観点から分析してください（結論を最初に記載してください）：
1. 売買判断（買い/買い増し/売り/ホールド/様子見）とその理由
   ※重要: 売買判断は以下のいずれか1つの単語のみで明示してください。
   　・買い
   　・買い増し
   　・売り
   　・ホールド
   　・様子見
   　例：「売買判断: 買い」「売買判断: ホールド」
2. 推奨する指値価格（買い注文または売り注文）
3. 株価とニュースの要約
4. 現在のトレンドと今後の見通し
5. リスク要因とチャンス要因

上記の投資家の志向性を考慮して、具体的な売買アクションを提案してください。
保有中の銘柄については、売却だけでなく買い増しの検討も含めて判断してください。"""


def analyze_with_claude(data, preference_prompt=None):
    """
    Claude Sonnet APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    
    Args:
        data: 株価データと保有情報を含む辞書
        preference_prompt: 投資志向性プロンプト（省略時は毎回生成）
    """
    if not CLAUDE_API_KEY or CLAUDE_API_KEY.strip() == "":
        error_msg = "Claude APIエラー: APIキーが未設定です。環境変数CLAUDE_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    currency = get_currency_for_symbol(data['symbol'], data.get('currency'))
    
    # 保有状況に基づいたプロンプトの生成
    holding_status = _generate_holding_status(data, currency)
    
    # 投資志向性プロンプトの生成（渡されていない場合のみ）
    if preference_prompt is None:
        preference_prompt = generate_preference_prompt()
    
    prompt = f"""
{data['symbol']}の分析をお願いします。

現在の株価: {data['price']}{currency}
{holding_status}

最近のニュース:
{chr(10).join(f"- {news}" for news in data['news'])}

{preference_prompt}

{ANALYSIS_VIEWPOINTS}
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


def analyze_with_gemini(data, preference_prompt=None):
    """
    Gemini APIを用いて株価・ニュースデータを分析し、要約・トレンド抽出・リスク/チャンスの指摘と売買判断を返す。
    
    Args:
        data: 株価データと保有情報を含む辞書
        preference_prompt: 投資志向性プロンプト（省略時は毎回生成）
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        error_msg = "Gemini APIエラー: APIキーが未設定です。環境変数GEMINI_API_KEYを確認してください。"
        print(error_msg)
        return f"## 分析失敗\n\n**エラー内容:** {error_msg}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    currency = get_currency_for_symbol(data['symbol'], data.get('currency'))
    
    # 保有状況に基づいたプロンプトの生成
    holding_status = _generate_holding_status(data, currency)
    
    # 投資志向性プロンプトの生成（渡されていない場合のみ）
    if preference_prompt is None:
        preference_prompt = generate_preference_prompt()
    
    prompt = (
        "あなたは株式分析の専門家です。データに基づいて客観的な分析と売買判断を提供してください。\n\n"
        f"{data['symbol']}の分析をお願いします。\n\n"
        f"現在の株価: {data['price']}{currency}\n"
        f"{holding_status}\n\n"
        f"最近のニュース:\n"
        f"{chr(10).join(f'- {news}' for news in data['news'])}\n\n"
        f"{preference_prompt}\n\n"
        f"{ANALYSIS_VIEWPOINTS}"
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
