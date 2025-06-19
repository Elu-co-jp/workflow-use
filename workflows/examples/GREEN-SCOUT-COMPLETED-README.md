# Green Scout Message Workflow - COMPLETED VERSION

## ファイル名
`green-scout-message-COMPLETED.workflow.json`

## 概要
Greenの転職サイトで候補者にスカウトメッセージを送信する自動化ワークフローの完成版です。

## テスト済み環境
- **日付**: 2025-06-19
- **候補者ID**: 1529182
- **求人名**: 【エンタープライズ向け】アカウントプランナー
- **メッセージ**: test

## 実行方法

```python
import asyncio
from workflow_use.workflow.service import Workflow

async def main():
    workflow = Workflow.load_from_file('examples/green-scout-message-COMPLETED.workflow.json')
    await workflow.run(
        inputs={
            'candidate_id': '1529182',  # 候補者ID
            'job_name': '【エンタープライズ向け】アカウントプランナー',  # 求人名
            'message_text': 'test'  # スカウトメッセージ
        },
        close_browser_at_end=False,
    )

if __name__ == '__main__':
    asyncio.run(main())
```

## 必要なパラメータ
1. **candidate_id** (string, required): 対象候補者のID
2. **job_name** (string, required): 選択する求人名
3. **message_text** (string, required): 送信するスカウトメッセージ

## ワークフローステップ
1. 候補者検索ページに移動 (`https://www.green-japan.com/client/search?user_ids%5B%5D={candidate_id}`)
2. 候補者の行をクリックして詳細を表示
3. スカウトボタンをクリック
4. 求人選択ドロップダウンをクリック
5. 指定された求人名を選択
6. メッセージ入力エリアをクリック
7. スカウトメッセージを入力
8. 送信ボタンをクリック

## 修正された要素
- 候補者行のセレクタ: `#js-main-contents > div > table > tbody:nth-child(2)`
- スカウトボタンのセレクタ: `#js-react-search-main > div > div.mdl-resume.mdl-shadow--4dp.mdl-resume--is-half-open > div.mdl-resume__main > div.mdl-resume__main-header > div.mdl-resume__main-header__actions > button`
- 求人選択ボタン: `button.custom-select-button[id="js-select-jobOffer{candidate_id}"]`
- メッセージ入力エリア: `textarea.mdl-scoutform__textarea[placeholder="本文"][id]`
- 送信ボタン: XPathで最初の送信ボタンを選択

## 成功ログ
全8ステップが正常に完了し、スカウトメッセージの送信が成功しました。

## 注意事項
- このワークフローは2025年6月19日時点のGreenサイトの構造に基づいています
- サイトの構造が変更された場合、セレクタの調整が必要になる可能性があります
- 実際の運用前に必ずテスト実行を行ってください