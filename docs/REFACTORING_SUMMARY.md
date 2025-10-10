# main.py 分割前後の比較

## ファイル構成の変化

### 分割前

```
src/
├── main.py (428行) ← すべての機能が詰め込まれている
│   ├── 環境変数管理
│   ├── YAML読み込み
│   ├── 株価データ取得
│   ├── ニュースデータ取得
│   ├── Claude API分析
│   ├── Gemini API分析
│   ├── HTMLレポート生成
│   └── メインフロー
└── mail_utils.py (60行)
    └── メール配信
```

### 分割後

```
src/
├── config.py (31行)
│   └── 環境変数管理
│
├── stock_loader.py (83行)
│   ├── YAML読み込み
│   └── 通貨判定
│
├── data_fetcher.py (93行)
│   ├── 株価データ取得
│   └── ニュースデータ取得
│
├── ai_analyzer.py (163行)
│   ├── Claude API分析
│   ├── Gemini API分析
│   └── 保有状況プロンプト生成
│
├── report_generator.py (39行)
│   └── HTMLレポート生成
│
├── mail_utils.py (60行)
│   └── メール配信
│
└── main.py (64行) ← シンプルなオーケストレーション
    └── メインフロー
```

## コード量の比較

| 項目 | 分割前 | 分割後 | 削減率 |
|------|--------|--------|--------|
| main.pyの行数 | 428行 | 64行 | **85%削減** |
| 総ファイル数 | 2個 | 7個 | - |
| 総行数 | 488行 | 532行 | +9% (構造化のため) |
| 平均ファイルサイズ | 244行 | 76行 | **69%削減** |

## 可読性の比較

### 分割前のmain.py

```python
# main.py (428行)
# すべての機能が一つのファイルに...

from dotenv import load_dotenv
import os
import sys
import datetime
import requests
import anthropic
import yaml
from mail_utils import send_report_via_mail, get_smtp_config, generate_mail_body, markdown_to_html

try:
    from defeatbeta_api.data.ticker import Ticker
    DEFEATBETA_AVAILABLE = True
except ImportError:
    DEFEATBETA_AVAILABLE = False

load_dotenv()
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MAIL_TO = os.getenv('MAIL_TO')
YAHOO_API_KEY = os.getenv('YAHOO_API_KEY')
USE_CLAUDE = "--claude" in sys.argv

def load_stock_symbols(filepath='data/stocks.yaml'):
    # 60行の実装...
    
def get_currency_for_symbol(symbol):
    # 通貨判定...
    
def fetch_stock_data(symbol, stock_info=None):
    # 40行の実装...
    
def fetch_news(symbol):
    # 40行の実装...
    
def analyze_with_claude(data):
    # 80行の実装...
    
def analyze_with_gemini(data):
    # 80行の実装...
    
def generate_report_html(symbol, name, analysis):
    # 30行の実装...

if __name__ == "__main__":
    # メインフロー...
```

### 分割後のmain.py

```python
# main.py (64行)
# シンプルで読みやすい！

import sys
import datetime
import yaml
from config import USE_CLAUDE, MAIL_TO
from stock_loader import load_stock_symbols
from data_fetcher import fetch_stock_data
from ai_analyzer import analyze_with_claude, analyze_with_gemini
from report_generator import generate_report_html
from mail_utils import send_report_via_mail, get_smtp_config, generate_mail_body, markdown_to_html

if __name__ == "__main__":
    try:
        stocks = load_stock_symbols()
        print(f"分析対象銘柄: {[s['symbol'] for s in stocks]}")
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        print(f"\n{str(e)}")
        print("\n処理を終了します。")
        sys.exit(1)
    
    all_reports = []
    for stock_info in stocks:
        symbol = stock_info['symbol']
        name = stock_info.get('name', symbol)
        data = fetch_stock_data(symbol, stock_info)
        if USE_CLAUDE:
            analysis = analyze_with_claude(data)
        else:
            analysis = analyze_with_gemini(data)
        html, filename = generate_report_html(symbol, name, analysis)
        print(f"レポート生成: {filename}")
        analysis_html = markdown_to_html(analysis)
        all_reports.append(f"<h1>{name}</h1>\n<p style=\"color: #666; font-size: 14px;\">銘柄コード: {symbol}</p>\n{analysis_html}")

    smtp_conf = get_smtp_config()
    if MAIL_TO and all(smtp_conf.values()):
        today = datetime.date.today().isoformat()
        subject = f"株式日次レポート ({today})"
        body = generate_mail_body(subject, all_reports)
        send_report_via_mail(
            subject, body, MAIL_TO,
            smtp_conf['MAIL_FROM'], smtp_conf['SMTP_SERVER'], smtp_conf['SMTP_PORT'], smtp_conf['SMTP_USER'], smtp_conf['SMTP_PASS']
        )
```

## メリット

### 1. 保守性 ⬆️

- **修正箇所が明確**: 株価取得に問題があれば`data_fetcher.py`のみを確認
- **影響範囲が限定**: AI分析の変更が他の機能に影響しない
- **コードレビューが容易**: 小さなファイルで変更内容を理解しやすい

### 2. 拡張性 ⬆️

- **新API追加が簡単**: `ai_analyzer.py`に関数を追加するだけ
- **独立した開発**: 複数の機能を並行して開発可能
- **プラグイン化が容易**: 将来的にはプラグインアーキテクチャへの移行も可能

### 3. テスト可能性 ⬆️

- **単体テストが簡単**: 各モジュールを独立してテスト可能
- **モック化が容易**: 外部APIをモック化しやすい
- **テストカバレッジ向上**: 小さな関数をすべてテスト可能

### 4. 可読性 ⬆️

- **機能が明確**: ファイル名で機能が分かる
- **ナビゲーションが容易**: IDEのファイル一覧で目的のコードをすぐ発見
- **学習コストが低い**: 新しい開発者も理解しやすい

## 依存関係

```
main.py (オーケストレーション)
  │
  ├─→ config.py (設定)
  │
  ├─→ stock_loader.py (銘柄データ)
  │
  ├─→ data_fetcher.py (データ取得)
  │     └─→ config.py
  │
  ├─→ ai_analyzer.py (AI分析)
  │     ├─→ config.py
  │     └─→ stock_loader.py
  │
  ├─→ report_generator.py (レポート生成)
  │     └─→ mail_utils.py
  │
  └─→ mail_utils.py (メール配信)
```

依存関係がシンプルで、循環依存がない設計になっています。

## まとめ

main.pyの分割により、コードの品質が大幅に向上しました：

- ✅ **85%のコード削減** (428行 → 64行)
- ✅ **機能が明確に分離**
- ✅ **保守性・拡張性・テスト可能性・可読性の向上**
- ✅ **新しい開発者にも理解しやすい構造**
