# Setup Python Environment Action

このComposite Actionは、Python環境のセットアップ時にNLTKデータとdefeatbeta-apiデータを事前にダウンロードし、GitHub Copilotのファイアウォール制限を回避します。

## 目的

GitHub Copilotがワークフロー内でpytestなどのコマンドを実行する際、ファイアウォールルールによって外部ネットワーク（特にhuggingface.co）へのアクセスが制限されます。このアクションは、ファイアウォールが有効になる前に必要なデータを事前にダウンロードすることで、この問題を解決します。

## 実施内容

### 1. NLTKデータのキャッシュとダウンロード

defeatbeta-apiが依存するnltkパッケージが必要とする以下のデータをダウンロード・キャッシュします：

- **punkt**: 文章のトークン化
- **stopwords**: ストップワード
- **wordnet**: 語彙データベース
- **averaged_perceptron_tagger**: 品詞タグ付け

キャッシュキーは`requirements.txt`のハッシュ値を使用し、依存関係が変更された場合のみ再ダウンロードされます。

### 2. defeatbeta-apiデータの事前ダウンロード

defeatbeta-apiパッケージがhuggingface.coから取得する株式データ情報を事前にダウンロードします。エラーハンドリングを含んでおり、ダウンロードが失敗してもワークフローは継続します。

## 使用方法

```yaml
steps:
  - name: Checkout repository
    uses: actions/checkout@v3
  
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: "3.10"
  
  - name: Install dependencies
    run: |
      pip install --upgrade pip
      pip install -r requirements.txt
  
  - name: Setup Python environment with data downloads
    uses: ./.github/actions/setup-python-env
```

## 使用しているワークフロー

このアクションは以下のワークフローで使用されています：

- `.github/workflows/test.yml` - テスト実行ワークフロー
- `.github/workflows/copilot-setup-steps.yml` - Copilotセットアップワークフロー
- `.github/workflows/report.yml` - 日次レポート生成ワークフロー

## メンテナンス

このアクションを変更すると、上記のすべてのワークフローに自動的に反映されます。これにより、メンテナンス性が向上し、変更が必要な場合は一箇所を修正するだけで済みます。

## トラブルシューティング

### NLTKデータのダウンロードが失敗する

- タイムアウト値（現在5分）を増やすことを検討してください
- キャッシュが破損している可能性がある場合、GitHub Actionsのキャッシュをクリアしてください

### defeatbeta-apiデータのダウンロードが失敗する

- このステップはエラーハンドリングを含んでおり、失敗してもワークフローは継続します
- ただし、後続のステップでdefeatbeta-apiを使用する場合、再度ダウンロードが試行されます

## 関連ドキュメント

システム全体のファイアウォール対策については、[要件定義書のセクション9.1](./../instructions/requirements.instructions.md#91-ファイアウォール対策)を参照してください。
