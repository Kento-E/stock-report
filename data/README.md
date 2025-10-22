# データファイル編集ガイド

このディレクトリには、株式レポートシステムの設定ファイルが格納されています。

## 銘柄リスト (stocks.yaml)

`stocks.yaml` ファイルは、分析対象とする銘柄リストを管理するファイルです。

## ファイル形式

YAML形式で記述されており、各銘柄は以下の情報を持ちます。

### 必須フィールド

- **symbol**: 銘柄コード（必須）
  - 日本株: 4桁の数字または `7203.T` のような形式
  - 米国株: `AAPL` のようなティッカーシンボル
  - その他の市場: `BMW.DE` のような形式

### 任意フィールド

- **name**: 企業名（任意）
  - レポートの見出しに使用されます
  - 未設定の場合は銘柄コードが表示されます

- **added**: 追加日（任意）
  - 銘柄をリストに追加した日付

- **note**: メモ（任意）
  - 銘柄に関する自由なメモや注記

- **quantity**: 保有数（任意）
  - 正の数: 保有中の銘柄
  - 負の数: 空売り中の銘柄
  - 0または未設定: 購入検討中の銘柄

- **acquisition_price**: 取得単価（任意）
  - 購入価格または空売り価格
  - 損益計算に使用されます

- **currency**: 通貨単位（任意）
  - 円、ドル、ユーロ、ポンドなど
  - 未設定の場合は銘柄シンボルから自動判定されます
    - 日本株（.T、.JP、または4桁数字）: 円
    - その他: ドル

- **considering_action**: 検討中の行動（任意）
  - `buy`: 購入を検討中（デフォルト）
  - `short_sell`: 空売りを検討中

- **account_type**: 口座種別（任意、デフォルト: '特定'）
  - **特定**: 譲渡益に20.315%課税
  - **NISA**: 非課税
  - **旧NISA**: 非課税

## 記述例

```yaml
stocks:
  - symbol: 7203.T
    name: トヨタ自動車
    added: 2024-01-01
    note: 自動車メーカー最大手
    quantity: 100
    acquisition_price: 2500
    currency: 円
    account_type: NISA
  
  - symbol: 6758.T
    name: ソニーグループ
    quantity: -50
    acquisition_price: 12000
    note: 空売りポジション
  
  - symbol: AAPL
    name: Apple Inc.
    currency: ドル
  
  - symbol: BMW.DE
    name: BMW
    currency: ユーロ
    quantity: 50
    acquisition_price: 95
```

## 投資志向性設定 (investment_preferences.yaml)

`investment_preferences.yaml` ファイルは、ユーザーの投資に対する志向性を管理するファイルです。この設定はAI分析時のプロンプトに反映され、個人の投資方針に合わせた分析結果を提供します。

### 編集方法

1. GitHub上で `data/investment_preferences.yaml` ファイルを開く
2. 編集ボタン（鉛筆アイコン）をクリック
3. 投資スタイル、リスク許容度などの設定を編集
4. 変更をコミット

スマートフォンのブラウザからも同様の手順で編集できます。

### 設定項目

各設定項目の詳細は `investment_preferences.yaml` ファイル内のコメントを参照してください。

#### 投資スタイル (`investment_style`)

- `growth`: 成長投資（成長性重視、高リスク・高リターン）
- `value`: バリュー投資（割安株投資、中リスク・中リターン）
- `income`: インカムゲイン投資（配当・優待重視、低リスク・安定志向）
- `balanced`: バランス投資（成長と配当のバランス、中リスク）
- `speculative`: 投機的投資（短期売買、高リスク・高リターン）

#### リスク許容度 (`risk_tolerance`)

- `low`: 低リスク（元本重視、安全性優先）
- `medium`: 中リスク（適度なリスクとリターンのバランス）
- `high`: 高リスク（積極的なリターン追求、損失許容度が高い）

#### 投資期間 (`investment_horizon`)

- `short`: 短期（数日～数週間）
- `medium`: 中期（数ヶ月～1年）
- `long`: 長期（数年以上）

#### 売買頻度 (`trading_frequency`)

- `high`: 頻繁（デイトレード、スイングトレード）
- `medium`: 適度（週次～月次で売買）
- `low`: 少ない（バイ&ホールド、長期保有）

#### 重視する指標 (`focus_areas`)

複数選択可能：

- `technical`: テクニカル分析（チャート、移動平均、RSIなど）
- `fundamental`: ファンダメンタル分析（PER、PBR、財務状況）
- `news`: ニュース・イベント（市場センチメント、企業ニュース）
- `dividend`: 配当利回り（株主優待、インカムゲイン）
- `momentum`: モメンタム（トレンド、勢い）

#### カスタムメッセージ (`custom_message`)

AIへの追加の指示や好みを自由記述できます。

例: 「環境に配慮した企業を優先したい」「テクノロジー企業に関心がある」

### 設定例

```yaml
# 成長投資家の例
investment_style: growth
risk_tolerance: high
investment_horizon: long
trading_frequency: low
focus_areas:
  - technical
  - momentum
custom_message: "テクノロジー企業を優先したい"
```

```yaml
# 配当重視の安定志向投資家の例
investment_style: income
risk_tolerance: low
investment_horizon: long
trading_frequency: low
focus_areas:
  - dividend
  - fundamental
custom_message: "安定した配当が期待できる企業を優先"
```
