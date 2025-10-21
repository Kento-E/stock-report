# 投資志向性設定の例

このドキュメントには、様々な投資スタイルに応じた `investment_preferences.yaml` の設定例を示します。

## 例1: 成長投資家（テクノロジー企業重視）

積極的にリターンを追求し、成長性のある企業に投資するスタイル。

```yaml
investment_style: growth
risk_tolerance: high
investment_horizon: long
trading_frequency: low
focus_areas:
  - technical
  - momentum
  - news
custom_message: "テクノロジー企業や革新的なビジネスモデルを持つ企業を優先したい"
```

## 例2: バリュー投資家（割安株重視）

割安な株を見つけて長期保有するスタイル。

```yaml
investment_style: value
risk_tolerance: low
investment_horizon: long
trading_frequency: low
focus_areas:
  - fundamental
custom_message: "PERやPBRが低く、財務が健全な企業を優先"
```

## 例3: 配当投資家（安定収入重視）

配当や株主優待による安定した収入を重視するスタイル。

```yaml
investment_style: income
risk_tolerance: low
investment_horizon: long
trading_frequency: low
focus_areas:
  - dividend
  - fundamental
custom_message: "安定した配当が期待できる優良企業を優先"
```

## 例4: バランス投資家（中庸なスタイル）

成長性と安定性のバランスを重視するスタイル（デフォルト設定）。

```yaml
investment_style: balanced
risk_tolerance: medium
investment_horizon: medium
trading_frequency: medium
focus_areas:
  - fundamental
  - news
custom_message: ""
```

## 例5: 投機的トレーダー（短期売買重視）

短期的な値動きを利用して積極的に売買するスタイル。

```yaml
investment_style: speculative
risk_tolerance: high
investment_horizon: short
trading_frequency: high
focus_areas:
  - technical
  - momentum
  - news
custom_message: "短期的なトレンドを重視し、機動的に売買したい"
```

## 例6: ESG投資家（環境・社会重視）

環境や社会への配慮を重視する投資スタイル。

```yaml
investment_style: balanced
risk_tolerance: medium
investment_horizon: long
trading_frequency: low
focus_areas:
  - fundamental
  - news
custom_message: "環境に配慮した企業（ESG評価が高い企業）やSDGsに貢献する企業を優先したい"
```

## 例7: テクニカル分析重視のトレーダー

チャートやテクニカル指標を重視するスタイル。

```yaml
investment_style: growth
risk_tolerance: high
investment_horizon: medium
trading_frequency: high
focus_areas:
  - technical
  - momentum
custom_message: "移動平均線、RSI、MACDなどのテクニカル指標を重視"
```

## 設定のカスタマイズ方法

1. GitHub上で `data/investment_preferences.yaml` を開く
2. 編集ボタンをクリック
3. 上記の例を参考に、自分の投資スタイルに合わせて設定を変更
4. 変更をコミット
5. 次回のレポート生成時から新しい設定が反映されます

## 注意事項

- 設定を変更すると、AI分析の視点が変わります
- 自分のリスク許容度や投資目的に合った設定を選択してください
- 定期的に見直して、投資方針の変化に合わせて調整することをお勧めします
