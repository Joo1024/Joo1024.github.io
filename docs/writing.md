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

只要求标题和原始发布日期。其余字段按需要填写，省略时文章仍进入首页、存档、最近更新和全站 RSS。文件名决定默认地址 `/posts/a-question/`；标题、形式与标签变化不会改变 URL。文件名可以用简短英文或中文。

也可运行 `.tools/bin/hugo new content posts/a-question.md`。默认模板创建 `draft: true`；公开前删除此行或改为 `false`。预览草稿用 `.tools/bin/hugo server -D`，生产构建不发布草稿。

## 可选的四个维度

一篇文章可以同时涉及几个领域和方向，无需在文件夹之间选择。所有文章直接放在 `posts/`，不建立子目录。

```yaml
---
title: 练倒立时，想到的自由
date: 2026-10-02
type: practice
domains: [body, mind]
paths: [自在, 精进]
tags: [倒立, 自由]
---
```

| 字段 | 用途 | 示例 |
| --- | --- | --- |
| `type` | 单个写作形式 | reflection 随笔、note 短记、practice 实践记录、making 作品记录 |
| `domains` | 涉及的人生领域，平面数组 | `[mind, body]`；常用 mind/body/work/life/craft |
| `paths` | 长期愿意走下去的方向，平面数组 | `[明心, 自在]` |
| `tags` | 具体主题，平面数组 | `[AI, 死亡, 瓦尔登湖]` |

四个维度均可省略；数组可写成 `[]`。不要写 `domains: mind, body`，应写 `domains: [mind, body]`。不必建立“修炼/身体/力量/倒立”这样的层级，也不必把每篇文章贴满标签。

词汇开放。例如 `type: letter`、`domains: [friendship]`、`paths: [闲游]` 会直接生成对应索引，无需登记配置。常用英文词的中文显示别名保存在 `data/dimensions.yaml`，它不是白名单；新词原样显示。

阅读、行旅、年度回顾通常可使用 `type: reflection`，再加 `[阅读]`、`[行旅]` 或 `[年度回顾]` 主题。每年的回顾也只是一篇普通文章，例如 `posts/2026.md`，原始日期会让它自然进入对应年份的存档。

`/tags/` 集中展示非空维度；各维度也有独立索引：`/types/`、`/domains/`、`/paths/`。点击任意词条，按时间查看跨年份的文章。所有这些索引由 Hugo 原生生成，不需要维护文章名单。

## 其他 metadata

| 字段 | 含义 |
| --- | --- |
| `title` | 必填，中文或英文标题 |
| `date` | 必填，原始发布日；公开后不要为了更新而重写 |
| `lastmod` | 可选，最后实质更新日；省略时回退到 date |
| `description` | 可选，一句介绍，用于列表与 SEO；省略时使用站点描述 |
| `status` | 可选，`ongoing` 持续中或 `archived` 已归档；兼容旧 note/reflection 值 |
| `later_notes` | 可选后记，包含 `date` 与 Markdown `text` |
| `toc` | 默认展示可折叠目录；短文可设 `false` |
| `draft` | `true` 时不发布 |
| `sample` | 只用于示例文章；自己的记录移除 |
| `url` | 迁移文章的原发布地址，如 `/reflection/on-keeping-a-place/`；新文章通常省略 |
| `aliases` | 改公开地址时保留旧链接，如 `[/old-path/]` |

不用填写 `categories`。文章不再按目录分类，这个旧字段会明确报错，提示移除。

`archived` 不会隐藏文章。最后更新早于发布日、无效 status、后记日期晚于 lastmod、数组字段填写错误时，构建会明确报错。未来发布日期默认不发布，预览可加 `--buildFuture`。

## 三个固定单页

- `content/about.md`：关于此地与写作原则。
- `content/now.md`：近期投入与近况，有变化时再更新。
- `content/path.md`：简短的长期方向，允许方向改变或暂时放下。

Now、Path 更新时可以把旧片段追加到 `later_notes`，只修改 `lastmod`。近期行动留在 Now，Path 不需要待办、进度或固定回顾频率。

存档、最近更新和文字总页由 `content/_content.gotmpl` 生成，不需要另建 Markdown 索引。首页三个入口由 `data/sections.yaml` 管理；页首最近更新、存档、标签、关于由 `data/navigation.yaml` 管理。写新文章不需要改这些配置。

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

后记在正文末尾按时间排列，首页有旧文后记入口，最近更新按 lastmod 排序，存档按原始 date 分年。RSS 包含全文与后记，保留 pubDate 与唯一地址。部分阅读器会刷新旧条目，部分不会把后记视为新推送，定期查看最近更新更可靠。

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
[一篇旧文]({{< relref "posts/on-keeping-a-place.md" >}})
```

它会解析文章的公开地址，包括迁移时保留的旧 URL。普通 Markdown 相对链接也可使用；应以公开 URL 计算相对位置，而不是磁盘目录。HTML 默认不直接执行。

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

推送到 main 后 GitHub Actions 自动构建部署。新文章、新词条、归档和订阅自动更新。示例可逐步删除或替换，无需修改 CI；开发验收 `--examples` 仅在初始示例仍保留时使用。

## 迁移与订阅

既有九篇文章已经移动到 posts，并通过 `url` 保留原发布地址、RSS guid、日期和后记。此后不要因为整理元数据而更改这个字段。

旧栏目与分类网页根据 `data/legacy.yaml` 跳转到相应形式或主题，不出现在日常导航与 sitemap。旧 `index.xml` 继续输出对应维度的有效 RSS；“观心录”订阅如今对应随笔形式，也包含阅读、行旅和年度回顾中的随笔。最后一篇相关文字删除后，旧入口回退到相应维度索引。

全站订阅始终为 `/index.xml`。`/posts/index.xml`、四个维度及其词条都有独立订阅，阅读器中使用页面提供的 RSS 地址即可。原站 `?p=posts/hello.md` 也继续指向保留的 Hello World。
