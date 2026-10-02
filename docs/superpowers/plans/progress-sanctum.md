# SDD ledger — plan: docs/superpowers/plans/2026-10-02-sanctum.md

用户已提供完整需求并要求直接实现可运行第一版；按用户指示持续执行，不增加设计审批停顿。
现有隔离云 checkout，分支 work，基线 056c881；保留 checkout，不创建额外 worktree。
预检查：模板与 taxonomy 使用 Hugo 原生 Page；CI 与本地共享生成输出检查脚本；无接口冲突。

Task 1: complete — 0c97f5f；旧站验收失败 → Hugo 生产构建通过，48 HTML / 9 篇文章，本地链接与锚点无断链。
Task 2: complete — a7c17a8；安装脚本官方 SHA256 验证且连续运行两次；生产与 /sanctum/ 子路径验收通过；临时新增 Markdown 自动进入栏目、分类、中文标签、年份、最近更新和 RSS，之后移除测试文件。
Task 3: complete — 320 / 375 / 768 / 1440px × 10 路由检查通过；配色循环与持久化、系统深色、无 JS 目录与导航、localStorage 禁用、旧 Hello World 直链通过；无运行时外部请求。
边界检查：删去全部样例文章后的空栏目构建通过；省略 tags/categories/lastmod/later_notes 可构建；无效状态、lastmod 早于 date、后记日期晚于 lastmod 均明确失败。
独立审查：sanctum_review 对 056c881..a7c17a8 提出 3 项 Important、2 项 Minor，全部修复。Pages 构建增加 pages: read；RSS 所有相对 href/src（包括脚注）按文章 URL 解析；后记全部局部 ID 添加命名空间；空后记不显示首页锚点；深色偏好下打印采用浅色。
回归记录：后记锚点重复先失败、修复后 RSS 相对路径再失败、修复后通过；空后记首页链接先失败后通过；深色打印浏览器断言先失败后通过。独立 fixture 测试 2/2，完整构建/子路径/浏览器再次通过。
云配置：install_script 与 start_skill 已保存为 Hugo 工作流；保留原有网络设置并增加 github.com、release-assets.githubusercontent.com。开发服务器 /tmp/sanctum-dev 与 public 生产输出分开；未执行推送、线上部署或环境快照发布。
