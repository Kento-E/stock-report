# 自動化・CI/CD機能仕様書

> **Note**: このファイルは自動化、CI/CD、テスト機能の仕様を定義します。

## 依存関係の自動更新

### Dependabot による自動更新

- Dependabot が依存関係を自動的に監視し、更新が利用可能になると Pull Request を自動作成。
- Python パッケージ（requirements.txt）と GitHub Actions ワークフローの両方を監視。

#### 更新スケジュール

- **実行タイミング**: 毎週土曜日午前9時（JST）
- **理由**: 平日はstock-reportが稼働するため、土曜日に更新して平日の稼働に影響を与えない
- **Python依存関係**: 最大10件のPRを同時にオープン
- **GitHub Actions**: 最大5件のPRを同時にオープン

#### ラベルとレビュアー

- 自動的に `dependencies` ラベルが付与される
- Python更新には `python` ラベル、GitHub Actions更新には `github-actions` ラベルが追加
- PRレビュアーとしてリポジトリオーナーが自動割り当て

#### セキュリティアップデート

- セキュリティ脆弱性が検出された場合、優先的に更新PRが作成される
- 手動でのバージョン管理作業を削減し、常に最新の安全な依存関係を維持

#### 自動承認とマージ

- **自動承認とマージ**: Dependabotが作成したPRは GitHub Actions により自動的に承認され、マージも自動設定される
- **ワークフロー**: `.github/workflows/dependabot-auto-approve.yml`が承認とマージ設定を同時に実行
- **マージ方式**: 必須チェック完了後にスカッシュマージを自動実行し、ブランチを自動削除
- **安全性**: `pull_request_target`イベントを使用し、Dependabotのメタデータを検証
- **実装理由**: `GITHUB_TOKEN`を使った承認では`pull_request_review`イベントがトリガーされないため、承認とマージ設定を同一ワークフローで実行

**設定ファイル**:
- `.github/dependabot.yml` - Dependabot設定
- `.github/workflows/dependabot-auto-approve.yml` - 自動承認ワークフロー

## スケジューラ・自動実行

### 定期実行の状態

現在、レポートの定期実行は**停止中**です。APIの無料枠減少に伴うモデル変更検討のため、一時的に稼働を停止しています。

### 手動実行

GitHub Actions の「workflow_dispatch」トリガーにより、手動での実行が可能です：

- GitHub リポジトリの「Actions」タブから「Stock Report」ワークフローを選択
- 「Run workflow」ボタンをクリックして実行

### 定期実行の再開方法

`.github/workflows/report.yml` の `schedule` セクションのコメントを解除することで、定期実行を再開できます：

```yaml
on:
  schedule:
    - cron: "0 0 * * 2,4"  # 火曜日と木曜日の00:00 UTC（JST 09:00）に実行
  workflow_dispatch:
```

### 定期実行の仕様（再開時）

- GitHub Actions 等の CI/CD で週2回（火曜日・木曜日）の自動実行を実施。
- 実行時刻は JST（日本標準時）で午前 9 時（UTC 0:00）。
- 土日・祝日は株式市場が休みのため実行しない。

### Gemini API レート制限対策

- **レート制限**: Gemini API 無料枠は 10 リクエスト/分（RPM）の制限があります。
- **実装**: `src/main.py`にレート制限機能を実装し、各API呼び出し間に6.5秒の待機時間を確保。
- **並列処理の制御**: スレッドセーフなロック機構により、複数スレッドからの同時API呼び出しを防止。
- **対象**: Gemini APIのみに適用（Claude APIは対象外）。

この機能により、71銘柄の分析でも確実に10 RPM制限内に収まり、`RESOURCE_EXHAUSTED`エラーを回避します。

### セキュリティ管理

- .env や Secrets で安全に API キー・認証情報を管理。
- Claude Sonnet API キーやメール配信設定等の機密情報は、GitHub リポジトリの「Secrets」で安全に管理する。

**環境変数とSecrets設定の詳細は <a>README.md</a> を参照してください。**

## テスト自動化

### pytest によるユニットテスト

- pytest を使用したユニットテストの実装により、コードの品質を保証。
- Pull Request 作成時・プッシュ時に GitHub Actions で自動的にテストを実行。

### テストカバレッジ

- テストカバレッジレポートの生成とアーティファクト保存。
- CI/CD パイプラインでテストが失敗した場合、マージをブロック。

### テスト対象モジュール

- stock_loader（銘柄リスト読み込み、多通貨対応の通貨判定、銘柄分類、口座種別管理、課税計算）
- preference_loader（投資志向性設定読み込み、バリデーション、プロンプト生成）
- data_fetcher（データ構造検証）
- report_generator（HTMLレポート生成）
- mail_utils（メール本文生成、分類別メール本文生成、マークダウン変換）
- ai_analyzer（保有状況プロンプト生成、多通貨対応の損益計算、口座種別を考慮した税引後損益計算）
- validate_stocks（stocks.yamlのバリデーション）
- format_yaml（YAMLファイルの自動フォーマット、コメント保持、インデント修正）

**詳細なテスト実行方法は <a>docs/TEST.md</a> を参照してください。**

## コード品質自動チェック

### 概要

コミット時に自動的にコード品質チェックが実行される仕組みを導入。開発者は `pre-commit install` を実行することで、ローカル環境でコード品質を保証。

### セットアップ手順

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# pre-commitフックのインストール
pre-commit install

# 全ファイルに対して手動実行する場合
pre-commit run --all-files
```

### チェック項目

#### Python

- **Black**: Pythonコードフォーマッター（行長100文字）
- **isort**: importの自動整理（Blackプロファイル準拠）
- **Flake8**: コード品質リンター（PEP 8準拠、一部ルール除外）

#### Markdown

- **markdownlint**: Markdown形式のリントチェック
- プロジェクト規約に準拠したMarkdownファイルの品質保証

#### 基本チェック

- 行末の空白削除
- ファイル末尾の改行修正
- YAML/JSON構文チェック
- 改行コードの統一（LF）
- マージコンフリクトの検出
- 大きなファイル（1MB以上）の検出

#### セキュリティ

- 秘密鍵の検出
- AWS認証情報の検出

### 設定ファイル

| ファイル | 用途 |
|---------|------|
| `.pre-commit-config.yaml` | pre-commitフックの設定（使用するツールとバージョン） |
| `.flake8` | Flake8の設定（行長100、除外ルール：E203,W503,E402,F401,F841,F541,E501） |
| `.markdownlint.json` | Markdownリントルール（MD001,MD025,MD047など） |
| `pyproject.toml` | BlackとisortのPEP 518準拠設定 |

### CI/CDでの自動実行

- **トリガー**: Pull Request作成時・同期時、mainブランチへのpush時
- **ワークフロー**: `.github/workflows/lint.yml`
- **動作**: pre-commit run --all-files を実行
- **失敗時**: チェック失敗時はマージをブロックし、コード品質を保証
- **最適化**: pip cacheを活用して実行時間を短縮

## 自動マージ機能

### PR自動承認・マージ

- GitHub Copilot が作成した Pull Request を承認（Approve）すると、自動的にマージされる。
- GitHub Actions の `pull_request_review` イベントをトリガーとして実行。

### マージ済みPRの処理

- PRが既に手動でマージされている場合、自動マージ処理をスキップして正常終了する。
- コードオーナーが作成したPRを手動でマージした場合でも、エラーは発生しない。

### マージ方式

- マージ方式はスカッシュマージ（Squash Merge）を採用し、コミット履歴を整理。
- マージ後、自動的にブランチを削除してリポジトリを整理。

**詳細な動作確認手順は <a>.github/instructions/testing.instructions.md</a> を参照してください。**

## PR自動更新機能

### 他のPRの自動更新

- mainブランチにマージされた際、他のオープンなPRを自動的に更新する。
- GitHub Actions の `pull_request` (closed) と `push` (main) イベントをトリガーとして実行。

### 更新プロセス

1. **対象PRの検索**: 同じベースブランチ（main）を対象とする全てのオープンなPRを検索
2. **コンフリクトチェック**: マージ可能性を確認し、コンフリクトがある場合はスキップ
3. **ブランチ更新**: GitHub APIの `update-branch` エンドポイントを使用してブランチを更新
4. **リントチェック**: 更新後のブランチに対して変更ファイルのみpre-commitチェックを実行
5. **エラー通知**: リントエラーが検出された場合、PRにコメントで通知

### リントチェック統合

- ブランチ更新後、自動的にpre-commitによる**変更ファイルのみ**のリントチェックを実行。
- `git diff --name-only origin/main...HEAD`で差分ファイルを抽出し、効率的にチェック。
- マージで取り込まれたファイルに行末空白などの問題がある場合でも即座に検出。
- エラー検出時はPRに警告コメントを自動追加し、開発者に修正を促す。
- 変更ファイルがない場合はチェックをスキップし、処理を高速化。

### エラーハンドリング

- コンフリクトがある場合: 更新をスキップし、手動解決を促す
- 既に最新の場合: 成功として扱う
- リントエラー: PRにコメントで通知するが、更新自体は成功として扱う

**ワークフローファイル**: `.github/workflows/update-other-prs.yml`

## バリデーション自動実行

### stocks.yamlバリデーション

- `data/stocks.yaml` ファイルの形式を自動的に検証し、不正なデータの混入を防止。
- GitHub Actions により、dataフォルダ内のファイルが更新されるたびに自動実行。

#### 検証項目

- YAML構文の正確性
- 必須フィールド（`symbol`）の存在確認
- `symbol`フィールドは文字列または数値（整数）を許可
- フィールドの型チェック（`quantity`、`acquisition_price`は数値、など）
- 値の範囲チェック（`acquisition_price`は正の数、など）
- `account_type`の有効値チェック（'特定'、'NISA'、'旧NISA'）
- `considering_action`の有効値チェック（'buy'、'short_sell'）
- 後方互換性（文字列形式の銘柄リストもサポート）

#### エラー処理

- バリデーションエラー時は詳細なエラーメッセージを表示し、問題箇所を明示。
- Pull Request作成時にバリデーションが失敗した場合、マージをブロック。

### 投資志向性設定バリデーション

- `data/investment_preferences.yaml` ファイルの形式を自動的に検証。
- GitHub Actions により、設定ファイル更新時に自動でバリデーションを実行。
- バリデーション機能により、設定ファイルの形式を自動検証。

## YAML自動フォーマット

### フォーマット機能

- `data/` ディレクトリ以下のYAMLファイルを自動的にフォーマットし、インデントのズレを修正。
- スマートフォンから編集した際のインデント不整合を自動で修正。

### 実行タイミング

- GitHub Actions により、Pull RequestおよびMainブランチへのPush時に自動実行。

### フォーマット方式

- `ruamel.yaml`ライブラリを使用し、コメントと引用符を保持したままフォーマット。
- フォーマット対象：`data/` ディレクトリ内の `.yaml`, `.yml` ファイル

## ファイアウォール対策

GitHub Copilotがワークフロー内でpytestなどのコマンドを実行する際、ファイアウォールルールによって外部ネットワークへのアクセスが制限されます。本システムでは、`.github/actions/setup-python-env`という再利用可能なComposite Actionを使用して、以下の対策を実施しています：

### 事前ダウンロード処理

- **NLTKデータの事前ダウンロード**：defeatbeta-apiが依存するnltkパッケージのデータをファイアウォール有効化前にダウンロード
- **defeatbeta-apiデータの事前ダウンロード**：huggingface.coからの株式データ情報を事前取得

### キャッシュ機能

- **キャッシュ機能の活用**：2回目以降のワークフロー実行を高速化

### 適用範囲

このアクションは複数のワークフロー（test.yml、report.yml、copilot-setup-steps.yml）から参照されており、メンテナンス性が向上しています。

**詳細な実装内容・使用方法・トラブルシューティングについては、<a>.github/actions/setup-python-env/README.md</a>を参照してください。**

## カスタムチャットモード

### VS Code GitHub Copilot 拡張

- VS Code の GitHub Copilot で使用可能なカスタムチャット参加者（Custom Chat Participant）を定義。
- `.github/copilot-instructions.md` ファイルでカスタムチャットモードを設定。

### @kansai チャット参加者

- `@kansai` とメンションすることで、関西弁で応答するフレンドリーなプログラミングアシスタントを利用可能。
- コードの質問や相談に対して、関西弁でわかりやすく親しみやすい回答を提供。
- 技術的な正確性を保ちつつ、「せやな」「ほんまに」「ええで」などの関西弁特有の表現を使用。

## GitHub Copilot Premium の効率的な利用

### 消費削減戦略

- GitHub Copilot への明確な指示により、不要な処理を抑制し、Premium消費を節約。
- テスト自動化（pytest + GitHub Actions）の活用により、手動テスト実施を最小化。
- 既存ドキュメントの優先的な更新により、実用性の低いドキュメントファイルの作成を回避。

### ドキュメント管理

- 要件定義書の更新は必須としつつ、その他のドキュメント作成は実用性が明確な場合のみ実施。
- 最小限の変更と既存コードの再利用により、作業効率を最大化。

### 自動化活用

- 自動化ワークフロー（テスト、ビルド、デプロイ、自動マージ、YAML自動フォーマット）の活用により、手動作業を削減。
