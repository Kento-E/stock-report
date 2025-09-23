# stock-report

## Github Actions用 Secrets and variables 設定方法

本プロジェクトの自動実行・メール配信には、GithubリポジトリのWeb画面から以下の「Secrets and variables」の登録が必要です。

### 必須Secrets（リポジトリ設定 > Settings > Secrets and variables > Actions）

| Secret名         | 用途                         | 例・備考           |
| ---------------- | ---------------------------- | ------------------ |
| `CLAUDE_API_KEY` | Claude Sonnet APIキー        |                    |
| `MAIL_TO`        | レポート送信先メールアドレス |                    |
| `MAIL_FROM`      | 送信元メールアドレス         |                    |
| `SMTP_SERVER`    | SMTPサーバー                 | 例: smtp.gmail.com |
| `SMTP_PORT`      | SMTPポート                   | 通常587            |
| `SMTP_USER`      | SMTP認証ユーザー             |                    |
| `SMTP_PASS`      | SMTP認証パスワード           |                    |

> これらは「Repository secrets」として登録してください。値は外部に公開されません。

#### Claude Sonnet APIキー発行手順

1. [Anthropic Developer Platform](https://console.anthropic.com)にアクセスし、アカウントを作成します。
2. ログイン後、ダッシュボードまたはAPI管理画面に移動します。
3. 「[API Keys](https://console.anthropic.com/settings/keys)」から新規APIキーを発行します。
4. 発行されたAPIキーを控え、Githubリポジトリの「Secrets and variables」に `CLAUDE_API_KEY` として登録してください。

※API利用には有料プランや申請が必要な場合があります。詳細はAnthropic公式の案内をご確認ください。

### 追加設定（必要に応じて）

- 対象銘柄リストや分析条件を変数として管理したい場合は「Variables」に追加可能です。

## Github Web画面で必要なその他設定

- Actionsの有効化（Settings > Actions > General）
- メール配信に外部サービス（Gmail等）を使う場合は、アプリパスワードや2段階認証の設定も必要です。
- Github Actions workflowファイル（.github/workflows/）の設置

## 参考

- [Github公式: Secrets and variables](https://docs.github.com/ja/actions/security-guides/encrypted-secrets)
- [Github公式: Actionsの設定](https://docs.github.com/ja/actions/using-workflows/workflow-syntax-for-github-actions)

---

ご不明点は `.github/outputs/questions.md` へ追記してください。
