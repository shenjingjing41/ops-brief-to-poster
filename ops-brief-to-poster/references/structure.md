# 文件与结构说明

这份说明只描述 `ops-brief-to-poster/` 这个 skill 的组成和维护边界。它不规定某一次海报的文案、版式或风格，也不把 `poster/` 下的历史项目内容带入新任务。

## Skill 本体

```text
ops-brief-to-poster/
├── SKILL.md                         # 运行规则、阶段流程、交付边界
├── LICENSE                          # skill 许可
├── agents/
│   └── openai.yaml                  # 在 Codex 中显示的名称、描述和默认调用提示
├── references/                      # 按需读取的规则、示例和提示词模板
│   ├── brief-intake.md              # 需求补全、必要提问和停问条件
│   ├── clinical-default.md          # 临床决策默认品牌风格和资产边界
│   ├── clinical-examples.md         # 产品介绍、扫码页、专科演示、展架等参考案例
│   ├── clinical-offline-assets.md   # Logo、IP 等正式素材的使用规则
│   ├── default-flat.md              # 历史普通扁平配置，仅在用户明确指定时参考
│   ├── design-review.md             # 生图前后自检、修正顺序和记录要求
│   ├── functional-illustration.md   # 需要新生成配图时的轻量功能插画规则
│   ├── prompt-template.md           # 每张图独立完整提示词的字段结构
│   ├── style-planning.md            # 将自然语言风格要求转成可生图方案
│   ├── structure.md                 # 本文件：skill 文件职责和产物结构
│   └── workflow.md                  # 运营事实、信息层级和布局决策规则
├── assets/
│   ├── brand/clinical-offline/      # 可原样使用的正式 Logo、IP 等品牌素材
│   └── style-references/            # 风格、案例和功能插画参考图
└── scripts/
    └── extract_docx.py              # DOCX 文字、表格、图片关系和原图提取脚本
```

`.DS_Store` 等系统元数据不属于 skill 运行结构，不应被引用或作为交付依赖。

## 单次任务产物

每个任务在工作区 `poster/<项目名>/` 下独立保存。目录名和文件名可以按任务调整，但保留以下职责：

```text
poster/<项目名>/
├── analysis.md                     # 有来源事实、用户选择、设计推断、缺项和设计任务
├── layout.md                       # A/B 构图、阅读顺序、必显责任、锁定项和尺寸处理
├── style-plan.md                   # 风格约束、参考图角色、生成前后检查记录
├── prompts/
│   ├── poster-a-v1.md              # A 稿完整提示词；后续实质修改递增版本
│   └── poster-b-v1.md              # B 稿完整提示词；后续实质修改递增版本
├── source/                         # DOCX 提取结果或用户提供的本次素材
│   ├── source.json                 # 提取顺序、关系和警告（如有）
│   └── assets/                     # 原始图片，不根据文件名猜内容
└── <result>-vN.png                 # 每轮生成结果，保留旧版本，不覆盖
```

只要求分析或提示词时，可以不生成图片；只缺二维码、正式封面或定制商品图时，可在 `layout.md` 和提示词中记录净空或文字表达，不伪造素材。线下尺寸未确认时，不能把概念预览标成印刷完稿。

## 维护边界

- 修改默认规则、参考路径或资产目录时，更新 skill 本体及本文件；不要只改某个历史项目的提示词来改变默认行为。
- 用户单次指定的色彩、风格、布局或文案只写入该任务的 `style-plan.md`、`layout.md` 和提示词，不自动升级为共享配置。
- 共享 skill 的规范源是仓库中的 `ops-brief-to-poster/`；实际运行前需确认已安装目录与仓库副本一致。同步后至少检查 `SKILL.md`、`references/`、`assets/` 和 `scripts/` 的文件清单。
- 生成图片、项目记录和验证日志属于工作区产物，不是 skill 本体；它们可以支持复盘，但不会自动成为新的默认案例或规则。
