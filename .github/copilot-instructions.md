# GitHub Copilot Instructions

このリポジトリで GitHub Copilot を使用する際の指示事項です。

## はじめに

このリポジトリは、株式銘柄の動向をAIで自動分析し、レポートを生成・配信するPythonシステムです。

詳細な情報は以下のドキュメントを参照してください：

- **システム概要・技術スタック**: [README.md](../README.md)
- **詳細な技術仕様・モジュール構成**: [requirements.instructions.md](instructions/requirements.instructions.md)

## 重要な指示ファイル

このリポジトリには、以下の詳細な指示ファイルが `.github/instructions/` ディレクトリに配置されています。コードを変更する前に、必ず該当する指示ファイルを確認してください。

### 1. [requirements.instructions.md](instructions/requirements.instructions.md)

**システムの要件定義書** - 最も重要なドキュメント

システム概要、機能要件、非機能要件、モジュール構成など、システム全体の仕様を定義しています。

**いつ参照すべきか**: 機能追加、仕様変更、システム理解が必要な時

### 2. [copilot.instructions.md](instructions/copilot.instructions.md)

**GitHub Copilot 使用時の指示事項**

言語設定、Markdownルール、コーディング規約、ドキュメント更新ルール、効率的な利用方針を定義しています。

**いつ参照すべきか**: Pull Request作成、ドキュメント作成、コード変更時

### 3. [coding.instructions.md](instructions/coding.instructions.md)

**コーディングガイドライン**

Markdown Lintルール、コードスタイル規約を定義しています。

**いつ参照すべきか**: Markdownファイル編集時

### 4. [testing.instructions.md](instructions/testing.instructions.md)

**テスト・動作確認手順**

GitHub Actionsによる自動テスト、エラー確認、自動マージ機能の手順を説明しています。

**いつ参照すべきか**: テスト実行、ワークフロー確認時

## VS Code カスタムチャット参加者

VS Code で GitHub Copilot を使用する際、カスタムチャット参加者を利用できます。

- **@kansai**: 関西弁で応答するフレンドリーなプログラミングアシスタント

詳細は [copilot-chat-participants.md](copilot-chat-participants.md) を参照してください。

## 参考リンク

- [README.md](../README.md): ユーザー向け使用方法・セットアップ手順・環境変数設定
- [docs/TEST.md](../docs/TEST.md): ユニットテストの実行方法
- [requirements.instructions.md](instructions/requirements.instructions.md): システム全体の要件定義とモジュール構成
