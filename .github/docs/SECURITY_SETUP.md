# リポジトリセキュリティ設定ガイド

> **Note**: このドキュメントは、リポジトリを外部からの不正な改修から保護するための設定方法を説明します。

## 概要

このリポジトリをオーナー以外からのソースプッシュや不正な改修から保護するため、以下のセキュリティ設定を実施します。

## 1. ブランチ保護ルールの設定

### 設定方法

1. GitHubリポジトリページにアクセス
2. **Settings** > **Branches** を開く
3. **Add branch protection rule** をクリック
4. 以下の設定を行う

### 推奨設定

#### Branch name pattern

```
main
```

#### 必須のルール

- **✅ Require a pull request before merging**
  - プルリクエストなしで直接mainブランチにプッシュすることを禁止
  - ✅ **Require approvals**: 1以上を推奨
    - オーナー自身が承認者になることで、すべての変更を確認可能
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
    - 新しいコミットがプッシュされた場合、以前の承認を無効化
  - ✅ **Require review from Code Owners**
    - CODEOWNERSファイルで指定されたユーザーのレビューを必須化

- **✅ Require status checks to pass before merging**
  - テストやビルドが成功しないとマージできないようにする
  - ✅ **Require branches to be up to date before merging**
    - マージ前にブランチを最新の状態に更新することを必須化
  - 以下のステータスチェックを必須に設定：
    - `test` (GitHub Actions テストワークフロー)
    - その他、プロジェクトで実行しているチェック

- **✅ Require conversation resolution before merging**
  - プルリクエストのすべてのコメントが解決されるまでマージを禁止

- **✅ Require signed commits**（推奨）
  - コミットにGPG署名を必須化することで、コミット作成者の正当性を保証
  - 設定方法は後述

- **⚠️ Do not allow bypassing the above settings**
  - 管理者でも上記のルールをバイパスできないようにする
  - ただし、緊急時に自分でもマージできなくなるため、状況に応じて判断

- **⚠️ Restrict who can push to matching branches**（オプション）
  - 特定のユーザーやチームのみがブランチにプッシュできるように制限
  - オーナーのみを指定することで、完全な保護が可能
  - ただし、GitHub Actionsからのプッシュも制限される可能性があるため注意

#### その他の推奨設定

- **✅ Require linear history**
  - マージコミットを禁止し、履歴を線形に保つ
  - スカッシュマージやリベースマージのみを許可

- **✅ Require deployments to succeed before merging**（該当する場合）
  - デプロイメント環境がある場合、デプロイ成功を必須化

### 自動マージワークフローとの互換性

本リポジトリには `.github/workflows/auto-merge.yml` による自動マージ機能が実装されています。上記のブランチ保護ルールを設定しても、以下の条件を満たせば自動マージは正常に動作します：

#### 互換性を保つための設定

1. **GitHub Actions の権限設定**
   - **Settings** > **Actions** > **General** > **Workflow permissions** で以下を設定：
     - ✅ 「Read and write permissions」を選択
     - ✅ 「Allow GitHub Actions to create and approve pull requests」にチェック
   - これにより、`GITHUB_TOKEN` がマージ権限を持つ

2. **ブランチ保護ルールの設定時の注意点**
   - ✅ **「Require a pull request before merging」を有効化**: 自動マージは問題なく動作（PRを介してマージするため）
   - ✅ **「Require approvals」を設定**: 自動マージワークフローは承認後にトリガーされるため問題なし
   - ✅ **「Require review from Code Owners」を有効化**: オーナーが承認すれば自動マージ可能
   - ✅ **「Require status checks to pass」を有効化**: テストが成功していれば自動マージ可能
   - ⚠️ **「Do not allow bypassing the above settings」を有効化**: 管理者もルールをバイパスできなくなるが、自動マージワークフローは `GITHUB_TOKEN` を使用するため、正しく権限設定されていれば動作する
   - ❌ **「Restrict who can push to matching branches」でGitHub Actionsを除外しない**: この設定を有効にする場合、GitHub Actionsを許可リストに含める必要がある（通常は設定不要）

3. **動作フロー**
   - PRが作成される → テストが実行される → オーナーがレビュー・承認する → 自動マージワークフローがトリガーされる → ブランチ保護ルールのチェックを通過してマージされる

#### トラブルシューティング

自動マージが失敗する場合、以下を確認してください：

- GitHub Actions の権限設定が正しいか（Read and write permissions）
- ブランチ保護ルールで必要なステータスチェック（`test`）が成功しているか
- CODEOWNERSで指定されたオーナーの承認が得られているか
- PRがDraft状態でないか

## 2. リポジトリ権限の設定

### コラボレーターの管理

1. **Settings** > **Collaborators and teams** を開く
2. 外部のコラボレーターは追加しない、または最小限の権限（Read）のみを付与
3. 必要に応じて、信頼できるコラボレーターに限定して権限を付与

### 権限レベルの説明

- **Read**: リポジトリの閲覧とクローンのみ可能
- **Triage**: Issueやプルリクエストの管理が可能（コード変更は不可）
- **Write**: プッシュが可能（ブランチ保護ルールに従う）
- **Maintain**: リポジトリ設定の一部を管理可能
- **Admin**: すべての権限

**推奨**: 外部ユーザーには **Read** のみ、信頼できる開発者には **Write** を付与し、ブランチ保護ルールで制御する。

## 3. CODEOWNERSファイルの活用

本リポジトリには `.github/CODEOWNERS` ファイルが既に存在します。

### 現在の設定

```
# デフォルトのコードオーナー（すべてのファイルに適用）
* @copilot
```

### オーナー追加方法

オーナー自身をコードオーナーに追加することで、すべてのプルリクエストに対して自動的にレビュアーとして割り当てられます。

```
# デフォルトのコードオーナー（すべてのファイルに適用）
* @Kento-E @copilot
```

または、重要なファイルのみを保護する場合：

```
# デフォルト
* @copilot

# 重要な設定ファイル
/data/* @Kento-E @copilot
/.github/workflows/* @Kento-E @copilot
/src/* @Kento-E @copilot
```

### CODEOWNERSの効果

- プルリクエスト作成時に自動的にレビュアーが割り当てられる
- ブランチ保護ルールで「Require review from Code Owners」を有効にすることで、指定されたオーナーの承認が必須となる

## 4. 2要素認証（2FA）の有効化

### オーナーアカウントの2FA設定

1. GitHubアカウント設定 > **Password and authentication** を開く
2. **Two-factor authentication** を有効化
3. 認証アプリ（Google Authenticator、Authy等）またはSMSで設定

## 5. GitHub Actionsのセキュリティ設定

### Workflow permissions の設定

既にREADMEに記載されている設定を確認：

1. **Settings** > **Actions** > **General** > **Workflow permissions** を開く
2. 以下を設定：
   - 「Read and write permissions」を選択（必要な場合のみ）
   - 「Allow GitHub Actions to create and approve pull requests」にチェック

### Actions の承認設定

1. **Settings** > **Actions** > **General** > **Actions permissions** を開く
2. 推奨設定：
   - **Allow all actions and reusable workflows**: すべてのアクションを許可
   - または **Allow select actions and reusable workflows**: 信頼できるアクションのみを許可

## 6. Secretsの保護

### Secretsの管理

本リポジトリでは、以下のSecretsが設定されています（READMEより）：

- `CLAUDE_API_KEY`
- `GEMINI_API_KEY`
- `MAIL_TO`
- `MAIL_FROM`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `YAHOO_API_KEY`

### Secretsの保護方法

- Secretsは自動的に暗号化され、ログに表示されない
- Secretsは **Repository secrets** として登録されており、外部からアクセスできない
- 定期的にAPIキーをローテーションすることを推奨

## 7. コミット署名の設定（推奨）

### GPG署名の設定方法

1. GPGキーを生成：

```bash
gpg --full-generate-key
```

2. GPGキーをGitHubに登録：

```bash
gpg --armor --export YOUR_KEY_ID
```

3. Gitに署名設定を追加：

```bash
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true
```

4. GitHubアカウント設定 > **SSH and GPG keys** > **New GPG key** からキーを追加

### コミット署名の確認

署名されたコミットには、GitHub上で「Verified」バッジが表示されます。

## 8. 監査とモニタリング

### セキュリティログの確認

1. **Settings** > **Security** > **Audit log** を開く
2. リポジトリへのアクセスや変更履歴を確認

### 通知設定

1. **Watch** ボタンから通知設定を行う
2. すべてのプルリクエスト、Issue、コミットに対して通知を受け取る設定を推奨

## まとめ

上記の設定を実施することで、リポジトリは以下のように保護されます：

1. ✅ **直接プッシュの禁止**: mainブランチへの直接プッシュを禁止
2. ✅ **レビュー必須**: すべての変更はプルリクエストとレビューを経る
3. ✅ **テスト必須**: テストが成功しないとマージできない
4. ✅ **オーナー承認必須**: CODEOWNERSによりオーナーの承認が必須
5. ✅ **2要素認証**: アカウント乗っ取りを防止
6. ✅ **署名コミット**: コミット作成者の正当性を保証
7. ✅ **Secrets保護**: 機密情報の安全な管理

これらの設定により、オーナー以外からの不正な改修を効果的に防止できます。
