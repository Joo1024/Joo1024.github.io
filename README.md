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

无需数据库、API key、CMS 或第三方账户。示例内容有明确标记，可替换或删除。About、Now、Path 是固定单页；所有文章统一放在 `content/posts/`，不按主题分文件夹。时间是经，标签是纬。

## 目录

```text
.
├── hugo.toml                   # 站点地址、语言、Markdown 与输出配置
├── archetypes/default.md       # 新文章 metadata 模板
├── data/
│   ├── sections.yaml          # 今朝、道途、文字三个入口
│   ├── dimensions.yaml        # 四个维度的显示名，常用词中文别名（非词汇白名单）
│   ├── legacy.yaml            # 历史栏目与分类入口的兼容映射
│   └── navigation.yaml        # 全站导航：最近更新、存档、标签、关于
├── content/
│   ├── _content.gotmpl        # 生成文章总页、存档、更新及兼容入口
│   ├── now.md                 # 今朝
│   ├── path.md                # 道途，简短的长期方向
│   ├── about.md               # 关于此地
│   └── posts/                 # 每篇文章一个 Markdown 文件，含原有 Hello World
├── layouts/
│   ├── index.html             # 首页：三入口、四近作、旧文后记
│   ├── 404.html
│   ├── _default/
│   │   ├── baseof.html        # 页面骨架
│   │   ├── single.html        # 文章与持续更新页
│   │   ├── list.html          # 全部文章、维度词条
│   │   ├── terms.html         # 多维标签总览与各维度索引
│   │   ├── archive.html       # 年份索引
│   │   ├── updates.html       # 最后更新时间索引
│   │   ├── rss.xml            # 全文订阅，包含后记
│   │   ├── legacy.html        # 旧入口自动跳转与无 JS 阅读链接
│   │   └── _markup/render-image.html
│   └── partials/              # 内容校验、metadata、导航、文章列表、后记
├── assets/css/main.css        # 排版与浅色/深色配色
├── assets/js/theme.js         # 配色选择与旧文章直链迁移
├── static/
│   ├── favicon.svg
│   └── images/                # 文章图片，原创山脊示意图
├── scripts/install-hugo.sh
├── tests/
│   ├── check_site.py          # Python 标准库生成结果与断链验收
│   ├── test_content.py        # 独立 Markdown 边界用例，不依赖示例文章
│   ├── test_metadata.py       # 可选字段、跨维度索引、旧订阅与空集合回归
│   ├── hugo_helpers.py        # 独立测试共用的真实 Hugo 构建与内容初始化
│   └── browser_smoke.py       # 可选浏览器验收，开发依赖 Playwright
├── docs/
│   ├── writing.md             # 完整写作指南
│   └── superpowers/           # 设计、实施计划与验证记录
└── .github/workflows/pages.yml
```

日常只编辑三个固定单页和 `posts/*.md`。文章只要求 `title` 与原始 `date`，无需填写 `categories`、注册栏目或创建 `_index.md`。所有公开文章自动进入首页、归档、最近更新与全站 RSS；相邻文章沿全部文字的时间顺序排列。

可选元数据：`type` 是单个形式（如 reflection/note/practice/making），`domains` 是人生领域数组，`paths` 是长期方向数组，`tags` 是具体主题数组。词汇开放，新增值就会生成索引，不需要修改配置；数组留空或省略都可以。阅读、行旅与年度回顾通过主题标签关联。不要建立复杂的层级，也不必给每篇文章填满四个维度。

Hugo 原生生成 `/types/`、`/domains/`、`/paths/`、`/tags/` 与各词条页；`/tags/` 集中展示所有非空维度。`/archive/`、`/updates/` 由 content adapter 自动生成。旧 `/categories/` 与七个栏目只保留兼容入口，不再是内容分类。`public/`、工具二进制和缓存不进入 Git。页首导航统一，页脚保留 RSS。

## 写下一篇

创建 `content/posts/my-question.md`：

```markdown
---
title: 一个值得留下的问题
date: 2026-10-02
---

从一个真实的念头开始。

## 当时的想法

写下正文。
```

提交并推送到 `main`，发布会自动进行：

```sh
git add content/posts/my-question.md
git commit -m "write: 一个值得留下的问题"
git push origin HEAD:main
```

更多 metadata、脚注、图片、后记、草稿与年度回顾见 [写作指南](docs/writing.md)。新文章地址默认为 `/posts/my-question/`，修改标题、形式或标签不会改变它。既有文章显式保留原 URL；移动后的文件路径与公开地址可以不同。

## GitHub Pages

1. 第一次在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。
2. 推送这些文件到 `main`。workflow 会下载并校验固定版本 Hugo，构建、检查本地链接，再上传并部署 Pages artifact。
3. 在 **Actions → Publish Sanctum** 查看构建和部署结果。

本仓库地址为 `https://joo1024.github.io/`。`hugo.toml` 保存 canonical 的默认地址；workflow 使用 Pages 实际 `base_url`，因此迁移到项目子路径也可发布。新域名或项目仓库要同步更新 `baseURL`；自定义域名另在 Pages 中设置 DNS 与域名，按 GitHub 文档配置 HTTPS。

无需保存个人 token：工作流使用 GitHub 提供的 `GITHUB_TOKEN`，部署 job 仅申请 Pages 与 OIDC 权限。修改本地文件和保存云配置并不代表站点已部署；以 Actions 成功记录和实际线上内容为准。

## 阅读、主题与隐私

- 中性近白与炭灰配色；墨绿只点缀品牌，蓝色用于链接和交互状态。按钮循环 **系统 → 浅色 → 深色**，仅在浏览器本地保存配色。
- 无 JS 时，内容、目录、导航、索引、RSS 均可用，配色跟随系统。
- 站点名、标题、正文与导航统一使用系统无衬线，代码使用等宽字体；通过字号、字重与留白区分层级。栏目中文为主、英文为辅。正文 17–18px、行高 1.8、宽度 680px；导航与说明 13–14px，日期至少 12px。
- 原生 Markdown 目录、脚注、引用、代码高亮、表格、图片图注与懒加载。
- 基础 SEO：描述、canonical、Open Graph、BlogPosting 日期数据、sitemap、robots。
- 全站订阅 `/index.xml`；文章总页、各维度及各词条也有 `index.xml`。旧栏目与分类订阅地址继续返回有效 RSS。
- 无广告、统计、追踪、弹窗、登录、点赞、评论指标或社交分享组件。

旧站 `?p=posts/hello.md` 会跳转到新的 `/notes/hello-world/`。原始发布日期 2026-01-09 保留；迁移只补全了原文未闭合的代码围栏。旧站文章列表中不存在的 Git 速查页没有虚构补写。

## 验证与长期维护

```sh
# 所有实际文章、HTML 内部链接/锚点、RSS、SEO 等
python3 tests/check_site.py public

# 多维索引、最简文章、旧订阅、后记脚注等独立回归
python3 -m unittest discover -s tests -p 'test_*.py' -v

# 首版示例仍保留时，额外验收脚注、目录、代码与后记
python3 tests/check_site.py public --examples

# 验证项目站子路径
.tools/bin/hugo --minify --baseURL https://example.com/sanctum/ --destination /tmp/sanctum-build
python3 tests/check_site.py /tmp/sanctum-build --base-path /sanctum/
```

可选浏览器检查需要 Python Playwright 与 Chromium；它们只用于开发验证，不是站点运行或发布依赖，命令见脚本说明。升级 Hugo 时更新安装脚本版本，重新构建并检查；没有 npm/Gem 依赖需要定期更新。文章与图片随 Git 历史保存，建议再保留离线备份。静态输出可以复制到任何普通 Web 服务器。
