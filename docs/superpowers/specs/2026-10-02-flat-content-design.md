# 扁平内容与多维索引

用户已评估并同意本方案。日常内容只维护 `about.md`、`now.md`、`path.md` 和 `posts/*.md`；归档与更新页由 Hugo content adapter 生成。首页保留今朝、道途、文字三个入口。

所有文章共用 `posts/`。`title`、原始 `date` 必填；`type` 为可选单值形式，`domains`、`paths`、`tags` 为可选平面字符串数组。词汇开放，不需要注册；常用词只有可选的中文显示名称。`status` 可选，兼容旧值，日常只用 ongoing/archived。lastmod 默认 date，后记保留。

用 Hugo 原生 taxonomy：form = type、domain = domains、path = paths、tag = tags；形式索引通过 permalink 输出到 `/types/`。标签首页集中展示四个维度，原生各维度及各词条页支持独立 RSS。空维度不出现在总索引中。文章相邻导航沿全部文章的时间顺序排列。

既有文章移动到 posts 时填写原 URL，保留正文、图片、原始日期、更新日、后记和 RSS guid。reflection/reading/journey/yearly 迁移为 reflection（后三类增加阅读/行旅/年度回顾主题）；notes 为 note；practice 和 making 保留对应形式。仅示例文章演示 domains/paths，不为真实 Hello World 虚构个人方向。

旧栏目及分类入口作为不进入日常列表和 sitemap 的兼容页面，跳转到对应形式或主题；旧 index.xml 输出该维度的有效 RSS。目标词条删除后回退到对应维度总索引，不产生断链。全站 RSS 始终包含所有公开文章一次。

Path 改为短段落的长期方向，不保留 Current/Progress/Next 和定期任务；Now 不规定更新频率。示例保留明确标记，About 增加“档案可以有空白，生活不需要为档案服务”。

保持 Hugo 0.147.9、GitHub Pages Actions、现有无衬线与中性配色，无新增运行时依赖、数据库、搜索插件或树状分类。
