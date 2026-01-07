# VS Code 設定ディレクトリ

このディレクトリには、VS Code固有の設定ファイルが含まれています。

## mcp.json

**MCP (Model Context Protocol) サーバー設定ファイル**

このファイルは、GitHub Copilotが MCP (Model Context Protocol) を通じてリポジトリ情報にアクセスするための設定を定義しています。

### 機能

- **GitHub MCP Server**: DockerコンテナでGitHub MCP Serverを起動し、GitHub Copilotにリポジトリの詳細情報を提供
- **セキュアな認証**: Personal Access Tokenをプロンプト入力方式で取得し、リポジトリにコミットしない安全な設計

### 使用方法

1. **前提条件**
   - VS Code（最新版推奨）
   - GitHub Copilot拡張機能がインストールされていること
   - Dockerがインストールされていること

2. **初回起動時の設定**
   - VS Codeでこのリポジトリを開くと、GitHub Personal Access Tokenの入力を求められます
   - トークンの取得方法は、READMEの「MCP (Model Context Protocol) サポート」セクションを参照してください

3. **MCPサーバーの起動**
   - VS Codeが自動的にDockerコンテナでGitHub MCP Serverを起動します
   - GitHub Copilotがリポジトリ情報（Issue、Pull Request、コミット履歴など）にアクセス可能になります

### セキュリティ

- **Personal Access Tokenは絶対にコミットしないでください**
- このファイル（mcp.json）は安全にリポジトリ管理できます（トークンは含まれていません）
- 使用しなくなったトークンは、GitHubの設定画面から必ず削除してください

### トラブルシューティング

#### Dockerが起動しない

- Dockerがインストールされているか確認してください
- Dockerデーモンが起動しているか確認してください

#### トークン入力のプロンプトが表示されない

- VS Codeを再起動してください
- GitHub Copilot拡張機能が最新版か確認してください

#### MCP Serverに接続できない

- GitHub Personal Access Tokenの権限スコープを確認してください（推奨: `repo`, `read:org`, `read:user`）
- トークンの有効期限が切れていないか確認してください

### 参考リンク

- [GitHub公式: Setting up the GitHub MCP Server](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server)
- [VS Code: Use MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [リポジトリのREADME - MCP サポートセクション](../README.md#mcp-model-context-protocol-サポート)
