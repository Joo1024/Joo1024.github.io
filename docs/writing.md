# 在 Sanctum 写作

原始念头可以留在 flomo、卡片日记或任何地方。准备公开时，把它整理为 Markdown，放进对应栏目，提交到 Git；无需进入 CMS。

## 一篇新的文章

直接创建 `content/reflection/a-question.md`，例如：

```yaml
---
title: 一个还没有答案的问题
date: 2026-10-02
lastmod: 2026-10-02
description: 用一句话记下文章从哪里开始。
categories: [reflection]
tags: [选择, 自我理解]
status: reflection
---
```

正文从 front matter 之后开始。无需登记文章列表。文件名决定永久地址（此例 `/reflection/a-question/`），中文标题、日期或标签变化不会改变 URL。尽量使用简短的英文文件名；中文文件名也可使用，链接会编码。

也可运行 `.tools/bin/hugo new content reflection/a-question.md`。默认模板创建 `draft: true`；公开前删除此行或改为 `false`。预览草稿用 `.tools/bin/hugo server -D`，生产构建不发布草稿。

## Metadata

| 字段 | 含义与要求 |
| --- | --- |
| `title` | 中文或英文标题 |
| `date` | 原始发布日；一旦公开不要为了更新而重写 |
| `lastmod` | 最后实质更新日；初次发布与 date 相同；省略时回退到 date |
| `description` | 一句描述，用于列表、SEO 与分享链接预览 |
| `categories` | 栏目 slug 数组，如 `[practice]`，自动进入分类索引 |
| `tags` | 可选，多主题数组，如 `[技术, 方法]`；不必太多 |
| `status` | 必填：`note`、`reflection`、`ongoing`、`archived` |
| `later_notes` | 可选后记列表，字段为 `date` 与 Markdown `text` |
| `toc` | 默认展示可折叠目录；短文可设 `false` |
| `draft` | 可选；`true` 时不发布 |
| `sample` | 只给演示文章用；自己的记录请移除 |
| `aliases` | 可选旧地址数组，如 `[/old-path/]`，改文件名时用于保留链接 |

`archived` 代表已存档，不会从网站隐藏。`ongoing` 是仍在进行的记录，不代表进度或等级。最后更新早于原始日期、无效状态、后记日期晚于 lastmod 时，构建会明确报错。未来发布日期不会在普通构建中发布，预览时可加 `--buildFuture`。

## 放在哪个栏目

| 路径 | 记录 |
| --- | --- |
| `content/now.md` | 最近几个月的近况；单页持续更新 |
| `content/path.md` | Mind / Body / Craft / Work / Making / Life；单页持续更新 |
| `content/reflection/` | 人生、价值、选择、自我理解 |
| `content/practice/` | 技术、身体、技能、工作方法 |
| `content/making/` | 做出的 App、工具、代码、小说或作品 |
| `content/reading/` | 书引起的想法、同意与不同意 |
| `content/journey/` | 自然、骑行、旅行、城市与生活环境 |
| `content/notes/` | 100–500 字的小想法和短记录 |
| `content/yearly/` | 年度回顾，例如 `2026.md`；可以一年数篇 |

`_index.md` 是栏目介绍，不是文章，不要覆盖它。Now 与 Path 可在更新时把旧片段追加到 later_notes，也可放到对应年份的岁录中。只更新 `lastmod`，不用给这两页新增文章日期。

## 观点改变：追加后记

保留正文与 `date`。在 metadata 中追加：

```yaml
lastmod: 2027-03-21
later_notes:
  - date: 2027-03-21
    text: |
      半年后回看，对这件事有了不同理解。

      **现在的判断**写在这里，过去的文字仍留在正文中。
```

后记在正文末尾按时间排列，首页有旧文后记入口，最近更新页按 lastmod 排序。Archive 始终按 date 的年份归档。RSS 包含全文与后记，pubDate 和文章唯一地址保留；部分阅读器会刷新旧条目，部分不会把后记视为新推送，定期查看“最近更新”更可靠。

## Markdown

用 `##`、`###` 组织正文；文章标题已经由模板渲染，不必再写 `#`。

````markdown
## 一个问题

中文正文与 English text 可以自然混排。

> 引用一段需要慢慢想的话。

```python
print("small steps")
```

这是带脚注的判断。[^1]

[^1]: 脚注可以记录来源、限制或后来想到的细节。

![描述图片的内容](/images/my-walk.jpg "拍摄时间或简短图注")
````

图片放到 `static/images/`，Markdown 引用 `/images/...`。模板自动加懒加载、替代文字与可选图注；建议先压缩照片，长边 1600px 左右，使用 WebP 或 JPEG。原始照片另行保存，提交前自行去除不希望公开的地理位置等 EXIF 信息。本站不会进行远程图片上传或变换。

内部文章链接推荐用 Hugo shortcode，构建时会检查目标是否存在：

```markdown
[一篇旧文]({{< relref "reflection/on-keeping-a-place.md" >}})
```

如不想绑定 Hugo，普通 Markdown 相对链接也能使用；保留地址路径即可。HTML 默认不直接执行，避免在文章中嵌入脚本。

## 一次发布

```sh
# 本地预览，可省略
.tools/bin/hugo server -D

# 验证生产输出
.tools/bin/hugo --minify --cleanDestinationDir
python3 tests/check_site.py public

# 仅提交自己的文章与图片
git add content/reflection/a-question.md
git commit -m "write: 一个还没有答案的问题"
git push origin HEAD:main
```

推送到 main 后 GitHub Actions 构建并部署。第一次需在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**，无须 API token。Actions 失败时查看构建或验证步骤，不要绕过检查。

首批示例可自由删除或替换，无需修改 CI。通用验收会检查所有实际生成的文章、订阅与本地链接。开发时可用 `python3 tests/check_site.py public --examples` 额外验证初始示例中的脚注、目录、代码和后记；此选项不用于生产发布。
