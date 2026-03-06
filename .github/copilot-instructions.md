# GitHub Copilot Instructions

このリポジトリで GitHub Copilot を使用する際の指示事項です。

## はじめに

このリポジトリは、株式銘柄の動向をAIで自動分析し、レポートを生成・配信するPythonシステムです。

詳細な情報は以下のドキュメントを参照してください：

- **システム概要・技術スタック**: <a>README.md</a>
- **要件定義と仕様書**: <a>specs/requirements-index.md</a>（エントリーポイント）

## 重要な指示ファイル

### 1. <a>specs/requirements-index.md</a>

**要件定義インデックス** - 最も重要なドキュメント

全仕様書のエントリーポイント。システム概要、クイックリファレンス、各機能別仕様書へのリンクを提供。

**いつ参照すべきか**: システム全体の理解が必要な時、機能別仕様書を探す時

### 2. <a>instructions/copilot.instructions.md</a>

**GitHub Copilot 使用時の指示事項**

言語設定、Markdownルール、コーディング規約、ドキュメント更新ルール、効率的な利用方針を定義しています。

**いつ参照すべきか**: Pull Request作成、ドキュメント作成、コード変更時

### 3. <a>instructions/coding.instructions.md</a>

**コーディングガイドライン**

Markdown Lintルール、Pythonコードのエラーハンドリング、コード品質のルールを定義しています。

**いつ参照すべきか**: Markdownファイル編集時、Pythonコード変更時

### 4. <a>instructions/documentation.instructions.md</a>

**ドキュメント作成ガイドライン**

ドキュメントの責任分掌、DRY原則、適切な配置ルールを定義しています。

**いつ参照すべきか**: ドキュメント作成・更新時

### 5. <a>instructions/testing.instructions.md</a>

**テスト・動作確認手順**

GitHub Actionsによる自動テスト、エラー確認、自動マージ機能の手順を説明しています。

**いつ参照すべきか**: テスト実行、ワークフロー確認時

## VS Code カスタムチャット参加者

VS Code で GitHub Copilot を使用する際、カスタムチャット参加者を利用できます。

- **@kansai**: 関西弁で応答するフレンドリーなプログラミングアシスタント

詳細は <a>copilot-chat-participants.md</a> を参照してください。

## 参考リンク

- <a>README.md</a>: ユーザー向け使用方法・セットアップ手順
- <a>data/README.md</a>: 銘柄リスト・投資志向性設定の編集ガイド
- <a>docs/TEST.md</a>: ユニットテストの実行方法
- <a>specs/requirements-index.md</a>: 要件定義と機能別仕様書のインデックス
