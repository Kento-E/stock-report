# 見出し変更の実装例

## 変更前と変更後の比較

### 変更前（銘柄コードのみ）

HTMLレポートの見出し:
```html
<h1>7203.T 日次レポート (2025-10-10)</h1>
```

メール本文の見出し:
```html
<h1>7203.T</h1>
<h2>市場分析</h2>
<p>トヨタ自動車の株価は...</p>
```

**問題点:**
- 銘柄コード（7203.T）だけでは、どの企業かすぐに分からない
- 複数の銘柄を見ている場合、どれがどの企業か混乱しやすい

### 変更後（企業名を見出しに使用）

HTMLレポートの見出し:
```html
<h1>トヨタ自動車</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: 7203.T | 日付: 2025-10-10</p>
```

メール本文の見出し:
```html
<h1>トヨタ自動車</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: 7203.T</p>
<h2>市場分析</h2>
<p>トヨタ自動車の株価は...</p>
```

**改善点:**
- ✅ 企業名が見出しになり、一目で分かりやすい
- ✅ 銘柄コードは副題として表示され、必要な情報も確認できる
- ✅ 企業名が設定されていない場合は、銘柄コードが見出しになる（後方互換性）

## 技術的な変更内容

### 1. `load_stock_symbols()`関数

**変更前:**
```python
def load_stock_symbols(filepath='data/stocks.yaml'):
    # ...
    return ['7203.T', '6758.T', 'AAPL', 'MSFT']  # 銘柄コードのリスト
```

**変更後:**
```python
def load_stock_symbols(filepath='data/stocks.yaml'):
    # ...
    return [
        {'symbol': '7203.T', 'name': 'トヨタ自動車'},
        {'symbol': '6758.T', 'name': 'ソニーグループ'},
        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'}
    ]  # 銘柄情報の辞書のリスト
```

### 2. `generate_report_html()`関数

**変更前:**
```python
def generate_report_html(symbol, analysis):
    html = f"""
    <h1>{symbol} 日次レポート ({today})</h1>
    {analysis_html}
    """
```

**変更後:**
```python
def generate_report_html(symbol, name, analysis):
    html = f"""
    <h1>{name}</h1>
    <p style="color: #666; font-size: 14px;">銘柄コード: {symbol} | 日付: {today}</p>
    {analysis_html}
    """
```

### 3. メイン実行部

**変更前:**
```python
for symbol in symbols:
    data = fetch_stock_data(symbol)
    analysis = analyze_with_gemini(data)
    html, filename = generate_report_html(symbol, analysis)
    all_reports.append(f"<h1>{symbol}</h1>\n{analysis_html}")
```

**変更後:**
```python
for stock in stocks:
    symbol = stock['symbol']
    name = stock['name']
    data = fetch_stock_data(symbol)
    analysis = analyze_with_gemini(data)
    html, filename = generate_report_html(symbol, name, analysis)
    all_reports.append(f"<h1>{name}</h1>\n<p style=\"color: #666; font-size: 14px;\">銘柄コード: {symbol}</p>\n{analysis_html}")
```

## 後方互換性

- `data/stocks.yaml`に`name`フィールドが設定されていない銘柄は、`symbol`がフォールバックとして使用される
- 既存のYAMLファイルをそのまま使用でき、後から`name`フィールドを追加するだけで企業名表示が有効になる

## 例: 複数銘柄のメールレポート

```html
<h1>トヨタ自動車</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: 7203.T</p>
<p>トヨタ自動車の株価は15,234円で...</p>

<h1>ソニーグループ</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: 6758.T</p>
<p>ソニーグループの株価は13,456円で...</p>

<h1>Apple Inc.</h1>
<p style="color: #666; font-size: 14px;">銘柄コード: AAPL</p>
<p>Apple Inc.の株価は$180.50で...</p>
```

このように、見出しが企業名になることで、複数銘柄のレポートも読みやすくなります。
