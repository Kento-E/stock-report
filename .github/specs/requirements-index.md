# 要件定義書（インデックス）

> **Note**: このファイルは開発者およびGitHub Copilot向けの要件定義インデックスです。  
> 各機能の詳細仕様は、機能別の仕様書を参照してください。  
> ユーザー向けの使用方法・セットアップ手順は <a>README.md</a> を参照してください。

## システム概要

銘柄株の動向やトレンドを Claude Sonnet（AI）で調査・分析し、HTML レポートとして自動生成・メール配信するシステム。

## 仕様書一覧

システムは機能別に仕様書を分割し、単一責任の原則に従って整理されています。各機能の詳細は該当する仕様書を参照してください。

### 1. システムアーキテクチャ仕様書

**ファイル**: <a>system-architecture.md</a>

システム全体の構成、モジュール設計、技術スタック、非機能要件を定義します。

### 2. データ収集・分析機能仕様書

**ファイル**: <a>data-collection-analysis.md</a>

株価・ニュースデータの収集とAI分析機能の仕様を定義します。

### 3. レポート生成・メール配信機能仕様書

**ファイル**: <a>report-email.md</a>

HTMLレポート生成とメール配信機能の仕様を定義します。

### 4. 自動化・CI/CD機能仕様書

**ファイル**: <a>automation-cicd.md</a>

自動実行、テスト、バリデーション、CI/CDの仕様を定義します。

### 5. データ管理機能仕様書

**ファイル**: <a>data-management.md</a>

銘柄リストと投資志向性設定の管理仕様を定義します。

## クイックリファレンス

### 主要な機能要件

1. **データ収集**: Yahoo Finance API + defeatbeta-api による株価・ニュース取得
2. **AI分析**: Claude Sonnet / Gemini API による動向・トレンド分析
3. **レポート生成**: HTML形式の見やすいレポート自動生成
4. **メール配信**: 複数宛先へのBCC送信、銘柄分類表示
5. **自動実行**: GitHub Actions による自動実行
6. **テスト自動化**: pytest による品質保証
7. **データ管理**: YAML形式の銘柄リスト・投資志向性設定

### 主要な非機能要件

- **セキュリティ**: API キー・認証情報の安全管理
- **パフォーマンス**: 1時間以内の処理完了
- **拡張性**: 銘柄・分析ロジックの容易な拡張
- **保守性**: モジュール分割・関数化された設計
- **多市場対応**: 日本株・米国株等、複数市場・通貨対応

## 環境設定

### 実行環境

- GitHub Actions 上で定期実行（cron スケジューラ）
- 実行スケジュールの詳細は <a>automation-cicd.md</a> の「スケジューラ・自動実行」セクションを参照

### 設定管理

- 機密情報: GitHub Secrets で管理
- 銘柄リスト: `data/stocks.yaml`（Git管理）
- 投資志向性: `data/investment_preferences.yaml`（Git管理）
- 環境変数: `.env` または GitHub Secrets

**環境変数の詳細は <a>README.md</a> を参照してください。**

## 関連ドキュメント

### ユーザー向けドキュメント

- <a>README.md</a>: 使用方法・セットアップ手順
- <a>data/README.md</a>: 銘柄リスト・投資志向性設定の詳細

### 開発者向けドキュメント

- <a>docs/TEST.md</a>: テスト実行方法
- <a>.github/instructions/testing.instructions.md</a>: 動作確認手順
- <a>.github/instructions/copilot.instructions.md</a>: GitHub Copilot 利用指示
- <a>.github/instructions/coding.instructions.md</a>: コーディングガイドライン
- <a>.github/actions/setup-python-env/README.md</a>: Python環境セットアップアクション

## 更新履歴の管理

本要件定義書の変更履歴は Git のコミット履歴、Issue、Pull Request で管理します。要件定義書内には変更履歴セクションを含めません。

---

（本要件定義書は現行のモジュール化されたシステム設計・実装内容に基づき、今後の議論・運用により随時更新します）
