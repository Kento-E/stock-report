# GitHub Copilot エージェント設定ディレクトリ

このディレクトリには、GitHub Copilot向けのタスク別エージェント設定ファイルが格納されています。

## エージェント一覧

### default.md

**GitHub Copilot デフォルト指示**

すべてのタスクで適用される基本的な指示を定義します。

- 言語設定（日本語での出力）
- コミットハッシュの表記ルール
- Markdownスタイル
- Pythonコーディング規約
- ドキュメント・要件定義書の反映ルール
- GitHub Copilot Premiumの効率的な利用方針

### code-review.md

**GitHub Copilot コードレビュー指示**

コードレビュー実施時に適用される指示を定義します。

- レビューコメントの言語設定
- エラーハンドリングのチェック項目
- コード品質のチェック項目
- テストファイルの確認
- リンター実行の確認
- セキュリティチェック
- Markdownファイルのチェック

### pull-request.md

**GitHub Copilot Pull Request作成指示**

Pull Request作成時に適用される指示を定義します。

- 言語設定
- コミットハッシュの表記ルール
- PR説明文の管理ルール
- コーディング指示（エラーハンドリング、コード品質）
- リンター実行の必須化
- テストファイルの管理
- チェックリスト

### issue.md

**GitHub Copilot Issue作成指示**

Issue作成時に適用される指示を定義します。

- 言語設定
- コミットハッシュの表記ルール
- Issueタイトル・本文のベストプラクティス
- Markdownスタイル

## 設計思想

### タスク別エージェント

GitHub Copilotの公式仕様`.github/agents/`に従い、タスク（コードレビュー、Issue作成、PR作成）ごとに異なるAIペルソナを定義しています。これにより：

- 各タスクに最適化された指示を提供
- 指示内容の重複を排除
- 保守性の向上

### リポジトリ間の統一

discord-ai-chatbotリポジトリと同じ構造を採用し、管理を統一しています。

## メンテナンス

エージェント設定を更新する際は、以下のガイドラインに従ってください：

1. **Markdown Lintルール準拠**: 見出し階層、空行、ファイル末尾の改行などのルールを守る
2. **日本語で記述**: すべての内容は日本語で記述する
3. **重複の排除**: 複数のエージェントファイルで同じ内容を記載しない
4. **タスクごとの最適化**: 各エージェントファイルはそのタスクに特化した指示のみを含める

## 参考

- [GitHub Docs - Creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs - Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
