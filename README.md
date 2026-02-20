<div align="center">

# Minecraft ID Hunter

Lightweight. Parallel. Endless.

A headless engine for hunting available Minecraft usernames.

[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![asyncio](https://img.shields.io/badge/async-native-success)]()
[![aiohttp](https://img.shields.io/badge/http-aiohttp-informational)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-purple)]()

</div>

---

<div align="center">

🌐 **Language**

[🇺🇸 English](#english) | [🇯🇵 日本語](#japanese)

</div>

---

---

# English

## What is this?

This tool scans for available Minecraft usernames — continuously and efficiently.

No GUI. 
No extra layers. 
Just a fast async pipeline built for long runs.

---

## Features

- Fully asynchronous
- Adaptive rate limiter
- Automatic 429 recovery
- Low memory footprint
- High parallelism
- Live terminal stats
- Instant result saving

---

## Installation

```bash
git clone https://github.com/yourname/minecraft-id-hunter
cd minecraft-id-hunter
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

Stop safely with:

```
CTRL + C
```

---

## Output

```
available_ids.txt
```

---

## Tuning

Low-end machine:

```python
concurrent_connections = 20
max_rate = 8
```

High-end machine:

```python
concurrent_connections = 80
max_rate = 20
```

---

## Philosophy

This is not a feature-heavy tool.

It’s a throughput engine.

---

## License

MIT

---

---

# Japanese

## What is this?

利用可能な Minecraft ID を高速で探索し続ける 
ヘッドレス型の非同期エンジンです。

GUIなし。 
無駄なレイヤーなし。 
長時間稼働前提の設計。

---

## 特徴

- フル async 構成
- 自動レート調整
- 429 自動復帰
- 低メモリ使用量
- 高並列処理
- リアルタイム統計表示
- 結果の即時保存

---

## インストール

```bash
git clone https://github.com/yourname/minecraft-id-hunter
cd minecraft-id-hunter
pip install -r requirements.txt
```

---

## 実行

```bash
python main.py
```

停止：

```
CTRL + C
```

---

## 出力

```
available_ids.txt
```

---

## チューニング

低スペック環境：

```python
concurrent_connections = 20
max_rate = 8
```

高性能環境：

```python
concurrent_connections = 80
max_rate = 20
```

---

## 設計思想

多機能ツールではありません。

探索速度に全振りしたエンジンです。

---

## ライセンス

MIT
