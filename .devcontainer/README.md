# Dev Container for Workflow Use

このDev Container設定は、workflow-useプロジェクトの開発環境を提供します。ブラウザの動作を可視化できるVNCサーバーが含まれています。

## 主な機能

- **Python 3.12**: 最新の安定版Python
- **uv**: 高速なPythonパッケージマネージャー
- **ブラウザ自動化**: Chromium、Firefox（browser-use用）
- **ブラウザ表示機能**: VNCサーバーによる可視化
- **開発ツール**: git, GitHub CLI, Node.js
- **VS Code拡張機能**: Python, Ruff, Black formatter等

## セットアップ

1. VS CodeでこのプロジェクトをDevContainerで開く
2. 自動セットアップが完了するまで待つ
3. **VNCサーバーが自動起動** - ブラウザで http://localhost:6080/vnc.html を開く
4. ブラウザの動作を可視化して確認できます

## ブラウザ表示の使い方

DevContainer内でブラウザ自動化を可視化するための設定：

1. **自動起動**: コンテナ起動時にVNCサーバーが自動的に開始
2. **アクセス方法**: ブラウザで http://localhost:6080/vnc.html を開く
3. **パスワード不要**: 開発の利便性のためパスワードなしで設定
4. **解像度**: デフォルトは1280x1024

### ブラウザ表示のテスト

動作確認用のテストスクリプト：

```bash
cd /workspace/workflows/examples
python test_browser_display.py
```

このスクリプトは：
- VNCディスプレイ内でブラウザを起動
- Webサイトへのナビゲーション
- 視覚的なフィードバックのデモ
- スクリーンショットの撮影

## 利用可能なコマンド

### 基本コマンド
- `runtest` - 環境チェック
- `wf` - ワークスペースへ移動
- `uvactivate` - 仮想環境をアクティベート（通常は自動）

### VNC/ブラウザ表示コマンド
- `vnc-status` - VNCサーバーの状態確認
- `browser-view` - ブラウザ表示用URLを表示
- `stopvnc` - VNCサーバーを停止
- `startvnc` - VNCサーバーを再起動

## ワークフローの実行

### CSVランナーの使用

```bash
cd /workspace/workflows/examples
python csv_runner.py
```

ブラウザの動作は http://localhost:6080/vnc.html で確認できます。

### プログラムでの実行

```python
from workflow_use import WorkflowOrchestrator
from browser_use import Browser

# 可視化する場合は headless=False を設定
browser = Browser(headless=False)
orchestrator = WorkflowOrchestrator()
result = await orchestrator.run("path/to/workflow.json", input_data={})
```

## uvの使い方

```bash
# パッケージのインストール
uv pip install package-name

# 依存関係の更新
uv pip install -e .

# パッケージの一覧
uv pip list

# 新しいPythonバージョンのインストール
uv python install 3.11
```

## トラブルシューティング

### 一般的な問題
1. `runtest`で環境を確認
2. 仮想環境がアクティブか確認（プロンプトに`(.venv)`が表示）
3. 依存関係の再インストール: `uv pip install -e /workspace`

### ブラウザ表示の問題
1. **ブラウザが見えない**: http://localhost:6080/vnc.html を開いているか確認
2. **VNCが動作しない**: `vnc-status`でサービス状態を確認
3. **VNCの再起動**: `stopvnc`してから`startvnc`
4. **ブラウザがクラッシュ**: `headless=False`を使用しているか確認

### browser-useが動作しない場合

```bash
# 仮想ディスプレイの確認
echo $DISPLAY  # :99 が表示されるはず

# VNCサーバーの状態確認
vnc-status

# 手動でVNCを再起動
stopvnc
startvnc
```

## 開発のヒント

1. **デバッグ**: ブラウザの動作を視覚的に確認可能
2. **スクリーンショット**: 可視化モードでも通常通り動作
3. **パフォーマンス**: 可視化モードは若干遅いが開発には最適
4. **ヘッドレスモード**: 本番/CI環境では`headless=True`を使用

## 環境の詳細

- **ベースイメージ**: Python 3.12 on Debian Bookworm
- **ディスプレイサーバー**: Xvfb (仮想フレームバッファ)
- **VNCサーバー**: x11vnc
- **Webアクセス**: noVNC (ブラウザベースのVNCクライアント)
- **ウィンドウマネージャー**: Fluxbox (軽量)