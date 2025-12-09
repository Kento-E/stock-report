# stock-report

株式銘柄の動向をAI（Claude Sonnet / Gemini）で自動分析し、HTML形式のレポートを生成・メール配信するシステムです。

> **開発者向け情報**: 詳細な技術仕様・要件定義は <a>requirements.instructions.md</a> を参照してください。

## 特徴

- 🤖 **AI分析**: Claude SonnetまたはGemini APIによる株価・ニュース分析
- 📊 **自動レポート生成**: HTML形式の見やすいレポート
- 📧 **メール配信**: 複数宛先へのBCC送信
- 📑 **分類別レポート**: 保有銘柄、空売り銘柄、購入検討中の銘柄を自動分類してメール配信
- ⏰ **自動実行**: GitHub Actionsによる週2回（火曜日・木曜日）の自動実行
- 🔧 **モジュール設計**: 保守性・拡張性の高い構造

## システム構成

本プロジェクトは機能別にモジュール化されており、各モジュールが単一の責任を持つ設計になっています。

詳細なモジュール構成とシステムアーキテクチャについては、<a>requirements.instructions.md</a> を参照してください。

## Github Actions用 Secrets and variables 設定方法

本プロジェクトの自動実行・メール配信には、GithubリポジトリのWeb画面から以下の「Secrets and variables」の登録が必要です。

### 必須Secrets（リポジトリ設定 > Settings > Secrets and variables > Actions）

| Secret名         | 用途                         | 例・備考           |
| ---------------- | ---------------------------- | ------------------ |
| `CLAUDE_API_KEY` | Claude Sonnet APIキー        |                    |
| `GEMINI_API_KEY` | GEMINI APIキー               |                    |
| `MAIL_TO`        | レポート送信先メールアドレス |                    |
| `MAIL_FROM`      | 送信元メールアドレス         |                    |
| `SMTP_SERVER`    | SMTPサーバー                 | 例: smtp.gmail.com |
| `SMTP_PORT`      | SMTPポート                   | 通常587            |
| `SMTP_USER`      | SMTP認証ユーザー             |                    |
| `SMTP_PASS`      | SMTP認証パスワード           |                    |
| `YAHOO_API_KEY`  | Yahoo Finance APIキー        |                    |

> これらは「Repository secrets」として登録してください。値は外部に公開されません。

### Variables（リポジトリ設定 > Settings > Secrets and variables > Actions > Variables）

| Variable名               | 用途                           | 設定値             |
| ------------------------ | ------------------------------ | ------------------ |
| `SIMPLIFY_HOLD_REPORTS`  | ホールド判断時のレポート簡略化 | `true` または `false` |

> これらは「Repository variables」として登録してください。デフォルト値は`true`です。

### オプション設定

#### レポート簡略化オプション

`SIMPLIFY_HOLD_REPORTS` を設定することで、AI分析の売買判断が「ホールド」の場合にレポートを簡略化できます。

- **`true` (デフォルト)**: ホールド判断時は銘柄名、現在価格、ホールド理由の要約のみ表示
- **`false`**: ホールド判断でも詳細な分析レポートを表示

メール本文が長すぎて読みづらい場合は、この機能により読みやすさが向上します。

## 投資志向性の設定

ユーザーの投資に対する志向性（投資スタイル、リスク許容度、投資期間など）を設定し、AI分析の視点を調整できます。

`data/investment_preferences.yaml` ファイルを編集することで、個人の投資方針に合わせた分析結果を得られます。

**詳細な設定方法**: [data/README.md](data/README.md#投資志向性設定-investment_preferencesyaml) を参照してください。

## 銘柄リストの管理

分析対象の銘柄リストは、リポジトリ内の `data/stocks.yaml` ファイルで管理します。

> **詳細な編集ガイド**: [data/README.md](data/README.md) に、フィールドの詳細説明や編集方法の詳細を記載しています。

### 銘柄リストファイルの編集方法

1. GitHub上で `data/stocks.yaml` ファイルを開く
2. 編集ボタン（鉛筆アイコン）をクリック
3. 銘柄を追加・削除・編集
4. 変更をコミット

スマートフォンのブラウザからも同様の手順で編集できます。

### 銘柄リストの書式

YAML形式で記述します。詳細なフィールド仕様や記述例については [data/README.md](data/README.md) を参照してください。

**主な機能:**
- 保有情報（`quantity`、`acquisition_price`）を設定すると、AIが保有状況を考慮した売買判断を提供
- 銘柄は保有状況に応じて自動分類され、メール本文でセクション分けして表示
- 日本株・米国株など複数の市場と通貨に対応
- **自動バリデーション**: Pull RequestやPush時に自動的にファイル形式を検証

#### stocks.yamlバリデーション機能

`data/stocks.yaml` ファイルの形式は自動的に検証されます。以下の場合に自動バリデーションが実行されます：

- `data/` フォルダ内のファイルを変更してPull Requestを作成した時
- `main` ブランチに `data/` フォルダ内のファイルをPushした時

**検証項目:**
- YAML構文の正確性
- 必須フィールド（`symbol`）の存在
- フィールドの型チェック（`quantity`、`acquisition_price`は数値など）
- 値の範囲チェック（`acquisition_price`は正の数など）
- `account_type`の有効値チェック（'特定'、'NISA'、'旧NISA'）
- `considering_action`の有効値チェック（'buy'、'short_sell'）

**手動でバリデーションを実行する場合:**

```bash
python src/validate_stocks.py data/stocks.yaml
```

バリデーションが失敗した場合、詳細なエラーメッセージが表示されます。

#### YAML自動フォーマット機能

`data/` ディレクトリ以下のYAMLファイルは、自動的にフォーマットされます。スマートフォンから編集した際のインデントのズレも自動修正されます。

**自動フォーマット実行タイミング:**
- Pull Request作成時
- `main` ブランチへのPush時

**フォーマット内容:**
- インデントを2スペースに統一
- 余分な空白を削除
- コメントと引用符は保持

**手動でフォーマットを実行する場合:**

```bash
# フォーマットを実行
python src/format_yaml.py data/stocks.yaml

# フォーマットが必要かチェックのみ（ファイルは変更しない）
python src/format_yaml.py data/stocks.yaml --check
```

フォーマットが実行されると、GitHub Actionsが自動的に変更をコミットします。

#### Claude Sonnet APIキー発行手順

1. [Anthropic Developer Platform](https://console.anthropic.com)にアクセスし、アカウントを作成します。
2. ログイン後、ダッシュボードまたはAPI管理画面に移動します。
3. 「[API Keys](https://console.anthropic.com/settings/keys)」から新規APIキーを発行します。
4. 発行されたAPIキーを控え、Githubリポジトリの「Secrets and variables」に `CLAUDE_API_KEY` として登録してください。

#### Gemini APIキー発行手順

1. [Gemini APIキーを取得する](https://aistudio.google.com/apikey?hl=ja)アクセスする。
2. "Get API key" > "APIキーを作成"を選択する。

※API利用には有料プランや申請が必要な場合があります。詳細はAnthropic公式の案内をご確認ください。

#### Yahoo Finance APIキー発行手順

[YH Finance API](https://financeapi.net/dashboard) でAPIキーを取得。

## 銘柄リストの管理について

本プロジェクトでは、分析対象の銘柄リストをリポジトリ内の `data/stocks.yaml` ファイル（YAML形式）で管理しています。これにより、以下のメリットがあります：

- **変更履歴の管理**: Gitで銘柄の追加・削除履歴を追跡できます
- **編集の容易さ**: スマートフォンのブラウザからも簡単に編集できます
- **構造化されたデータ**: 企業名、追加日、メモなどを銘柄ごとに整理して記録できます
- **拡張性**: 将来的に銘柄ごとの設定（アラート閾値、分析頻度など）を追加しやすい

詳しい編集方法は上記「銘柄リストの管理」セクションを参照してください。

### 追加設定（必要に応じて）

- YAML形式により、銘柄ごとに追加のメタデータを柔軟に管理できます
- その他の分析条件を変数として管理したい場合は、環境変数や設定ファイルに追加可能です

## テスト

本プロジェクトには自動テストが実装されており、コードの品質を保証しています。

### テストの実行方法

ローカル環境でテストを実行する場合：

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# すべてのテストを実行
python -m pytest tests/ -v

# カバレッジレポート付きで実行
python -m pytest tests/ -v --cov=src --cov-report=html
```

### テストの種類

- **ユニットテスト**: 各モジュールの個別機能をテスト
  - `test_stock_loader.py`: 銘柄リスト読み込み、通貨判定
  - `test_validate_stocks.py`: stocks.yamlのバリデーション
  - `test_data_fetcher.py`: データ構造の検証
  - `test_report_generator.py`: HTMLレポート生成
  - `test_mail_utils.py`: メール本文生成、マークダウン変換
  - `test_ai_analyzer.py`: 保有状況プロンプト生成、損益計算

### 自動テスト実行

Pull Requestを作成すると、GitHub Actionsで自動的にテストが実行されます：

- テスト結果はPRの「Checks」タブで確認できます
- テストが失敗した場合、マージ前に修正が必要です
- カバレッジレポートはアーティファクトとしてダウンロード可能です

## コード品質管理

本プロジェクトでは、pre-commitフックとリンターツールを導入してコード品質を自動化しています。

### 初回セットアップ

```bash
pip install -r requirements.txt
pre-commit install
```

コミット時に自動的にコードフォーマット・リントチェックが実行されます。詳細な技術仕様は [automation-cicd.md](.github/specs/automation-cicd.md#コード品質自動チェック) を参照してください。

## GitHub Copilotの活用

本リポジトリではGitHub Copilotを活用できます：

- **Issueテンプレート**: Issue作成時、「GitHub Copilotへの質問」フィールドに自動的に `@copilot` メンションの例が挿入されます。このフィールドを使用することで、Issue作成と同時にGitHub Copilotに質問できます。デフォルトでは、Copilotに修正とPull Request作成まで依頼する内容になっています。また、Issue作成時に自動的にCopilotがAssigneeとして設定されます。
- **Copilotへの質問**: Issueのコメント欄で `@copilot` とメンションすることで、GitHub Copilotに質問や分析を依頼できます。分析だけでなく、修正とPull Request作成まで自動で依頼することも可能です。
- **コードレビュー**: Pull Requestでは、CODEOWNERSファイルにより `@copilot` が自動的にレビュアーとして設定されます。
- **カスタムチャットモード**: VS Codeで `@kansai` とメンションすることで、関西弁で応答するフレンドリーなCopilotチャットモードを使用できます。詳細は `.github/copilot-chat-participants.md` を参照してください。
- **Copilot Instructions**: GitHub Copilot コーディングエージェント向けの詳細な指示は `.github/copilot-instructions.md` にまとめられています。要件定義、コーディング規約、テスト手順などの詳細な指示ファイルへのリンクが含まれています。
- **効率的な利用**: GitHub Copilot Premium の消費を節約するため、テスト自動化の活用や実用性重視のドキュメント方針など、効率的な作業方針を定めています。詳細は `.github/instructions/copilot.instructions.md` を参照してください。

### Pull Request 自動マージ機能

本リポジトリには、Pull Request を承認（Approve）すると自動的にマージする機能が実装されています。

#### 動作仕様

- Pull Request が承認されると、`.github/workflows/auto-merge.yml` ワークフローが自動実行されます。
- マージ方式は **スカッシュマージ（Squash Merge）** を採用し、複数のコミットを1つにまとめます。
- マージ後、ブランチは自動的に削除されます。

#### 必要な権限設定

この機能を使用するには、以下の設定が必要です：

1. **Settings > Actions > General > Workflow permissions** で以下を設定：
   - 「Read and write permissions」を選択
   - 「Allow GitHub Actions to create and approve pull requests」にチェック

2. リポジトリの設定で、GitHub Actions に必要な権限が付与されていることを確認してください。

#### 注意事項

- マージ可能な状態（競合がない、必要なチェックが通過しているなど）でなければ、自動マージは実行されません。
- **Draft状態のPRは自動マージされません。** Draft状態のPRを承認した場合、その旨が表示されますが、ワークフローはエラーにならず正常終了します。Ready for reviewに変更してから再度Approveしてください。
- 承認後、手動でマージボタンを押す必要はありません。
- 詳細な動作確認手順は `.github/instructions/testing.instructions.md` を参照してください。

## 参考

- [Github公式: Secrets and variables](https://docs.github.com/ja/actions/security-guides/encrypted-secrets)
- [Github公式: Actionsの設定](https://docs.github.com/ja/actions/using-workflows/workflow-syntax-for-github-actions)

---

ご不明点は `.github/outputs/questions.md` へ追記してください。
