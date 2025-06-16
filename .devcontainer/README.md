# Dev Container for Workflow Use

このDev Container設定は、workflow-useプロジェクトの開発環境を提供します。

## 含まれるツール

- **uv**: 高速なPythonパッケージマネージャー
- **Python 3.12**: 最新の安定版Python
- **ブラウザ**: Chromium、Firefox（browser-use用）
- **開発ツール**: git, GitHub CLI, Node.js
- **VS Code拡張機能**: Python, Ruff, Black formatter等

## 使い方

1. VS CodeでこのプロジェクトをDevContainerで開く
2. 自動セットアップが完了するまで待つ
3. ターミナルで以下のコマンドが使用可能:

```bash
# 環境チェック
runtest

# ワークスペースへ移動
wf

# 仮想環境をアクティベート（通常は自動）
uvactivate

# CSVランナーを実行
cd /workspace/workflows/examples
python csv_runner.py sample_candidates.csv cr-support-candidate-message.workflow.json
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

### browser-useが動作しない場合

```bash
# 仮想ディスプレイの確認
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

### パッケージが見つからない場合

```bash
# 開発モードで再インストール
cd /workspace
uv pip install -e .
```