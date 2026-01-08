# システムアーキテクチャ仕様書

> **Note**: このファイルはシステム全体の構成・技術スタック・アーキテクチャを定義します。

## システム概要

銘柄株の動向やトレンドを Claude Sonnet（AI）で調査・分析し、HTML レポートとして自動生成・メール配信するシステム。

## 目的

- 投資判断の材料となる情報を自動で収集・分析し、分かりやすいレポートとして提供する。
- 日々の株式市場の変化を迅速に把握できるようにする。

## モジュール構成

システムはAPI別・機能別にモジュール化されており、単一責任の原則に従って設計されています。

### コアモジュール（src/）

システムは機能別にディレクトリ分割されており、保守性と可読性が向上しています。

#### メインモジュール

- **main.py**：メインエントリーポイント。各モジュールを組み合わせたオーケストレーション処理。全体のワークフローを制御し、データ取得・分析・レポート生成・メール配信の一連の処理を統合する。
- **config.py**：環境変数の読み込みと設定値の一元管理。API キー、メール設定、モデル名などのシステム設定を管理する。

#### データ読み込みモジュール（loaders/）

- **stock_loader.py**：YAML銘柄リストの読み込み、通貨判定、銘柄分類機能。銘柄データの読み込みと保有状況に基づく分類（保有中、空売り中、購入検討中）を担当する。
- **preference_loader.py**：投資志向性設定の読み込みとプロンプト生成。YAML形式の投資志向性設定ファイルを読み込み、AI分析用のプロンプト文字列を生成する。

#### バリデーションモジュール（validators/）

- **validate_stocks.py**：stocks.yamlファイルのバリデーションスクリプト。YAML構文、必須フィールド、型、値の範囲などを検証し、不正なデータの混入を防止する。
- **validate_preferences.py**：investment_preferences.yamlファイルのバリデーションスクリプト。投資志向性設定の形式を検証し、不正な設定値の混入を防止する。

#### フォーマットモジュール（formatters/）

- **format_yaml.py**：YAMLファイルの自動フォーマットスクリプト。インデントのズレを修正し、コメントを保持したままフォーマット。`--check` オプションでフォーマットが必要かチェックのみ可能。

#### 分析モジュール（analyzers/）

- **data_fetcher.py**：Yahoo Finance APIとdefeatbeta-apiによるデータ取得。株価データとニュースデータの取得を担当し、外部APIとの通信を抽象化する。
- **ai_analyzer.py**：Claude API/Gemini APIによる分析処理と保有状況プロンプト生成。取得したデータと投資志向性設定を基にAIで分析を実施し、売買判断と推奨価格を含むレポートを生成する。

#### レポート生成モジュール（reports/）

- **simplifier.py**：レポート簡略化モジュール。ホールド判断の検出とレポートの簡略化を担当する。
- **generator.py**：HTMLレポート生成とファイル保存。分析結果をHTML形式に変換し、ファイルとして保存する。ホールド判断時の簡略化ロジックを含む。

#### メール配信モジュール（mails/）

- **config.py**：SMTP設定の取得。環境変数からメール送信に必要な設定を読み込む。
- **formatter.py**：MarkdownからHTMLへの変換、折りたたみセクションの生成。
- **toc.py**：目次（Table of Contents）の生成。売買判断を抽出してサマリーを作成する。
- **body.py**：メール本文生成。保有状況に応じて分類されたメール本文を生成する。formatterとtocを使用。
- **sender.py**：メール送信機能。SMTP設定に基づいてレポートをメール配信する。

### データ・設定ファイル

- **data/stocks.yaml**：分析対象銘柄リスト（YAML形式、Git で変更履歴管理）
- **data/investment_preferences.yaml**：投資志向性設定ファイル（YAML形式、Git で変更履歴管理）
- **requirements.txt**：依存パッケージ管理
- **.env/.env.example**：環境変数テンプレート

### GitHub Actions・設定

- **.github/workflows/report.yml**：自動実行ワークフロー
- **.github/workflows/auto-merge.yml**：PR 承認時の自動マージワークフロー
- **.github/workflows/test.yml**：テスト自動実行ワークフロー
- **.github/workflows/copilot-setup-steps.yml**：GitHub Copilot用セットアップワークフロー
- **.github/workflows/validate-stocks.yml**：stocks.yamlバリデーション自動実行ワークフロー
- **.github/workflows/validate-preferences.yml**：investment_preferences.yamlバリデーション自動実行ワークフロー
- **.github/workflows/format-yaml.yml**：YAML自動フォーマットワークフロー
- **.github/actions/setup-python-env**：Python環境セットアップ用の再利用可能アクション（NLTKデータ・defeatbeta-apiデータの事前ダウンロード処理を集約）
- **.github/copilot-instructions.md**：VS Code 用カスタムチャットモード定義
- **.vscode/mcp.json**：MCP (Model Context Protocol) サーバー設定

**Note**: report.yml、test.yml、copilot-setup-steps.ymlは、setup-python-envアクションを使用してファイアウォール対策を実施しています（詳細は自動化仕様書を参照）。

### テスト（tests/）

テストの詳細については <a>docs/TEST.md</a> を参照してください。

## モジュール間の関係

```
main.py (オーケストレーション)
  ├── config.py (設定管理)
  ├── loaders/ (データ読み込み)
  │     ├── stock_loader.py (銘柄データ読み込み)
  │     └── preference_loader.py (投資志向性設定読み込み)
  ├── analyzers/ (分析)
  │     ├── data_fetcher.py (外部API: Yahoo Finance, defeatbeta-api)
  │     │     └── config.py
  │     └── ai_analyzer.py (AI分析: Claude, Gemini)
  │           ├── config.py
  │           ├── loaders/stock_loader.py
  │           └── loaders/preference_loader.py (投資志向性プロンプト生成)
  ├── reports/ (レポート生成)
  │     ├── generator.py (HTMLレポート生成)
  │     │     ├── mails/formatter.py
  │     │     └── reports/simplifier.py (ホールド判断検出・簡略化)
  │     └── simplifier.py (レポート簡略化)
  └── mails/ (メール配信)
        ├── sender.py (メール送信)
        ├── body.py (メール本文生成)
        ├── formatter.py (Markdown→HTML変換)
        ├── toc.py (目次生成)
        └── config.py (SMTP設定)

validators/ (バリデーション - 独立実行)
  ├── validate_stocks.py (stocks.yaml検証)
  └── validate_preferences.py (投資志向性設定検証)

formatters/ (フォーマット - 独立実行)
  └── format_yaml.py (YAML自動フォーマット)
```

## 利用技術

- Python（データ収集・分析・レポート生成・メール送信）
- anthropic（Claude Sonnet API 公式パッケージ）
- defeatbeta-api（市場ニュースデータ取得）
- PyYAML（YAML ファイルの解析）
- ruamel.yaml（コメント保持可能なYAMLフォーマッター）
- requests, python-dotenv, smtplib, email, markdown
- pytest, pytest-cov（テストフレームワーク・カバレッジ測定）
- GitHub Actions（スケジューラ・自動化・CI/CD）
- MCP (Model Context Protocol)（GitHub MCP Server経由でGitHub Copilotのコンテキスト拡張）

## 開発環境・ツール

### GitHub Copilot と MCP サポート

本プロジェクトは、GitHub Copilot の活用を推奨しており、MCP (Model Context Protocol) をサポートしています。

#### MCP (Model Context Protocol)

VS Code で MCP を利用することで、GitHub Copilot がリポジトリの情報により深くアクセスし、以下のような高度な支援が可能になります：

- **リポジトリ情報の直接取得**：Issue、Pull Request、コミット履歴などへのアクセス
- **ファイルシステム操作**：YAMLファイルの編集支援、データディレクトリの安全な操作
- **コード品質分析**：Ruffによる品質チェック、pytest統合、未使用コード検出
- **CI/CD管理**：GitHub Actionsワークフローの管理と自動化

設定の詳細は [.vscode/README.md](../../.vscode/README.md) を参照してください。

## 非機能要件

- **セキュリティ**：API キーや個人情報の安全な管理（.env, Secrets, BCC 運用等）
- **パフォーマンス**：処理が 1 時間以内に完了すること
- **拡張性**：銘柄追加や分析ロジックの拡張が容易。銘柄リストはYAML形式で管理し、スマートフォンからも編集可能。銘柄ごとに追加メタデータを柔軟に管理可能
- **保守性**：設定や運用が容易で、モジュール分割・関数化されていること。銘柄の変更履歴を Git で管理
- **多市場・多通貨対応**：日本株（円）、米国株（ドル）、欧州株（ユーロ）など、複数の市場と通貨に対応可能な設計

## 運用・保守

- エラー通知・ログ出力（print ベース、今後拡張可）
- エラー詳細情報をメール本文に含めることで、GitHub Actions画面を確認せずに原因把握が可能
- API キー・認証情報の安全な管理
- モデル EOL や API 仕様変更時の迅速な対応
- モジュール分割により、各機能の独立したテスト・保守が可能
- 自動テストによりコード品質を継続的に保証
- Pull Request 作成時の自動テスト実行により、問題を早期発見

## その他

- 法令遵守（金融商品取引法等）
- 利用規約・プライバシーポリシーの整備
