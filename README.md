# Sanctum

A place for reflection, practice, and making.

一间用 Markdown 写作的数字书房。记录思考、练习、创作、阅读与行旅，沿着年份回看生活。允许旧文不成熟，允许判断改变；后来的想法追加在后记里。

## 为什么是 Hugo

| 方案 | 适合之处 | 本项目的取舍 |
| --- | --- | --- |
| Jekyll | GitHub Pages 原生支持，成熟、简单 | Ruby/Gem 工具链需要维护；自定义构建仍常用 Actions |
| **Hugo** | 单个二进制，内置分类、标签、目录、脚注、RSS、sitemap、代码高亮 | 选择；静态生成快，没有 npm、数据库或主题依赖 |
| Astro | 灵活的组件系统、现代前端生态 | 本站少交互，组件与 Node 依赖并非必需 |

Hugo 固定为 **0.147.9 标准版**。页面运行时只有 HTML、CSS 和一个小型配色脚本，不依赖外部 CDN 或字体。Markdown 文件可以随时迁移到其他工具；Hugo 专用 shortcode 仅用于内部链接。原生模板完全可修改，无需购买或更新主题。

## 本地运行

Linux/macOS 已有 Python 3、curl、tar 和 Bash 时：

```sh
bash scripts/install-hugo.sh
.tools/bin/hugo server --bind 127.0.0.1 -D
```

安装脚本从 Hugo 官方 GitHub Release 下载，验证官方 SHA256，重复运行会复用同版本二进制。Windows 可安装官方 Hugo **0.147.9**，然后运行 `hugo server -D`。本地默认端口 1313。生产不包含草稿：

```sh
.tools/bin/hugo --minify --cleanDestinationDir
python3 tests/check_site.py public
```

无需数据库、API key、CMS 或第三方账户。示例内容有明确标记，可替换或删除。Now、Path 是持续更新单页，其余七个栏目每篇文章一个文件。

## 目录

```text
.
├── hugo.toml                   # 站点地址、语言、Markdown 与输出配置
├── archetypes/default.md       # 新文章 metadata 模板
├── data/
│   ├── sections.yaml           # 栏目唯一配置：类型、名称、中文、描述与年份分组
│   └── navigation.yaml         # 全站导航：最近更新、存档、标签、关于
├── content/
│   ├── _content.gotmpl         # 自动生成栏目页，按目录继承分类
│   ├── now.md                 # 今朝
│   ├── path.md                # 道途，六个长期方向
│   ├── archive.md             # 按原始年份归档
│   ├── updates.md             # 最近更新与后记
│   ├── about.md               # 关于此地
│   ├── reflection/            # 观心录
│   ├── practice/              # 修炼录
│   ├── making/                # 造物录
│   ├── reading/               # 读书札记
│   ├── journey/               # 行旅录
│   ├── notes/                 # 杂记，保留原有 Hello World
│   └── yearly/                # 岁录
├── layouts/
│   ├── index.html             # 首页：九入口、四近作、旧文后记
│   ├── 404.html
│   ├── _default/
│   │   ├── baseof.html        # 页面骨架
│   │   ├── single.html        # 文章与持续更新页
│   │   ├── list.html          # 栏目、单个标签/分类
│   │   ├── terms.html         # 标签/分类索引
│   │   ├── archive.html       # 年份索引
│   │   ├── updates.html       # 最后更新时间索引
│   │   ├── rss.xml            # 全文订阅，包含后记
│   │   └── _markup/render-image.html
│   └── partials/              # metadata、导航、文章列表、后记
├── assets/css/main.css        # 排版与浅色/深色配色
├── assets/js/theme.js         # 配色选择与旧文章直链迁移
├── static/
│   ├── favicon.svg
│   └── images/                # 文章图片，原创山脊示意图
├── scripts/install-hugo.sh
├── tests/
│   ├── check_site.py          # Python 标准库生成结果与断链验收
│   ├── test_content.py        # 独立 Markdown 边界用例，不依赖示例文章
│   ├── test_sections.py       # 新栏目、分类推导、一致性与全站导航检查
│   └── browser_smoke.py       # 可选浏览器验收，开发依赖 Playwright
├── docs/
│   ├── writing.md             # 完整写作指南
│   └── superpowers/           # 设计、实施计划与验证记录
└── .github/workflows/pages.yml
```

栏目列表只维护在 `data/sections.yaml`：`kind: page` 是 Now、Path 这样的持续更新页；`kind: articles` 是文章栏目。Hugo 原生 content adapter 自动创建文章栏目页，并把目录名作为分类继承给文章；首页、归档、RSS、文章模板和 SEO 共用同一配置。无需给文章填写 `categories`，也无需手动创建栏目 `_index.md`。旧文章若保留 `categories`，其值必须是与目录一致的单项数组，否则构建报错，提示删去该字段。

Hugo 自动生成 `/tags/`、`/categories/`、`/sitemap.xml`、`/robots.txt`。生成的 `public/`、工具二进制和缓存不进入 Git。最近更新、存档、标签、关于统一位于所有页面的页首导航；页脚保留 RSS。

## 写下一篇

创建 `content/reflection/my-question.md`：

```markdown
---
title: 一个值得留下的问题
date: 2026-10-02
lastmod: 2026-10-02
description: 一句话介绍。
tags: [选择]
status: reflection
---

从一个真实的念头开始。

## 当时的想法

写下正文。
```

提交并推送到 `main`，发布会自动进行：

```sh
git add content/reflection/my-question.md
git commit -m "write: 一个值得留下的问题"
git push origin HEAD:main
```

更多 metadata、脚注、图片、后记、草稿与年度回顾见 [写作指南](docs/writing.md)。首页最近四篇、分类、标签、归档和 RSS 都自动更新。文件名决定 URL，标题修改不会造成断链。同栏目上一篇/下一篇按原始日期排列。

新增栏目也只需在 `data/sections.yaml` 注册一次，再写入对应目录；步骤见写作指南中的“新增栏目”。不再维护另一份文章栏目名单或逐栏目 URL 配置。

## GitHub Pages

1. 第一次在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。
2. 推送这些文件到 `main`。workflow 会下载并校验固定版本 Hugo，构建、检查本地链接，再上传并部署 Pages artifact。
3. 在 **Actions → Publish Sanctum** 查看构建和部署结果。

本仓库地址为 `https://joo1024.github.io/`。`hugo.toml` 保存 canonical 的默认地址；workflow 使用 Pages 实际 `base_url`，因此迁移到项目子路径也可发布。新域名或项目仓库要同步更新 `baseURL`；自定义域名另在 Pages 中设置 DNS 与域名，按 GitHub 文档配置 HTTPS。

无需保存个人 token：工作流使用 GitHub 提供的 `GITHUB_TOKEN`，部署 job 仅申请 Pages 与 OIDC 权限。修改本地文件和保存云配置并不代表站点已部署；以 Actions 成功记录和实际线上内容为准。

## 阅读、主题与隐私

- 米白/冷灰与炭灰配色；按钮循环 **系统 → 浅色 → 深色**，仅在浏览器本地保存配色。
- 无 JS 时，内容、目录、导航、索引、RSS 均可用，配色跟随系统。
- 中文和英文使用系统衬线字体，宽松行距，正文宽度 680px；手机自然换行。
- 原生 Markdown 目录、脚注、引用、代码高亮、表格、图片图注与懒加载。
- 基础 SEO：描述、canonical、Open Graph、BlogPosting 日期数据、sitemap、robots。
- 全站订阅 `/index.xml`，每个文章栏目也有自己的 `index.xml`。
- 无广告、统计、追踪、弹窗、登录、点赞、评论指标或社交分享组件。

旧站 `?p=posts/hello.md` 会跳转到新的 `/notes/hello-world/`。原始发布日期 2026-01-09 保留；迁移只补全了原文未闭合的代码围栏。旧站文章列表中不存在的 Git 速查页没有虚构补写。

## 验证与长期维护

```sh
# 所有实际文章、HTML 内部链接/锚点、RSS、SEO 等
python3 tests/check_site.py public

# 后记脚注、空后记与订阅相对地址回归
python3 -m unittest discover -s tests -p 'test_*.py' -v

# 首版示例仍保留时，额外验收脚注、目录、代码与后记
python3 tests/check_site.py public --examples

# 验证项目站子路径
.tools/bin/hugo --minify --baseURL https://example.com/sanctum/ --destination /tmp/sanctum-build
python3 tests/check_site.py /tmp/sanctum-build --base-path /sanctum/
```

可选浏览器检查需要 Python Playwright 与 Chromium；它们只用于开发验证，不是站点运行或发布依赖，命令见脚本说明。升级 Hugo 时更新安装脚本版本，重新构建并检查；没有 npm/Gem 依赖需要定期更新。文章与图片随 Git 历史保存，建议再保留离线备份。静态输出可以复制到任何普通 Web 服务器。
