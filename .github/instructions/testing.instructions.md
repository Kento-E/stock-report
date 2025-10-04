# 動作確認手順

## 1. 事前準備

- 必要な Secrets（`CLAUDE_API_KEY`, `MAIL_TO`, `MAIL_FROM`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`）を GitHub リポジトリの「Settings > Secrets and variables > Actions」に登録する。
- Python 3.10 以上がインストールされていることを確認する。
- 必要なパッケージが`requirements.txt`に記載されている場合は、ローカル環境で`pip install -r requirements.txt`を実行する。

## 2. ローカル実行テスト

1. ターミナルでプロジェクトルートに移動する。

2. 以下のコマンドでスクリプトを実行する。

   ```sh
   python src/main.py
   ```

3. 実行結果として、各銘柄ごとに HTML レポートファイルが生成されることを確認する。

4. メール配信設定が正しければ、指定したメールアドレスにレポートが送信される。

## 3. GitHub Actions による自動実行テスト

1. `.github/workflows/report.yml`が正しく設置されていることを確認する。

2. GitHub リポジトリの「Actions」タブから`Daily Stock Report`ワークフローを手動で実行（`Run workflow`）する。

3. 実行ログで各ステップ（Checkout, Python セットアップ, 依存関係インストール, main.py 実行）が正常に完了することを確認する。

4. レポートファイルの生成・メール送信が成功しているか、ログおよび受信メールで確認する。

## 4. エラー発生時の確認

- エラーが発生した場合は、GitHub Actions のログまたはローカル実行時の出力を確認し、原因を特定する。
- Secrets の設定漏れや SMTP 認証エラー、API キーの不備などが主な原因となる。

## 5. 自動マージ機能の動作確認

1. テスト用のブランチを作成し、変更を加える。

2. GitHub 上で Pull Request を作成する。

3. Pull Request を承認（Approve）する。

4. `.github/workflows/auto-merge.yml` ワークフローが自動的に実行されることを確認する。

5. GitHub Actions のログで以下を確認する：
   - PR が承認されたことの検知
   - PR のマージ可能性のチェック
   - スカッシュマージの実行
   - ブランチの自動削除

6. Pull Request がマージされ、ブランチが削除されていることを確認する。

### エラーケース

- PR がマージ可能な状態でない場合（競合がある場合など）は、自動マージは実行されない。
- PR が Draft 状態の場合、Draft である旨が表示されるが、ワークフローはエラーにならず正常終了する。Ready for review に変更してから再度 Approve する必要がある。
- GitHub Actions の権限が不足している場合は、リポジトリ設定を確認する。

---

ファイル末尾は改行 1 つのみ（MD047）。
見出し・リストの前後には必ず空行（MD022, MD032）。
