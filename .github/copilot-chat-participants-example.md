# カスタムチャット参加者 使用例

このファイルでは、`.github/copilot-chat-participants.md` で定義されたカスタムチャット参加者の使用例を示します。

## 関西弁チャット（@kansai）の使い方

### VS Codeでの使用手順

1. VS Codeでこのリポジトリを開きます
2. GitHub Copilot拡張機能がインストールされていることを確認します
3. チャットパネルを開きます（Ctrl+Shift+I または Cmd+Shift+I）
4. チャット入力欄で `@kansai` とメンションします
5. その後に質問やリクエストを入力します

### 使用例

#### 例1: コードの書き方を質問

```
@kansai Pythonでファイルを読み込む方法を教えて
```

期待される応答:
関西弁でファイル読み込みの方法を説明してくれます。

#### 例2: エラーのデバッグ

```
@kansai このコードでエラーが出るんだけど、どこが間違ってる？
[コードを貼り付け]
```

期待される応答:
関西弁でエラー原因を分析し、修正方法を提案してくれます。

#### 例3: 関数の説明

```
@kansai この関数は何をしているの？
def calculate_moving_average(prices, window):
    return [sum(prices[i:i+window])/window for i in range(len(prices)-window+1)]
```

期待される応答:
関西弁で移動平均の計算処理を説明してくれます。

## 注意事項

- カスタムチャットモードは VS Code の GitHub Copilot Chat でのみ使用できます
- GitHub上のIssueやPull Requestのコメントでは使用できません
- 技術的な正確性は保たれつつ、関西弁で親しみやすく説明されます

## その他のカスタムチャット参加者

必要に応じて、`.github/copilot-chat-participants.md` に他のカスタムチャット参加者を追加できます。
例：敬語モード、初心者向けモード、上級者向けモードなど。
