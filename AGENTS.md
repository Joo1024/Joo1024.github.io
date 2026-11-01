# Sanctum 维护规则

- 修改前检查 git status，保留已有改动；提交、推送和发布遵循用户当次授权。
- 使用现有 Hugo 与 Markdown，不引入第三方框架。
- 本仓库只保存公开 Posts，放在 content/posts/，不建立子目录；私人札记放在同级私有仓库 sanctum-notebook/notes/，不放回 blog。
- 私有札记文件名 YYYY-MM-DD-NN.md，编号 01–99；转换时检查同日编号，禁止覆盖，建立后不重命名。不要擅自把临时材料改写成公开内容。
- Posts 的 title/date 必填，date 为首次公开日期，公开后保留；私有札记保留原始记录日期，lastmod 记录实质更新，迁移本身不改日期。其他字段按需填写。
- Posts 的短记 form 为 brief；note 不再用作 form。私有札记不使用 form，转为文章时按需添加。保留其他形式和维度词汇的开放性。
- 来源统一用可选 sources 对象列表；kind 为 note/book/article/video/ai/other，按需提供适合公开的 title/url。公开文章不接受 sources.path；私有札记路径及来源关系保留在 sanctum-notebook。
- 不添加 based_on、双向链接、图谱或自动反向索引；sources 暂作为数据字段。
- 不使用 Hugo 保留字段 type 表达写作形式；来源 kind 位于 sources 内。
- 首页、Posts、存档、全站 RSS 的文章集合继续仅取 posts；不生成札记页面、导航或订阅，构建拒绝 content/notes/ 中的材料（包括草稿）。
- 内容规范变化时同步 docs/writing.md、README.md 和相关校验/测试；显示别名维护在 data/dimensions.yaml。
- 验证：.tools/bin/hugo --minify --cleanDestinationDir；python3 tests/check_site.py public；python3 -m unittest discover -s tests -p 'test_*.py' -v。
