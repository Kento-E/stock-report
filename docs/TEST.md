# テスト自動化ドキュメント

## 概要

本プロジェクトでは、pytest を使用した自動テストを実装しています。Pull Request 作成時や既存 PR へのプッシュ時に、GitHub Actions で自動的にテストが実行されます。

## テストの実行方法

### ローカル環境での実行

```bash
# すべてのテストを実行
python -m pytest tests/ -v

# カバレッジレポート付きで実行
python -m pytest tests/ -v --cov=src --cov-report=html

# 特定のテストファイルのみ実行
python -m pytest tests/test_stock_loader.py -v
```

### GitHub Actions での自動実行

Pull Request を作成すると、自動的に以下が実行されます：

1. Python 環境のセットアップ
2. 依存パッケージのインストール
3. テストの実行
4. カバレッジレポートの生成とアップロード

テスト結果は PR の「Checks」タブで確認できます。

## テストの構成

### テストファイル一覧

| ファイル名 | テスト対象モジュール | テストケース数 |
|-----------|-------------------|--------------|
| `test_stock_loader.py` | stock_loader.py | 10 |
| `test_data_fetcher.py` | data_fetcher.py | 2 |
| `test_report_generator.py` | report_generator.py | 3 |
| `test_mail_utils.py` | mail_utils.py | 5 |
| `test_ai_analyzer.py` | ai_analyzer.py | 8 |

### テストカバレッジ

主要なモジュールについてユニットテストを実装しています：

- **stock_loader**: YAML読み込み、通貨判定、エラーハンドリング
- **report_generator**: HTMLレポート生成、マークダウン変換
- **mail_utils**: メール本文生成、マークダウン変換
- **ai_analyzer**: 保有状況プロンプト生成、損益計算

## テストの種類

### 1. 正常系テスト
- 正しい入力で期待通りの出力が得られることを確認

### 2. 異常系テスト
- エラーケースで適切に例外が発生することを確認
- ファイルが存在しない、YAML 形式が不正、など

### 3. 境界値テスト
- 空のリスト、ゼロ値、None など境界条件での動作を確認

## テスト環境の制約

一部のテストは、以下の理由でスキップまたは制限されています：

- **外部 API への依存**: 実際の API 呼び出しを避けるため、データ構造のみ検証
- **ネットワーク接続**: defeatbeta-api がネットワーク接続を試みるため、一部テストをスキップ

これらの制約は、テストの高速化と安定性向上のためのものです。実際の統合テストは、本番環境（GitHub Actions）で実施されます。

## テスト失敗時の対応

1. **GitHub Actions でテストが失敗した場合**:
   - PR の「Checks」タブでエラー内容を確認
   - ローカル環境で同じテストを実行して再現
   - エラーを修正して再度プッシュ

2. **ローカルでテストが失敗した場合**:
   - `-v` オプションで詳細を確認: `python -m pytest tests/ -v`
   - `--tb=short` で短いトレースバックを表示
   - 特定のテストのみ実行して問題を切り分け

## 新しいテストの追加

新しい機能を追加した場合は、対応するテストも追加してください：

1. `tests/` ディレクトリに `test_<module_name>.py` ファイルを作成
2. テストクラスとテストメソッドを実装
3. `python -m pytest tests/test_<module_name>.py -v` で確認

### テストの命名規則

- テストファイル: `test_*.py`
- テストクラス: `Test<ModuleName>`
- テストメソッド: `test_<function_name>_<scenario>`

例：
```python
class TestStockLoader:
    def test_load_valid_yaml_file(self):
        # テストコード
        pass
```

## CI/CD との統合

テストは CI/CD パイプラインに統合されており、以下のタイミングで自動実行されます：

- Pull Request の作成時
- Pull Request へのプッシュ時
- main ブランチへのマージ時

テストが失敗した場合、マージはブロックされます（推奨設定）。

## カバレッジレポート

カバレッジレポートは、テスト実行時に自動的に生成され、GitHub Actions のアーティファクトとしてダウンロード可能です：

1. PR の「Checks」タブを開く
2. 「Run Tests」ワークフローを選択
3. 「Artifacts」セクションから「coverage-report」をダウンロード
4. ダウンロードした ZIP ファイルを展開し、`index.html` をブラウザで開く

## ベストプラクティス

- **テストは独立させる**: テスト間で状態を共有しない
- **モックを使用**: 外部 API 呼び出しはモックで代用
- **明確なアサーション**: 何をテストしているか明確にする
- **エッジケースをテスト**: 正常系だけでなく異常系もテスト

## トラブルシューティング

### pytest が見つからない

```bash
pip install -r requirements.txt
```

### インポートエラー

テストファイルで `sys.path.insert(0, ...)` を使用して、src ディレクトリをパスに追加しています。

### defeatbeta-api 関連のエラー

defeatbeta-api はネットワーク接続を試みるため、一部テストをスキップする設定になっています。これは正常な動作です。
