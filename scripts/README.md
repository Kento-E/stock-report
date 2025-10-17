# scripts ディレクトリ

このディレクトリには、リポジトリの自動化スクリプトが含まれています。

## update_test_counts.py

テストケース数を自動算出して `docs/TEST.md` ファイルを更新するスクリプトです。

### 機能

- `tests/` ディレクトリ内の全テストファイルを検査
- pytest の `--collect-only` オプションを使用してテストケース数を算出
- `docs/TEST.md` のテストケース数テーブルを自動更新
- 変更がない場合は何もしない（冪等性を保証）

### 使用方法

```bash
# リポジトリのルートディレクトリから実行
python scripts/update_test_counts.py
```

### GitHub Actions での使用

このスクリプトは `.github/workflows/test.yml` で自動実行されます：

1. テスト実行後に自動的に実行
2. TEST.md に変更があれば自動コミット・プッシュ
3. 変更がなければスキップ

### 出力例

```
テストケース数を算出中...
TEST.md を更新しました
  test_ai_analyzer.py: 0 テスト
  test_data_fetcher.py: 2 テスト
  test_mail_utils.py: 10 テスト
  test_report_generator.py: 3 テスト
  test_stock_loader.py: 28 テスト
```

## update_line_counts.py

Pythonソースファイルの行数を自動算出して `.github/instructions/requirements.instructions.md` ファイルを更新するスクリプトです。

### 機能

- `src/` ディレクトリ内の全Pythonファイルの行数を算出
- `requirements.instructions.md` の行数表記を自動更新
- 変更がない場合は何もしない（冪等性を保証）

### 使用方法

```bash
# リポジトリのルートディレクトリから実行
python scripts/update_line_counts.py
```

### GitHub Actions での使用

このスクリプトは `.github/workflows/test.yml` で自動実行されます：

1. テスト実行後に自動的に実行
2. requirements.instructions.md に変更があれば自動コミット・プッシュ
3. 変更がなければスキップ

### 出力例

```
ソースファイルの行数を算出中...
requirements.instructions.md を更新しました
  main.py: 92 行
  config.py: 31 行
  stock_loader.py: 156 行
  data_fetcher.py: 94 行
  ai_analyzer.py: 163 行
  report_generator.py: 39 行
  mail_utils.py: 125 行
```
