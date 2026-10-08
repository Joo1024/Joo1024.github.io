# 在 Sanctum 写作

原始念头可以留在 flomo、卡片日记或任何地方。准备公开时，整理成 Markdown，放进 `content/posts/`，提交到 Git；无需进入 CMS。

时间是经，标签是纬。档案可以有空白，生活不需要为档案服务。

## 最简单的一篇

创建 `content/posts/a-question.md`：

```markdown
---
title: 一个还没有答案的问题
date: 2026-10-02
---

从一个真实的念头开始。
```

只要求标题和原始发布日期。其余字段按需要填写，文章自动进入文字列表、存档和全站 RSS，填写的维度会生成分类索引；首页展示最近五篇。文件名决定地址 `/posts/a-question/`；标题、形式与标签变化不会改变 URL。文件名可以用简短英文或中文。

也可运行 `.tools/bin/hugo new content posts/a-question.md`。默认模板创建 `draft: true`；公开前删除此行或改为 `false`。预览草稿用 `.tools/bin/hugo server -D`，生产构建不发布草稿。

## 可选的四个维度

一篇文章可以同时涉及几个领域和方向，无需在文件夹之间选择。所有文章直接放在 `posts/`，不建立子目录。

```yaml
---
title: 练倒立时，想到的自由
date: 2026-10-02
form: practice
domains: [body, mind]
paths: [自在, 精进]
tags: [倒立, 自由]
---
```

| 字段 | 用途 | 示例 |
| --- | --- | --- |
| `form` | 单个写作形式 | reflection 随笔、note 短记、practice 实践记录、making 作品记录 |
| `domains` | 涉及的人生领域，平面数组 | `[mind, body]`；常用 mind/body/work/life/craft |
| `paths` | 长期愿意走下去的方向，平面数组 | `[明心, 自在]` |
| `tags` | 具体主题，平面数组 | `[AI, 死亡, 瓦尔登湖]` |

四个维度均可省略；数组可写成 `[]`。不要写 `domains: mind, body`，应写 `domains: [mind, body]`。不必建立“修炼/身体/力量/倒立”这样的层级，也不必把每篇文章贴满标签。

词汇开放。例如 `form: letter`、`domains: [friendship]`、`paths: [闲游]` 会直接生成对应索引，无需登记配置。常用英文词的中文显示别名保存在 `data/dimensions.yaml`，它不是白名单；新词原样显示。

阅读、行旅、年度回顾通常可使用 `form: reflection`，再加 `[阅读]`、`[行旅]` 或 `[年度回顾]` 主题。每年的回顾也只是一篇普通文章，例如 `posts/2026.md`，原始日期会让它自然进入对应年份的存档。

`/tags/` 集中展示非空维度；各维度也有独立索引：`/forms/`、`/domains/`、`/paths/`。点击任意词条，按时间查看跨年份的文章。所有这些索引由 Hugo 原生生成，不需要维护文章名单。

Hugo 的 `type` 是保留字段，会参与内容类型和模板选择。文章形式改用 `form`；旧的 `type` 写法会给出迁移提示。本站使用下面的原生配置，让单值 `form` 直接进入索引：

```toml
[taxonomies]
form = 'form'
domain = 'domains'
path = 'paths'
tag = 'tags'

[permalinks.taxonomy]
form = '/forms/'
[permalinks.term]
form = '/forms/:slug/'
```

taxonomy 配置右侧是 Hugo 读取的 metadata 字段名；写成 `form = 'forms'` 会读取 `forms`，无法索引这里的单值 `form`。公开地址统一使用 `/forms/`，无需额外转换或重复字段。

## 其他 metadata

| 字段 | 含义 |
| --- | --- |
| `title` | 必填，中文或英文标题 |
| `date` | 必填，原始发布日；公开后不要为了更新而重写 |
| `lastmod` | 可选，最后实质更新日；省略时回退到 date |
| `description` | 可选，一句介绍，用于页眉、文章列表与 SEO；省略时不显示介绍，SEO 使用站点描述 |
| `status` | 可选，`ongoing` 持续中或 `archived` 已归档；note/reflection 属于 form |
| `later_notes` | 可选后记，包含 `date` 与 Markdown `text` |
| `toc` | 默认展示可折叠目录；短文可设 `false` |
| `draft` | `true` 时不发布 |

不用填写 `categories`。文章不再按目录分类，这个旧字段会明确报错，提示移除。

`archived` 不会隐藏文章。最后更新早于发布日、无效 status、后记日期晚于 lastmod、数组字段填写错误时，构建会明确报错。未来发布日期默认不发布，预览可加 `--buildFuture`。

## 修行单页与关于

- `content/now.md`：近期投入与近况，有变化时再更新。
- `content/path.md`：长期方向与功法，允许方向改变或暂时放下。
- `content/realms.md`：当前境界与修为，记录跨时间、跨场景沉淀的能力。
- `content/roots.md`：自身禀赋与自然倾向，有新的认识时再更新。
- `content/about.md`：关于自己与 Sanctum。

Now、Path 更新时可以把旧片段追加到 `later_notes`，只修改 `lastmod`。近期行动留在 Now，Path 不需要待办、进度或固定回顾频率。

修行总览 `/cultivation/`、文字列表 `/posts/` 和存档 `/archive/` 由 `content/_content.gotmpl` 在构建时创建，不需要另建 Markdown 索引。修行总览复用文字列表的模板，名单与顺序由 `data/sections.yaml` 管理，标题和更新时间来自对应 Markdown。配置项对应的页面必须存在；文件缺失或配置拼写错误会使构建报错。

文字列表和存档自动读取 posts。首页直接读取 Now 的近况，展示最近五篇文章，并提供修行总览、全部文字两个入口。`data/navigation.yaml` 管理修行、文字、关于三个顶级导航；`data/post_navigation.yaml` 管理文字区域的全部文字、存档、分类三个二级导航。写新文章不需要改这些配置。

## 观点改变：追加后记

保留正文与 `date`，在 metadata 中追加：

```yaml
lastmod: 2027-03-21
later_notes:
  - date: 2027-03-21
    text: |
      半年后回看，对这件事有了不同理解。

      **现在的判断**写在这里，过去的文字仍留在正文中。
```

后记在正文末尾按时间排列。首页展示最近追加后记的一篇旧文入口；文字列表和存档仍按原始 `date` 排序，存档按原始 `date` 分年。RSS 包含全文与后记，保留 `pubDate` 与唯一地址。部分阅读器会刷新旧条目，部分不会把后记视为新推送，可从首页入口查看。

## Markdown

用 `##`、`###` 组织正文；文章标题由模板渲染，不必再写 `#`。

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

图片放在 `static/images/`，模板自动加懒加载、替代文字与可选图注。建议压缩照片，长边 1600px 左右，使用 WebP 或 JPEG；原图另存，提交前自行去除不希望公开的 EXIF 信息。

内部链接推荐使用 Hugo shortcode，构建时检查目标是否存在：

```markdown
[一篇旧文]({{< relref "posts/on-attachment.md" >}})
```

它会解析为文章的 `/posts/文件名/` 地址。普通 Markdown 相对链接也可使用；应以公开 URL 计算相对位置，而不是磁盘目录。HTML 默认不直接执行。

## 一次发布

```sh
# 可选：本地预览
.tools/bin/hugo server -D

# 验证生产输出
.tools/bin/hugo --minify --cleanDestinationDir
python3 tests/check_site.py public

git add content/posts/a-question.md
git commit -m "write: 一个还没有答案的问题"
git push origin HEAD:main
```

推送到 main 后 GitHub Actions 自动构建、检查并部署。新文章、新词条、归档和订阅自动更新。CI 会运行站点检查、Markdown 回归与浏览器检查；任何一项失败都不会发布。浏览器依赖安装与本地运行方法见 [README](../README.md#配置与检查)。

## 地址与订阅

文章公开地址统一为 `/posts/文件名/`，不填写 `url` 或 `aliases`。重命名文件会改变公开地址，修改标题、形式与标签不会。

文章链接、RSS 条目与 sitemap 使用同一个公开地址。RSS 的 guid 也使用该地址；发布日期由原始 `date` 决定，正文与后记更新不会改变它。

全站订阅为 `/index.xml`。`/posts/index.xml`、四个维度及其词条都有独立订阅，阅读器中使用页面提供的 RSS 地址即可。
