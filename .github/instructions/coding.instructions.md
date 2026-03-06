# コーディングガイドライン

## Markdown

本プロジェクトで Markdown ファイル（README, 要件定義書, 質問リスト等）を生成・編集する際は、以下の Lint ルールに必ず準拠すること。

- 見出し階層は 1 段階ずつ（MD001）
- 見出し・リストの前後に必ず空行（MD022, MD032）
- h1 は 1 つのみ（MD025）
- ファイル末尾は 1 つの改行のみ（MD047）

これらを満たす Markdown のみ出力・編集すること。

## Python コーディング規約

### エラーハンドリングの必須チェック項目

- **リストや配列へのアクセス前に空チェックを実施**
  - `list[0]`のようなアクセスの前に、必ず`if not list:`または`if len(list) > 0:`でチェック
  - 例: `if similar_messages: first_message = similar_messages[0]`

- **`random.choice()`などの関数は空リストでエラーになるため事前チェック必須**
  - 空リストで`random.choice()`を呼ぶとIndexErrorが発生
  - 例: `ending = random.choice(endings) if endings else "。"`

- **`dict.get()`でデフォルト値を指定し、Noneチェックを追加**
  - `dict.get(key, default_value)`を使用してNone回避
  - 取得後も値が空でないことを確認
  - 例: `greetings = persona.get('sample_greetings', []); if greetings: ...`

- **ファイル・ディレクトリ操作前に存在確認**
  - ディレクトリ作成: `os.makedirs(path, exist_ok=True)`
  - ファイル存在確認: `if os.path.exists(file_path):`

### 正規表現の結果処理

- **`re.split()`の結果から空文字列を除外**
  - 例: `sentences = [s for s in re.split(r'[。！？]', text) if s.strip()]`
  - 空リスト対策: `response = sentences[0] if sentences else fallback_text`

### コード品質の基本ルール

- **未使用の変数・importは削除すること**
  - コミット前にリンター（flake8/pylint）を実行して確認
  - IDE/エディタの警告にも注意

- **変数名は明確に**
  - 目的が分かる名前を使用（例: `query_lower`は小文字変換されたクエリと分かる）
  - 略語は慣例的なもののみ使用

- **コメントは必要に応じて追加**
  - 複雑なロジックには説明コメントを追加（日本語推奨）
  - 自明なコードには不要
  - 既存のコメントスタイルに合わせる

### 推奨ツール（リンター・フォーマッター）

- **flake8**: Pythonコードの静的解析
- **pylint**: より詳細なコード品質チェック
- **autoflake**: 未使用importの自動削除
- **isort**: import文の自動整形
- **black**: コードの自動フォーマット

> **重要**: `.pre-commit-config.yaml` の `rev` と `requirements.txt` の `black` バージョンは常に同じバージョンに統一すること。バージョンが異なるとローカルの pre-commit とCIのフォーマット結果が食い違いCI失敗の原因になる。

使用方法:

```bash
# インストール
pip install flake8 pylint autoflake isort black

# 実行
flake8 src/
pylint src/
autoflake --remove-all-unused-imports --in-place src/*.py
isort src/
black src/
```

### pre-commit フックのセットアップ（必須）

**GitHub Copilot エージェント（sandbox 環境）を含む、すべての開発セッション開始時に必ず以下を実行すること。**

```bash
pip install pre-commit
pre-commit install
```

> **重要**: `pre-commit install` を実行しないと `git commit` 時に lint が自動実行されない。
> sandbox 環境でも `pip install pre-commit && pre-commit install` を実行することでフックをインストールできる。
> `report_progress` ツール経由のコミットにはフックが動作しない場合があるため、コミット前に必ず手動で lint を実行すること。

### チェックリスト

コード作成・変更時は以下を確認：

- [ ] セッション開始時に `pip install pre-commit && pre-commit install` を実行したか
- [ ] リスト・配列アクセス前に空チェックを実施したか
- [ ] `random.choice()`等の関数使用前にチェックしたか
- [ ] ファイル・ディレクトリ操作前に存在確認・作成したか
- [ ] 正規表現の結果処理で空文字列を考慮したか
- [ ] 未使用の変数・importを削除したか
- [ ] 変数名は明確か
- [ ] 必要なコメントを追加したか
- [ ] コミット前に `black`・`isort`・`flake8` を手動実行してエラーがないか確認したか
