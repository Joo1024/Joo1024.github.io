---
title: 把练习缩小，直到能够重复
date: 2026-09-26
lastmod: 2026-09-28
description: 技术学习和身体训练，都从一次可以再做的动作开始。
tags: [练习, 技术, 方法]
status: ongoing
sample: true
url: /practice/small-repetitions/
form: practice
domains: [body, craft]
paths: [精进]
---

## 先找到能持续的动作

很大的计划常常让人兴奋，也容易让第一次练习变成最后一次。现在倾向于把目标缩小：不是学完一门语言，而是弄懂一个函数；不是建立完美的训练计划，而是在今天完成一组动作。

> 好的练习，并不总是更用力。有时只是更清楚地知道自己正在做什么。

## 留下能回看的记录

一次技术练习可以只记三个字段：问题、尝试、观察。

```python
from datetime import date

practice = {
    "day": date.today().isoformat(),
    "question": "这个函数为什么需要边界检查？",
    "attempt": "写一个最小输入，再试一个空输入。",
    "observation": "先看失败，再理解假设。",
}

for key, value in practice.items():
    print(f"{key}: {value}")
```

## 下一次

如果下次打开记录时，能看见当时哪里不明白、后来哪里变得清楚，这次练习就已经有了用处。

| Current | Progress | Next |
| --- | --- | --- |
| 每次弄懂一个边界 | 能解释为什么失败 | 在另一个真实问题中重试 |
