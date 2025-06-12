# Workflow Examples

このディレクトリには、workflow-useのサンプルワークフローとスクリプトが含まれています。

## ファイル構成

### ワークフローファイル
- `example.workflow.json` - 基本的なワークフローの例
- `cr-support-candidate-message.workflow.json` - CR-Supportでの候補者メッセージ送信ワークフロー

### 実行スクリプト
- `runner.py` - 単一のワークフローを実行する基本的なスクリプト
- `csv_runner.py` - CSVファイルから複数のワークフローを一括実行するスクリプト

### サンプルデータ
- `sample_candidates.csv` - csv_runner.pyで使用するサンプルCSVファイル

## 使い方

### 単一ワークフローの実行

```bash
python runner.py
```

### CSV一括実行

```bash
# 基本的な使い方
python csv_runner.py sample_candidates.csv cr-support-candidate-message.workflow.json

# オプション付き
python csv_runner.py sample_candidates.csv cr-support-candidate-message.workflow.json --batch-size 3 --output results_cr_support
```

#### csv_runner.pyのオプション

- `csv_file` (必須): 入力CSVファイルのパス
- `workflow_file` (必須): 実行するワークフローJSONファイルのパス
- `--batch-size`: 同時実行数（デフォルト: 1）
- `--output`: 結果ファイルの接頭辞（デフォルト: results）

#### CSVファイルの形式

CSVファイルのカラム名は、ワークフローの`input_schema`で定義されたフィールド名と一致する必要があります。

例（cr-support-candidate-message.workflow.json用）:
```csv
email,password,member_id,subject,message_body
test@example.com,password123,12345,件名,本文
```

#### 実行結果

実行結果は以下の形式でCSVファイルに保存されます：
- ファイル名: `{output}_{YYYYMMDD_HHMMSS}.csv`
- 内容: 各行の実行ステータス、入力データ、エラー情報など

## ワークフローの作成

新しいワークフローを作成する場合は、以下の形式に従ってください：

```json
{
  "name": "ワークフロー名",
  "description": "ワークフローの説明",
  "version": "1.0",
  "steps": [
    {
      "type": "navigation",
      "url": "https://example.com",
      "description": "サイトにアクセス"
    }
  ],
  "input_schema": [
    {
      "name": "email",
      "type": "string",
      "required": true
    }
  ]
}
```

## 注意事項

- ワークフロー実行時は、対象のWebサイトの利用規約を確認してください
- 大量のリクエストを送信する場合は、適切な間隔を設けてください
- パスワードなどの機密情報は適切に管理してください