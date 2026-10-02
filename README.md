# Sanctum

一个人在时间中留下修行痕迹的地方。

[网站](https://joo1024.github.io/) · [RSS](https://joo1024.github.io/index.xml) · [写作指南](docs/writing.md)

基于 Hugo 的个人静态网站，部署于 GitHub Pages。用 Markdown 留下思考、练习、创作与生活记录，随 Git 保存。支持目录、脚注、后记与深浅配色，没有广告和访问追踪。

## 内容结构

三个常驻页面，一条时间长河，四种可选坐标。

| 位置 | 内容 |
| --- | --- |
| [content/about.md](content/about.md) | 关于自己与 Sanctum |
| [content/now.md](content/now.md) | 当前投入与近况 |
| [content/path.md](content/path.md) | 愿意长久走下去的方向 |
| [content/posts/](content/posts/) | 按时间积累的文章，每篇一个 Markdown 文件 |

文章直接放在 `content/posts/`，不按主题建立子目录。只需填写 `title` 和原始发布日期 `date`；`form` 表示形式，`domains` 表示领域，`paths` 表示方向，`tags` 表示主题，均可省略。`form` 是单值，其余三个维度是数组。

文章索引、存档、最近更新、标签与 RSS 自动生成，首页展示最近几篇。旧文实质更新时填写 `lastmod`，观点变化时可追加 `later_notes`，保留当时的文字。具体格式见[写作指南](docs/writing.md)。

## 本地预览

Linux/macOS 需要 Bash、curl、tar 和 Python 3。安装脚本下载并校验固定版本的 Hugo：

```sh
bash scripts/install-hugo.sh
.tools/bin/hugo server --bind 127.0.0.1 -D
```

打开 <http://127.0.0.1:1313/>。`-D` 用于预览草稿；正式构建不发布草稿或未来日期的文章。

## 写作与发布

创建 `content/posts/a-question.md`：

```markdown
---
title: 一个值得留下的问题
date: 2026-10-02
---

正文写在这里。
```

提交并推送到 `main`：

```sh
git add content/posts/a-question.md
git commit -m "write: 一个值得留下的问题"
git push origin HEAD:main
```

本仓库已启用 GitHub Actions 部署。[发布工作流](.github/workflows/pages.yml)会自动构建、检查并发布；在 [Actions](https://github.com/Joo1024/Joo1024.github.io/actions) 查看结果。

迁移到新仓库时，将 **Settings → Pages → Source** 设为 **GitHub Actions**；更换公开地址时，同步更新 `hugo.toml` 中的 `baseURL`。

## 配置与检查

- [hugo.toml](hugo.toml)：站点地址、语言与构建配置。
- [data/sections.yaml](data/sections.yaml)、[data/navigation.yaml](data/navigation.yaml)：首页入口与全站导航。
- [data/dimensions.yaml](data/dimensions.yaml)：维度名称与常用词的显示别名。
- [layouts/](layouts/)、[assets/](assets/)：模板、样式与配色脚本。

本地检查生产输出与回归用例：

```sh
.tools/bin/hugo --minify --cleanDestinationDir
python3 tests/check_site.py public
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Hugo 版本由[安装脚本](scripts/install-hugo.sh)固定。升级时更新脚本并运行上述检查；`public/` 是生成目录，不提交到 Git。
