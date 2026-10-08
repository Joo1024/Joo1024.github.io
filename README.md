# Sanctum

一个人在时间中留下修行痕迹的地方。

[网站](https://joo1024.github.io/) · [RSS](https://joo1024.github.io/index.xml) · [写作指南](docs/writing.md)

基于 Hugo 的个人静态网站，部署于 GitHub Pages。用 Markdown 留下思考、练习、创作与生活记录，随 Git 保存。支持目录、脚注、后记与深浅配色，没有广告和访问追踪。

## 内容结构

四个修行单页、一页关于；文章沿时间积累，用四种可选坐标检索。

| 位置 | 内容 |
| --- | --- |
| [content/now.md](content/now.md) | 当前投入与近况 |
| [content/path.md](content/path.md) | 长期方向与功法 |
| [content/realms.md](content/realms.md) | 当前境界与修为 |
| [content/roots.md](content/roots.md) | 自身禀赋与自然倾向 |
| [content/about.md](content/about.md) | 关于自己与 Sanctum |
| [content/posts/](content/posts/) | 按时间积累的文章，每篇一个 Markdown 文件 |

文章直接放在 `content/posts/`，不按主题建立子目录。只需填写 `title` 和原始发布日期 `date`；`form` 表示形式，`domains` 表示领域，`paths` 表示方向，`tags` 表示主题，均可省略。`form` 是单值，其余三个维度是数组。

修行总览、文字列表、存档、分类与 RSS 自动生成，首页读取 Now 的近况并展示最近五篇文章。顶级导航是修行、文字、关于；文字下有全部文字、存档、分类三个入口。旧文实质更新时填写 `lastmod`，观点变化时可追加 `later_notes`，保留当时的文字。具体格式见[写作指南](docs/writing.md)。

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
- [data/sections.yaml](data/sections.yaml)：修行总览的页面名单与顺序；引用的页面必须存在，否则构建报错。
- [data/navigation.yaml](data/navigation.yaml)、[data/post_navigation.yaml](data/post_navigation.yaml)：顶级导航与文字区域的二级导航。
- [data/dimensions.yaml](data/dimensions.yaml)：维度名称与常用词的显示别名。
- [layouts/](layouts/)、[assets/](assets/)：模板、样式与配色脚本。

本地检查生产输出与回归用例：

```sh
.tools/bin/hugo --minify --cleanDestinationDir
python3 tests/check_site.py public
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Hugo 版本由[安装脚本](scripts/install-hugo.sh)固定。升级时更新脚本并运行上述检查；`public/` 是生成目录，不提交到 Git。

浏览器检查使用 [requirements-browser.txt](requirements-browser.txt) 固定的 Playwright，以及该版本配套的 Chromium。首次安装：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-browser.txt
.venv/bin/python -m playwright install --with-deps --only-shell chromium
```

完成上面的生产构建后，在一个终端启动本地服务：

```sh
python3 -m http.server 8001 --bind 127.0.0.1 --directory public
```

在另一个终端运行检查：

```sh
.venv/bin/python -u tests/browser_smoke.py --url http://127.0.0.1:8001
```

覆盖 320–1440px 的响应式布局、导航、配色切换与持久化、打印、无 JavaScript 和存储受限场景。可加 `--screenshots /tmp/sanctum-shots` 保存截图，或用 `--chromium /path/to/chromium` 指定已有浏览器。CI 使用 Playwright 配套的 Chromium；这些检查与站点及 Markdown 回归检查均在上传部署产物之前运行，失败会阻止发布。
