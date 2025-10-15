# モジュール分割リファレンス

## 概要

main.pyファイルを機能別・API別に分割し、保守性と拡張性を向上させました。

## 分割前後の比較

| 項目 | 分割前 | 分割後 | 最新 |
|------|--------|--------|------|
| main.pyの行数 | 428行 | 64行 | 76行 |
| ファイル数 | 2ファイル | 7ファイル | 7ファイル |
| 責任の分離 | 単一ファイルに集約 | 機能別に明確に分離 | 機能別に明確に分離 |
| メール分類 | なし | なし | 3分類対応 |

## モジュール一覧

### 1. config.py (31行)

**責務**: 環境変数と設定値の一元管理

**主な機能**:
- 環境変数の読み込み（dotenv）
- APIキーの取得と管理
- defeatbeta-apiの可用性チェック
- 実行オプションの判定（Claude/Gemini選択）

**公開される変数**:
- `CLAUDE_API_KEY`: Claude APIキー
- `GEMINI_API_KEY`: Gemini APIキー
- `YAHOO_API_KEY`: Yahoo Finance APIキー
- `MAIL_TO`: メール送信先
- `USE_CLAUDE`: Claude使用フラグ
- `DEFEATBETA_AVAILABLE`: defeatbeta-api可用性フラグ

### 2. stock_loader.py (136行)

**責務**: 銘柄リストの読み込み、通貨判定、銘柄分類

**主な機能**:
- YAML形式の銘柄リストファイルの読み込み
- 銘柄情報の構造化（symbol, name, quantity, acquisition_price等）
- 市場通貨の自動判定（日本株=円、米国株=ドル）
- 保有状況に基づく銘柄分類（保有中、空売り中、購入検討中）
- エラーハンドリング（ファイル不在、YAML構文エラー等）

**公開される関数**:
- `load_stock_symbols(filepath='data/stocks.yaml')`: 銘柄リスト読み込み
- `get_currency_for_symbol(symbol)`: 通貨判定関数
- `categorize_stock(stock_info)`: 個別銘柄の分類判定
- `categorize_stocks(stocks)`: 銘柄リストの一括分類

### 3. data_fetcher.py (93行)

**責務**: 外部APIからのデータ取得

**主な機能**:
- Yahoo Finance APIからの株価データ取得
- defeatbeta-apiからのニュースデータ取得（最大5件）
- 保有情報の統合
- エラーハンドリングとフォールバック処理

**公開される関数**:
- `fetch_stock_data(symbol, stock_info=None)`: 株価・ニュース・保有情報の統合取得
- `fetch_news(symbol)`: ニュースデータ取得

**依存関係**:
- `config.YAHOO_API_KEY`
- `config.DEFEATBETA_AVAILABLE`

### 4. ai_analyzer.py (163行)

**責務**: AI分析処理

**主な機能**:
- Claude Sonnet APIによる株価分析
- Gemini APIによる株価分析
- 保有状況に基づいたプロンプト生成
- 損益計算と売買判断の提供
- エラーハンドリング

**公開される関数**:
- `analyze_with_claude(data)`: Claude API分析
- `analyze_with_gemini(data)`: Gemini API分析

**内部関数**:
- `_generate_holding_status(data, currency)`: 保有状況プロンプト生成

**依存関係**:
- `config.CLAUDE_API_KEY`
- `config.GEMINI_API_KEY`
- `stock_loader.get_currency_for_symbol`

### 5. report_generator.py (39行)

**責務**: HTMLレポートの生成

**主な機能**:
- 分析結果のHTMLフォーマット化
- レポートファイルの生成と保存
- Markdown→HTML変換

**公開される関数**:
- `generate_report_html(symbol, name, analysis)`: HTMLレポート生成

**依存関係**:
- `mail_utils.markdown_to_html`

### 6. main.py (76行)

**責務**: メインエントリーポイント・オーケストレーション

**主な処理フロー**:
1. 銘柄リストの読み込み
2. 銘柄の分類（保有中、空売り中、購入検討中）
3. 各分類の銘柄のデータ収集
4. AI分析の実行
5. レポート生成
6. 分類別メール配信

**依存関係**: すべてのモジュール

### 7. mail_utils.py (103行)

**責務**: メール配信処理

**主な機能**:
- SMTP設定の取得
- HTMLメールの送信
- Markdown→HTML変換
- 分類別メール本文の生成
- BCC送信による複数宛先対応

**公開される関数**:
- `get_smtp_config()`: SMTP設定取得
- `markdown_to_html(markdown_text)`: Markdown→HTML変換
- `generate_mail_body(subject, all_reports)`: 従来形式のメール本文生成（後方互換性）
- `generate_categorized_mail_body(subject, categorized_reports)`: 分類別メール本文生成
- `send_report_via_mail(...)`: メール送信

## モジュール間の依存関係図

```
main.py
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

## メリット

### 1. 保守性の向上

- 各モジュールが単一の責任を持つため、修正箇所が明確
- バグ修正時の影響範囲が限定される
- コードレビューが容易

### 2. 拡張性の向上

- 新しいAI APIの追加が容易（ai_analyzerに関数追加）
- 新しいデータソースの追加が容易（data_fetcherに関数追加）
- 設定値の追加が容易（config.pyに変数追加）

### 3. テスト可能性の向上

- 各モジュールを独立してテスト可能
- モックオブジェクトの導入が容易
- 単体テストの作成が簡単

### 4. 可読性の向上

- ファイルサイズが小さく、理解が容易
- 機能ごとにファイルが分かれているため、目的のコードを見つけやすい
- インポート文を見れば依存関係が明確

## 今後の拡張例

### 新しいAI APIの追加

```python
# ai_analyzer.pyに追加
def analyze_with_new_ai(data):
    """新しいAI APIによる分析"""
    # 実装
```

### 新しいデータソースの追加

```python
# data_fetcher.pyに追加
def fetch_from_new_source(symbol):
    """新しいデータソースから取得"""
    # 実装
```

### 設定値の追加

```python
# config.pyに追加
NEW_API_KEY = os.getenv('NEW_API_KEY')
```

## 注意事項

- すべてのモジュールは`src/`ディレクトリ内に配置
- 相対インポートではなく、モジュール名で直接インポート
- 環境変数は必ず`config.py`経由で取得
- エラーハンドリングは各モジュールで適切に実装
