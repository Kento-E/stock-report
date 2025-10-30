# 自動化・CI/CD機能仕様書

> **Note**: このファイルは自動化、CI/CD、テスト機能の仕様を定義します。

## スケジューラ・自動実行

### GitHub Actions による日次実行

- GitHub Actions 等の CI/CD で日次自動実行が可能。
- 実行時刻は JST（日本標準時）で平日（月曜日～金曜日）の午前 9 時 10 分。
- 土日は株式市場が休みのため実行しない。

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

## 自動マージ機能

### PR自動承認・マージ

- GitHub Copilot が作成した Pull Request を承認（Approve）すると、自動的にマージされる。
- GitHub Actions の `pull_request_review` イベントをトリガーとして実行。

### マージ方式

- マージ方式はスカッシュマージ（Squash Merge）を採用し、コミット履歴を整理。
- マージ後、自動的にブランチを削除してリポジトリを整理。

**詳細な動作確認手順は <a>.github/instructions/testing.instructions.md</a> を参照してください。**

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
