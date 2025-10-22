# 銘柄リスト (stocks.yaml) の編集ガイド

このディレクトリの `stocks.yaml` ファイルは、株式レポートシステムで分析対象とする銘柄リストを管理するファイルです。

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
