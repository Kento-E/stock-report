# 売買タイミング機能 - 実装完了サマリー

## 実装された機能

Issue で要求された売買タイミング分析機能をすべて実装しました。

### 1. 保有情報の設定

`data/stocks.yaml` ファイルに以下のフィールドを追加：

```yaml
stocks:
  - symbol: 7203.T
    name: トヨタ自動車
    quantity: 100              # 保有数（プラス=保有、マイナス=空売り）
    acquisition_price: 2500    # 取得単価
```

### 2. 保有状況の解釈

- **正の数（例: 100）**: 保有中の銘柄として扱い、売却タイミングを分析
- **負の数（例: -50）**: 空売り中の銘柄として扱い、買戻しタイミングを分析
- **未設定**: 購入検討中の銘柄として扱い、新規エントリーのタイミングを分析

### 3. AI分析の拡張

AIが以下の情報を提供するようになりました：

- 現在の損益状況（取得単価が設定されている場合）
- 売買判断（買い/売り/ホールド/様子見）とその理由
- 推奨する指値価格（買い注文または売り注文）
- 保有状況を考慮した具体的な売買アクション

## ファイルの変更内容

### 変更されたファイル

1. **src/main.py**
   - `load_stock_symbols()`: 銘柄情報を辞書として返すように変更
   - `fetch_stock_data()`: 保有情報を含むように拡張
   - `analyze_with_claude()`: 保有状況に基づいた分析プロンプトを生成
   - `analyze_with_gemini()`: 保有状況に基づいた分析プロンプトを生成
   - メインループ: 銘柄情報を渡すように変更

2. **data/stocks.yaml**
   - サンプルデータに `quantity` と `acquisition_price` フィールドを追加

3. **README.md**
   - 新しいフィールドの説明を追加
   - 保有情報の活用方法を説明

4. **.github/instructions/requirements.instructions.md**
   - 売買タイミング分析機能のセクションを追加

### 追加されたファイル

1. **docs/test_report/trading_timing_feature.md**
   - 機能のテストレポート

2. **docs/examples/ai_prompt_examples.md**
   - AI分析プロンプトの例

## 使用方法

### 基本的な使い方

1. `data/stocks.yaml` を編集して、銘柄の保有情報を設定

```yaml
stocks:
  - symbol: 7203.T
    name: トヨタ自動車
    quantity: 100
    acquisition_price: 2500
```

2. GitHub Actions で自動実行されるか、ローカルで実行

```bash
python src/main.py
```

3. レポートに売買判断と指値価格が含まれる

### 設定例

```yaml
stocks:
  # 保有中の銘柄
  - symbol: 7203.T
    name: トヨタ自動車
    quantity: 100
    acquisition_price: 2500
  
  # 空売り中の銘柄
  - symbol: 6758.T
    name: ソニーグループ
    quantity: -50
    acquisition_price: 12000
    note: 空売りポジション
  
  # 購入検討中の銘柄
  - symbol: AAPL
    name: Apple Inc.
    # quantity未設定
```

## 技術的な詳細

### 後方互換性

- 既存の銘柄リスト（保有情報なし）も引き続き動作
- `quantity` と `acquisition_price` はオプション項目

### 損益計算

取得単価が設定されている場合、以下の計算が自動的に行われます：

- **保有中**: `損益 = (現在価格 - 取得単価) × 保有数`
- **空売り中**: `損益 = (取得単価 - 現在価格) × 保有数の絶対値`
- **損益率**: `損益率 = 損益 / (取得単価 × 保有数の絶対値) × 100`

### AI分析プロンプト

AIに以下の情報が渡されます：

- 現在の株価
- 保有状況（保有数、取得単価）
- 現在の損益（計算済み）
- 最近のニュース

AIは保有状況を考慮して、具体的な売買アクションを提案します。

## テスト結果

すべてのテストが成功しました：

- ✅ YAMLファイルの解析
- ✅ 銘柄情報の読み込み
- ✅ 保有状況の解釈
- ✅ 通貨判定
- ✅ 損益計算
- ✅ コード構文チェック

詳細は `docs/test_report/trading_timing_feature.md` を参照してください。

## 次のステップ

本番環境（GitHub Actions）で実行すると、実際のAI分析結果が確認できます。

必要なAPIキー：
- `CLAUDE_API_KEY` または `GEMINI_API_KEY`
- `YAHOO_API_KEY`
- SMTPメール設定

## 関連ドキュメント

- テストレポート: `docs/test_report/trading_timing_feature.md`
- プロンプト例: `docs/examples/ai_prompt_examples.md`
- 要件定義書: `.github/instructions/requirements.instructions.md`
- README: `README.md`
