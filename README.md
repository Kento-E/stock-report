# stock-report

株式銘柄の動向をAI（Claude Sonnet / Gemini）で自動分析し、HTML形式のレポートを生成・メール配信するシステムです。

> **開発者向け情報**: 詳細な技術仕様・要件定義は [requirements.instructions.md](.github/instructions/requirements.instructions.md) を参照してください。

## 特徴

- 🤖 **AI分析**: Claude SonnetまたはGemini APIによる株価・ニュース分析
- 📊 **自動レポート生成**: HTML形式の見やすいレポート
- 📧 **メール配信**: 複数宛先へのBCC送信
- 📑 **分類別レポート**: 保有銘柄、空売り銘柄、購入検討中の銘柄を自動分類してメール配信
- ⏰ **自動実行**: GitHub Actionsによる日次実行
- 🔧 **モジュール設計**: 保守性・拡張性の高い構造

## システム構成

本プロジェクトは機能別にモジュール化されており、各モジュールが単一の責任を持つ設計になっています。

```
src/
├── config.py              # 環境変数と設定管理
├── stock_loader.py        # YAML銘柄リスト読み込み・分類
├── data_fetcher.py        # 株価・ニュースデータ取得
├── ai_analyzer.py         # AI分析（Claude/Gemini）
├── report_generator.py    # HTMLレポート生成
├── mail_utils.py          # メール配信・分類別本文生成
└── main.py                # メインエントリーポイント
```

詳細は以下のドキュメントを参照してください：
- [モジュール分割リファレンス](docs/MODULE_REFERENCE.md)

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

## 銘柄リストの管理

分析対象の銘柄リストは、リポジトリ内の `data/stocks.yaml` ファイルで管理します。

### 銘柄リストファイルの編集方法

1. GitHub上で `data/stocks.yaml` ファイルを開く
2. 編集ボタン（鉛筆アイコン）をクリック
3. 銘柄を追加・削除・編集
4. 変更をコミット

スマートフォンのブラウザからも同様の手順で編集できます。

### 銘柄リストの書式（YAML形式）

```yaml
# 銘柄リスト
stocks:
  - symbol: 7203.T
    name: トヨタ自動車
    added: 2024-01-01
    note: 自動車メーカー最大手
    quantity: 100
    acquisition_price: 2500
  
  - symbol: 6758.T
    name: ソニーグループ
    added: 2024-01-01
    quantity: -50
    acquisition_price: 12000
    note: 空売りポジション
  
  - symbol: AAPL
    name: Apple Inc.
    added: 2024-01-15
    # 保有数未設定（購入検討中）
```

**フィールド説明:**
- `symbol` (必須): 銘柄コード
- `name` (任意): 企業名
- `added` (任意): 追加日
- `note` (任意): メモ・注記
- `quantity` (任意): 保有数（プラスは保有、マイナスは空売り、未設定は購入検討中）
- `acquisition_price` (任意): 取得単価（購入価格または空売り価格）

**保有情報の活用:**
- `quantity`を設定すると、AIが保有状況を考慮した売買判断を提供します
- 正の数（例: 100）: 保有中の銘柄として、売却タイミングや追加購入の判断を提供
- 負の数（例: -50）: 空売り中（信用売り）として、買戻しタイミングの判断を提供
- 未設定: 購入または空売りを検討中として、新規エントリーのタイミングを提供
- `acquisition_price`を併せて設定すると、損益計算と具体的な指値価格の提案を受けられます

**メール分類:**
- 銘柄は自動的に以下の3つのカテゴリーに分類されます：
  - **保有銘柄**: `quantity > 0` の銘柄
  - **空売り銘柄**: `quantity < 0` の銘柄
  - **購入検討中の銘柄**: `quantity` 未設定または `0` の銘柄
- メール本文では各カテゴリーごとにセクション分けされ、読みやすく整理されます

**特徴:**
- 日本株（.T、.JPサフィックス）と米国株の両方に対応
- YAMLのコメント機能（`#`で始まる行）を使用可能
- 構造化されたデータで銘柄ごとに複数の情報を管理可能
- 読みやすく、編集しやすい形式

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
  - `test_data_fetcher.py`: データ構造の検証
  - `test_report_generator.py`: HTMLレポート生成
  - `test_mail_utils.py`: メール本文生成、マークダウン変換
  - `test_ai_analyzer.py`: 保有状況プロンプト生成、損益計算

### 自動テスト実行

Pull Requestを作成すると、GitHub Actionsで自動的にテストが実行されます：

- テスト結果はPRの「Checks」タブで確認できます
- テストが失敗した場合、マージ前に修正が必要です
- カバレッジレポートはアーティファクトとしてダウンロード可能です

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
