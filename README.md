# 我的 Skills 库

收集和维护可复用的 AI 工作流程。每个目录都是一个独立 Skill，包含 `SKILL.md` 以及必要的脚本、示例和参考资料。

个人 Skill 发布账号：小红书 **流水的skill铺** · 小红书号 **5389663157**。

## 已收录

| Skill | 用途 | 依赖 |
|---|---|---|
| [reference-request](reference-request/SKILL.md) · 推荐信请求邮件 | 根据真实经历撰写或修改中英文推荐信请求邮件，整理事实要点和跟进建议；可生成带来源的 HTML 批注展示 | 写作无需额外依赖；HTML 渲染需要 Python 3 标准库 |
| [resume-fix](resume-fix/SKILL.md) · 简历精批 | 基于真实经历诊断简历，逐轮追问后生成保留原 PDF 的双段精批 PDF 与 PNG | Python 3 和 `PyMuPDF==1.26.5` |
| [jd-decode](jd-decode/SKILL.md) · JD 拆解与面试准备 | 合并 JD 中重叠的职责与要求，整理为去重、可执行的面试准备重点；区分明确条件、加分项和待确认问题 | 无额外依赖 |
| [interview-q](interview-q/SKILL.md) · 面试预判与追问 | 结合简历、JD 和岗位类别常见题，给出回答框架与递进追问，最终生成脱敏的交互式 HTML 报告 | HTML 渲染需要 Python 3 标准库 |
| [mock-interview](mock-interview/SKILL.md) · 模拟面试与追问 | 从自我介绍、经历深挖到业务场景，一次一问并按回答追问；支持提示后重答，最终生成脱敏 HTML 报告与三色批注 | HTML 渲染需要 Python 3.9+ 标准库 |
| [interview-review](interview-review/SKILL.md) · 面试复盘与下一轮准备 | 依据真实问题、回答回忆和面试结果逐题复盘；未通过时补强，通过时准备下一轮，等待结果时先做共同分析；输出完整 Markdown 与脱敏 HTML 报告 | HTML 渲染需要 Python 3.9+ 标准库 |
| [resume-autofill-agent](resume-autofill-agent/SKILL.md) · 网申自动填写 | 使用本地候选人资料辅助填写招聘网站表单，支持浏览器连接、队列和填写前后核对 | Python 3；浏览器桥接需要 Node.js、Playwright Core 和 Chrome / Edge |
| [ux-writer](ux-writer/SKILL.md) · 界面文案设计与审查 | 从产品语气、术语和信息层级到逐屏微文案，检查按钮、空态、报错与提示 | 无额外依赖 |
| [resume-jd-match](resume-jd-match/SKILL.md) · 简历与 JD 匹配 | 确定性拆分要求、验证简历原文证据，并按规则计算匹配结论 | Python 3 标准库；实际模型评估需要自己的百炼配置 |

## 在 Codex 中安装

可以直接告诉 Codex：

> 请从 https://github.com/Zxyxyxy/zzzzxy-skills 安装 resume-fix，作为我的个人 skill。

也可以先克隆本仓库，再将需要的 Skill 目录导入所用工具的个人技能目录。只需安装具体 Skill 文件夹，无需把整个仓库作为一个 Skill 安装。

```bash
git clone https://github.com/Zxyxyxy/zzzzxy-skills.git
```

安装后可以这样调用：

> 用 $reference-request 帮我给课程老师写一封推荐信请求邮件。请先根据我提供的真实经历出稿，缺少的信息用占位符标出。

> 用 $reference-request 为我的现有邮件添加官方指南批注，保留原文，并生成 HTML 和纯文本版本。

> 用 $resume-fix 帮我优化这份简历。先根据经历逐轮追问，再生成保留原 PDF 的精批稿；不要虚构事实。

> 用 $jd-decode 拆解这份 JD，合并重复的职责与要求，按重要性列出具体准备重点，并标明明确条件、加分项和待确认问题。

> 用 $interview-q 根据我的简历和岗位 JD 预判面试问题，补充岗位类别常见题，提供真实回答框架和追问，最后生成脱敏的 HTML 阅读报告。

> 用 $mock-interview 结合我的简历和岗位 JD 模拟一次面试。从自我介绍开始，一次只问一道，等我回答后再追问；我说结束时，生成脱敏的 HTML 报告和三色批注。

> 用 $interview-review 复盘我的真实面试问题和回答思路。我会告诉你岗位、轮次和结果；未通过时给出补强方案，通过时帮我准备下一轮，最后生成脱敏的 HTML 报告。

## 运行批注示例

在仓库根目录执行：

```bash
python3 reference-request/scripts/render_annotations.py \
  --input reference-request/assets/example.json \
  --output output/reference-request-example.html
```

生成 `output/reference-request-example.html` 和同名 `.txt`，HTML 可离线打开。内附案例是匿名合成示例，须替换为真实信息后使用；来源链接在实际读取和核对之前均标为待核实。

渲染脚本只负责展示已有内容，不调用模型、不核验网页、不发送邮件。输入格式见[批注数据说明](reference-request/references/annotation-format.md)，写作和来源边界见 [SKILL.md](reference-request/SKILL.md)。

## 运行简历精批示例

在仓库根目录执行：

```bash
cd resume-fix
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python scripts/make_example.py --out /tmp/resume-fix-example
```

输出目录包含匿名合成简历的精批 PDF、PNG、QA 结果与 `review.json`。实际简历只在本地工作目录中处理，勿提交至仓库；完整输入规则、脱敏和校验要求见 [resume-fix/SKILL.md](resume-fix/SKILL.md)。

## 生成面试准备 HTML

使用 `interview-q` 分析材料后，将完整正文保存为 Markdown，再在仓库根目录执行：

```bash
python3 interview-q/scripts/render_report.py \
  --input /absolute/path/report.md \
  --output output/interview-report.html
```

生成的 HTML 可离线打开，包含模块目录、逐题折叠、全文阅读、打印 / 保存 PDF 和手机适配。保留 Markdown 作为正文；后续可按 Q01、S01、C01 等题号追问，要求更新报告时重新渲染 HTML。

渲染脚本不调用模型，只展示已有分析。姓名、联系方式、个人主页和来源文件名应在生成正文时脱敏；脚本的规则检测不能代替人工检查。真实简历、JD 和个人报告不随 Skill 发布。完整流程见 [interview-q/SKILL.md](interview-q/SKILL.md)。

## 生成模拟面试 HTML

使用 `mock-interview` 完成逐轮练习后，按[报告数据格式](mock-interview/references/report-format.md)整理实际问答、总结和批注，在仓库根目录执行：

```bash
python3 mock-interview/scripts/render_report.py \
  --input /absolute/path/report.json \
  --output output/mock-interview-report.html
```

同时生成 HTML 和同名 Markdown。报告先展示总结，随后可按阶段查看完整问答，支持折叠、全文阅读、打印和手机适配。绿色标亮点，橙色标待补信息，蓝色标改进建议；批注须引用记录中的原句，提示后回答单独标记。

逐轮面试由宿主 AI 完成，脚本仅渲染已有记录。个人简历、JD 和练习记录保留在本地，不随 Skill 发布。完整流程见 [mock-interview/SKILL.md](mock-interview/SKILL.md)。

## 生成真实面试复盘 HTML

使用 `interview-review` 分析真实面试记录后，将完整正文保存为 Markdown，再在仓库根目录执行：

```bash
python3 interview-review/scripts/render_report.py \
  --input /absolute/path/review.md \
  --output output/interview-review.html
```

同时生成 HTML 和 `output/interview-review-脱敏.md`。报告包含本场结论、完整问答、逐题分析、结果对应的行动方案和待补材料，支持折叠、全文阅读、打印与手机适配。绿色标亮点，橙色标待补，蓝色标调整建议；引用应来自实际记录。

已通过时准备下一轮的递进追问和真实证据，未通过时给出优先补强项，结果未知时先做共同复盘。不预测通过概率，不把回忆遗漏等同于现场没答，也不把推断写成确定淘汰原因。可重复传入 `--redact '需要隐藏的文字'` 补充脱敏项，交付前仍需人工核对。个人面试记录、简历、JD 和报告不随 Skill 发布。完整流程见 [interview-review/SKILL.md](interview-review/SKILL.md)。

## 目录约定

```text
reference-request/
├── SKILL.md                 # 触发条件与执行流程
├── agents/openai.yaml       # Codex 展示信息
├── assets/example.json      # 匿名合成示例
├── references/              # 格式、引用边界和来源说明
└── scripts/                 # 可独立运行的辅助脚本
```

新增 Skill 时使用独立目录，写明输入、步骤、输出和必要依赖。公开示例应使用匿名或合成材料；个人输入、邮件成稿、密钥和运行日志不进入仓库。

## 新收录 Skill 的离线检查

在仓库根目录运行，不会登录账号、提交网申或调用付费模型：

```bash
node --test resume-autofill-agent/scripts/browser-bridge/tests/profile_resolver.test.js
python3 -m unittest discover -s resume-autofill-agent/scripts/tests
python3 resume-jd-match/scripts/run_eval.py --dry
python3 -m unittest discover -s resume-jd-match/scripts/tests
```

网申浏览器桥接的依赖在 `resume-autofill-agent/scripts/browser-bridge` 中执行 `npm ci` 安装。候选人资料、浏览器登录状态和申请结果保存在本地；打包脚本仅收录维护的源码白名单，新增源码需同步更新该名单。

这三个目录从已维护的个人本地 Skill 整理发布，并修正了机器路径与配置示例。`resume-autofill-agent` 保留原有 MIT 许可；其他目录的许可和来源以各自文件为准，本仓库不替其添加统一授权。`resume-jd-match/fixtures` 全部为本次编写的虚构测试材料，不包含真实简历。离线检查不能证明网站适配、真实投递或模型判断效果。
