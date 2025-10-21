# モジュール分割リファレンス

## 概要

本プロジェクトはAPI別・機能別にモジュール化されており、保守性と拡張性を向上させています。

システム全体の詳細な要件定義については [requirements.instructions.md](../.github/instructions/requirements.instructions.md) を参照してください。

## モジュール一覧

各モジュールは単一責任の原則に従って設計されています。

### config.py

**責務**: 環境変数と設定値の一元管理

**主な公開変数**:
- `CLAUDE_API_KEY`, `GEMINI_API_KEY`, `YAHOO_API_KEY`
- `MAIL_TO`, `USE_CLAUDE`, `DEFEATBETA_AVAILABLE`

### stock_loader.py

**責務**: 銘柄リストの読み込み、通貨判定、銘柄分類

**主な関数**:
- `load_stock_symbols()`: YAML形式の銘柄リスト読み込み
- `get_currency_for_symbol()`: 市場通貨の自動判定
- `categorize_stocks()`: 保有状況に基づく銘柄分類

### validate_stocks.py

**責務**: stocks.yamlファイルのバリデーション

**主な機能**:
- YAML構文の正確性チェック
- 必須フィールド・型・値の範囲検証
- GitHub Actionsで自動実行

### data_fetcher.py

**責務**: 外部APIからのデータ取得

**主な関数**:
- `fetch_stock_data()`: Yahoo Finance APIから株価データ取得
- `fetch_news()`: defeatbeta-apiからニュースデータ取得

### ai_analyzer.py

**責務**: AI分析処理

**主な関数**:
- `analyze_with_claude()`: Claude APIによる株価分析
- `analyze_with_gemini()`: Gemini APIによる株価分析
- 保有状況に基づいた損益計算と売買判断の提供

### report_generator.py

**責務**: HTMLレポートの生成

**主な関数**:
- `generate_report_html()`: 分析結果のHTMLフォーマット化とファイル保存

### mail_utils.py

**責務**: メール配信処理

**主な関数**:
- `get_smtp_config()`: SMTP設定取得
- `markdown_to_html()`: Markdown→HTML変換
- `generate_categorized_mail_body()`: 分類別メール本文生成
- `send_report_via_mail()`: HTMLメール送信（BCC対応）

### main.py

**責務**: メインエントリーポイント・オーケストレーション

**処理フロー**: 銘柄リスト読み込み → 分類 → データ収集 → AI分析 → レポート生成 → メール配信

## モジュール間の依存関係

```
main.py (オーケストレーション)
├── config.py
├── stock_loader.py
├── data_fetcher.py
│   └── config.py
├── ai_analyzer.py
│   ├── config.py
│   └── stock_loader.py
├── report_generator.py
│   └── mail_utils.py
└── mail_utils.py
```

依存関係の詳細については [requirements.instructions.md](../.github/instructions/requirements.instructions.md) を参照してください。

## 使用方法

### 基本的な実行

```bash
# Gemini使用（デフォルト）
python src/main.py

# Claude使用
python src/main.py --claude
```

### モジュール単体の使用例

```python
# 銘柄リストの読み込み
from stock_loader import load_stock_symbols
stocks = load_stock_symbols()

# 株価データの取得
from data_fetcher import fetch_stock_data
data = fetch_stock_data('7203.T')

# AI分析
from ai_analyzer import analyze_with_gemini
analysis = analyze_with_gemini(data)

# レポート生成
from report_generator import generate_report_html
html, filename = generate_report_html('7203.T', 'トヨタ自動車', analysis)
```

## テスト

テストの実行方法については [TEST.md](TEST.md) を参照してください。

## 設計メリット

### 保守性の向上
- 各モジュールが単一の責任を持つため、修正箇所が明確
- バグ修正時の影響範囲が限定される

### 拡張性の向上
- 新しいAI APIの追加が容易（ai_analyzerに関数追加）
- 新しいデータソースの追加が容易（data_fetcherに関数追加）

### テスト可能性の向上
- 各モジュールを独立してテスト可能
- 単体テストの作成が簡単

### 可読性の向上
- 機能ごとにファイルが分かれているため、目的のコードを見つけやすい
- インポート文を見れば依存関係が明確

## 注意事項

- すべてのモジュールは`src/`ディレクトリ内に配置
- 相対インポートではなく、モジュール名で直接インポート
- 環境変数は必ず`config.py`経由で取得
- エラーハンドリングは各モジュールで適切に実装
