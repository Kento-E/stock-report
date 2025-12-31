# GitHub Copilot 向け指示ファイル

このディレクトリには、GitHub Copilot 向けのパス固有の指示ファイルが格納されています。

## GitHub Copilot 公式仕様について

このディレクトリ構造は、GitHub Copilot の公式仕様に準拠しています：

- **リポジトリ全体の指示**: `.github/copilot-instructions.md`（このディレクトリの親ディレクトリ）
- **パス固有の指示**: `.github/instructions/*.instructions.md`（このディレクトリ）

各 `.instructions.md` ファイルには、YAML フロントマターで `applyTo` パターンを指定し、特定のファイルやディレクトリにのみ適用される指示を記述できます。

## ファイル構成

- `coding.instructions.md` - コーディング時の品質・スタイル指示（Markdown、Python）
  - 適用対象: `**/*.{md,py}`
- `documentation.instructions.md` - ドキュメント作成時の責任分掌とDRY原則
  - 適用対象: `**/*.md`
- `testing.instructions.md` - テスト・動作確認手順（統合テスト、ワークフロー確認）
  - 適用対象: `**/*.{py,yml,yaml}`

## 用途別の分類のメリット

指示ファイルを用途別に分けることで、以下のメリットがあります：

- **保守性の向上**: 各ファイルが特定の目的に特化しているため、更新や修正が容易
- **可読性の向上**: 必要な情報を素早く見つけられる
- **拡張性**: 新しい指示カテゴリを追加する際、既存ファイルに影響を与えない
- **パフォーマンス**: GitHub Copilot が必要な指示のみを読み込むため、効率的

## 新しい指示の追加

新しい指示を追加する場合は、その用途に応じて適切なファイルに追加するか、新しいファイルを作成してください。

新規ファイルを作成する場合は、以下の形式に従ってください：

```markdown
---
applyTo: "適用するファイルパターン（例: src/**/*.py）"
---

# 指示タイトル

指示内容...
```

## 参考リンク

- [GitHub Copilot 公式ドキュメント - カスタム指示の追加](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [GitHub Copilot 公式ドキュメント - .instructions.md のサポート](https://github.blog/changelog/2025-07-23-github-copilot-coding-agent-now-supports-instructions-md-custom-instructions/)
