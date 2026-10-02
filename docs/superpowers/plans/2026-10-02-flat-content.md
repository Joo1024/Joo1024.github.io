# Flat Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 一个文章目录、时间归档和四个可选维度，保留旧文章与订阅地址。

**Architecture:** Hugo 原生 taxonomy 接收 type/domains/paths/tags；content adapter 生成文章总页、系统索引与旧入口。模板共用文章集合、维度名称与兼容目标解析。

**Tech Stack:** Hugo 0.147.9、Markdown/YAML、Python 标准库验收、可选 Playwright。

**Spec:** `docs/superpowers/specs/2026-10-02-flat-content-design.md`（用户已批准对话中的方案并要求继续）。执行方式：当前会话直接实施。

## Global Constraints

- 文章统一放入 `content/posts/*.md`；type/domains/paths/tags 均可选。
- 无新增运行时依赖；保留既有 URL、date、lastmod、正文与后记。
- 形式索引 `/types/`，其余 `/domains/`、`/paths/`、`/tags/`。
- 词汇开放；status 仅在需要时填写；空维度自然留白。

## Review Focus

- 只有 title/date 的文章仍进入首页、存档、更新与 RSS，草稿/未来文章不发布。
- 新形式、新领域和中文方向无须登记，能正确索引及订阅。
- 旧入口的目标词条不存在时不产生断链；旧订阅仍是有效 XML。
- 数组字段填成字符串明确报错；嵌套文章目录不能静默遗漏。
- 旧 URL 与项目子路径的 canonical、RSS guid、图片和脚注链接保持正确。

### Task 1: 原生多维索引与兼容入口

**Files:** tests/test_metadata.py, tests/test_content.py, hugo.toml, data/sections.yaml, data/dimensions.yaml, data/legacy.yaml, content/_content.gotmpl, layouts/partials/*, layouts/_default/{single,list,terms,rss,legacy}.html.

**Interfaces:** entries(Page) 返回公开 posts 文章；dimension(key) 返回显示配置；term-label({key,term}) 返回显示名；legacy-target(Page) 返回有效目标 Page；feed-pages(Page) 返回订阅集合。

- [x] 写独立 Hugo 用例：跨维度索引、可选字段、自由词汇、无个人方向、字段形状、日期、草稿、旧 URL、旧订阅与空集合。
- [x] 运行用例，确认新行为失败。
- [x] 配置原生 taxonomy 与 type permalink；生成 posts、archive、updates 和旧入口；实现共享索引/订阅/验证模板。
- [x] 运行测试至全部通过，检查旧词条缺失的回退行为。

### Task 2: 内容与写作流程迁移

**Files:** content/posts/*.md, content/{now,path,about}.md, archetypes/default.md, README.md, docs/writing.md, tests/{check_site,browser_smoke}.py.

**Interfaces:** 所有迁移文章的 url 保持原地址；新文章默认 `/posts/<filename>/`；目录不再决定主题。

- [x] 移动九篇文章并保留旧 URL，按形式和主题映射，仅示例演示 domains/paths。
- [x] 简化 Now/Path；把系统索引 metadata 移入生成器；更新完整目录、最简写作步骤和元数据说明。
- [x] 更新已改变的浏览器导航断言；构建并核对旧 RSS 的全部 guid/pubDate/正文与后记。

### Task 3: 验证、审查与发布

- [x] 构建根路径及 `/sanctum/` 子路径，运行 check_site 与全部独立用例。
- [x] 浏览器检查首页、四维索引、中文词条、旧入口跳转、无 JS、相邻文章、目录后记及 320–1440px 深浅模式。
- [x] 审查 staged diff、旧订阅、空维度与无元数据情况，修正实际缺陷。
- [ ] 提交并推送 main，确认该提交的 Publish Sanctum 构建与部署成功。

## Verification Record

- 根路径和 `/sanctum/` 子路径均构建通过；各 65 个 HTML 页面与 9 篇文章通过链接、RSS、sitemap、SEO、目录和后记检查。
- 14 项独立回归通过，包括真实固定页在删除所有示例后仍可构建，以及根目录误放文章会明确报错。
- 浏览器 smoke 验证通过；另检查四个尺寸、深浅配色下的 88 次页面布局、中文方向链接、九个旧入口和无 JS 跳转。
- 原九篇 RSS 条目的标题、地址、GUID、发布日期与全文逐项一致。
- 独立审查发现的两个 P2 已修正并经复查确认；无剩余发现。
