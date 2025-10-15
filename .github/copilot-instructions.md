# GitHub Copilot Instructions

このリポジトリで GitHub Copilot を使用する際の指示事項です。

## リポジトリ概要

株式銘柄の動向をAI（Claude Sonnet / Gemini）で自動分析し、HTML形式のレポートを生成・メール配信するPythonシステムです。

## 主要な技術スタック

- **言語**: Python 3.x
- **AI API**: Claude Sonnet API, Gemini API
- **データ取得**: Yahoo Finance API (RapidAPI), defeatbeta-api
- **自動化**: GitHub Actions
- **テスト**: pytest, pytest-cov

## プロジェクト構成

```
.
├── src/                    # ソースコード
│   ├── main.py            # メインエントリーポイント
│   ├── config.py          # 設定管理
│   ├── stock_loader.py    # 銘柄リスト読み込み
│   ├── data_fetcher.py    # データ取得
│   ├── ai_analyzer.py     # AI分析
│   ├── report_generator.py # レポート生成
│   └── mail_utils.py      # メール送信
├── data/
│   └── stocks.yaml        # 銘柄リスト（YAML形式）
├── tests/                 # テストコード
├── .github/
│   ├── instructions/      # 詳細な指示ファイル
│   └── workflows/         # GitHub Actions ワークフロー
└── docs/                  # ドキュメント
```

## 重要な指示ファイル

このリポジトリには、以下の詳細な指示ファイルが `.github/instructions/` ディレクトリに配置されています。コードを変更する前に、必ず該当する指示ファイルを確認してください。

### 1. [requirements.instructions.md](instructions/requirements.instructions.md)

**システムの要件定義書** - 最も重要なドキュメント

- システム概要と目的
- 機能要件（データ収集、AI分析、レポート生成、メール配信）
- 非機能要件（セキュリティ、パフォーマンス、拡張性）
- モジュール構成と依存関係
- 銘柄リスト管理（YAML形式）
- 売買タイミング分析機能

**いつ参照すべきか**: 機能追加、仕様変更、システム理解が必要な時

### 2. [copilot.instructions.md](instructions/copilot.instructions.md)

**GitHub Copilot 使用時の指示事項**

- 言語設定（日本語必須）
- Markdown ルール（MD001, MD022, MD025, MD032, MD047）
- コーディング規約
- ドキュメント・要件定義書の反映ルール
- GitHub Copilot Premium の効率的な利用方針

**いつ参照すべきか**: Pull Request作成、ドキュメント作成、コード変更時

### 3. [coding.instructions.md](instructions/coding.instructions.md)

**コーディングガイドライン**

- Markdown Lint ルール
- コードスタイル規約

**いつ参照すべきか**: Markdownファイル編集時

### 4. [testing.instructions.md](instructions/testing.instructions.md)

**テスト・動作確認手順**

- GitHub Actions による自動実行テスト
- エラー発生時の確認方法
- 自動マージ機能の動作確認

**いつ参照すべきか**: テスト実行、ワークフロー確認時

## 作業時の基本方針

### コード変更時

1. **最小限の変更**: 必要最小限のコード変更を心がける
2. **既存コードの尊重**: 動作しているコードは削除・変更しない
3. **テスト自動化の活用**: Pull Request作成時に自動テストが実行される
4. **要件定義書の更新**: コード変更時は requirements.instructions.md も更新

### ドキュメント作成時

1. **日本語必須**: すべての出力は日本語で記述
2. **Markdown Lint準拠**: 見出し階層、空行、ファイル末尾の改行ルールを遵守
3. **既存ドキュメント優先**: README.md、docs/TEST.md などを優先的に更新
4. **実用性重視**: 実際に使用されるドキュメントのみ作成

### Pull Request作成時

1. **タイトル・説明を日本語で記述**
2. **チェックリスト形式で進捗を報告**
3. **自動テストの結果を確認**
4. **CODEOWNERSにより @copilot が自動的にレビュアーに設定される**

## VS Code カスタムチャットモード

VS Code で GitHub Copilot を使用する際、カスタムチャット参加者を利用できます。

詳細は [copilot-chat-participants.md](copilot-chat-participants.md) を参照してください。

### 利用可能なカスタムチャット

- **@kansai**: 関西弁で応答するフレンドリーなプログラミングアシスタント

## 環境変数とSecrets

本番環境（GitHub Actions）では、以下のSecretsが設定されています：

- `CLAUDE_API_KEY` または `GEMINI_API_KEY`: AI分析用
- `YAHOO_API_KEY`: 株価データ取得用
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: メール送信用
- `MAIL_FROM`, `MAIL_TO`: メールアドレス

詳細は [README.md](../README.md) の「Github Actions用 Secrets and variables 設定方法」を参照してください。

## 参考リンク

- [README.md](../README.md): ユーザー向け使用方法・セットアップ手順
- [docs/TEST.md](../docs/TEST.md): ユニットテストの実行方法
- [docs/MODULE_REFERENCE.md](../docs/MODULE_REFERENCE.md): モジュール分割リファレンス
