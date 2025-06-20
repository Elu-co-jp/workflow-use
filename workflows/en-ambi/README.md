# en-ambi ワークフロー

## ファイル一覧
- `en-ambi-scout-message.workflow.json` - テスト用（求人選択なし）✅ 100%動作
- `en-ambi-scout-complete.workflow.json` - 完全版（開発中）🚧
- `en-ambi-scout-recorded.workflow.json` - 録画版（旧）
- `en-ambi-test.csv` - テストデータ

## 実行方法
```bash
cd workflows/en-ambi
python ../common/csv_runner.py en-ambi-test.csv en-ambi-scout-message.workflow.json
```

## 状況
- **テスト用**: 12ステップ、100%成功
- **完全版**: 18ステップ、新ウィンドウ処理が課題