# Green ワークフロー

## ファイル一覧
- `green-scout-message-COMPLETED.workflow.json` - 本番用ワークフロー ✅
- `green-scout-sample.csv` - 候補者データサンプル

## 実行方法
```bash
cd workflows/green
python ../common/csv_runner.py green-scout-sample.csv green-scout-message-COMPLETED.workflow.json
```

## 動作確認済み
- 候補者ID 1529182で動作確認済み
- 成功率: 約67%