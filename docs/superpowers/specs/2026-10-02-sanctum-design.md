# Sanctum 设计

目标：一个长期有人居住、写作、阅读的数字洞府。内容优先于装饰，可维护性优先于炫技，长期稳定优先于短期流行。

## 技术选择

选择 Hugo 0.147.9 标准版，使用原生 HTML 模板、CSS、少量原生 JavaScript。Jekyll 的 Pages 集成很方便，但需要 Ruby 与 Gem 依赖；Astro 的组件与客户端生态对本项目并非必要。Hugo 单个二进制提供 Markdown、脚注、目录、离线代码高亮、taxonomy、RSS、sitemap，不需要主题仓库、npm、数据库或在线 CMS。用 GitHub Actions 构建并部署 GitHub Pages。

## 页面与内容

- 首页：Sanctum、副标题、九个文字栏目入口、四篇最近文章和一条旧文后记。
- Now、Path：独立持续更新的 Markdown 页面；Path 包含 Mind / Body / Craft / Work / Making / Life，每项记录 Current / Progress / Next。
- Reflection、Practice、Making、Reading、Journey、Notes、Yearly：Markdown 栏目列表与文章。Yearly 以年份组织。
- Archive：按原始年份分组；另设最近更新页、分类页和标签页。所有索引在构建时生成，新文章不需要手动注册。
- 文章 front matter：title、date、lastmod、description、categories、tags、status、可选 later_notes。status 为 note / reflection / ongoing / archived；后记为 date + Markdown text 列表，正文原始观点保留。稳定 URL 不含日期。
- 日期显示原始发布与最后更新；RSS pubDate 使用原始日期，sitemap lastmod 使用最后更新。后记保留独立日期，RSS 内容含后记。
- 文章具备目录、脚注、引用、代码、懒加载图片、上一篇与下一篇；相邻文章按同栏目原始时间排序，不受最后更新时间影响。
- 示例全部明确标记为示例；旧 Hello World 原文迁入 Notes，保留原始日期。旧文章直链重定向到迁移位置。

## 视觉与访问

米白 #f5f3ee、深墨 #303532、低饱和灰绿；深色采用 #202523，避免纯黑。系统字体、不请求第三方字体。正文 18px 左右、行距 1.95、阅读宽度约 680px。留白和细线为主，不使用卡片墙、渐变、背景图、宗教符号、动画和社交指标。移动端导航自然换行。系统暗色偏好为默认，按钮循环系统 / 浅色 / 深色并保存本地选择；关闭 JS 仍可跟随系统颜色并访问全部内容。支持键盘焦点、跳至内容、语义化结构。

## 发布和维护

只需新增 content/<section>/<slug>.md，填写 metadata，git push。Now / Path 直接编辑各自文件。本地 hugo server；生产 hugo --minify。CI 下载指定 Hugo 版本并验证官方校验和，构建、检查本地链接和关键输出，然后部署 Pages。无追踪、广告、登录、推荐、分享按钮。RSS、sitemap、canonical、描述、Open Graph 和结构化数据由模板生成。

## 验证

先编写生成站点验收脚本并确认旧站失败。之后验证九栏目、taxonomy、年份、后记、Markdown 特性、RSS/sitemap、SEO、无 CDN 与断链；以移动和桌面浏览器检查窄屏溢出、暗色切换、持久化、无 JS 阅读、脚注和目录导航。额外构建带子路径的版本，验证 GitHub Pages 项目站迁移。不自动推送此次重构；本地提交供审阅。
