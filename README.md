# 我的 Skills 库

收集和维护可复用的 AI 工作流程。每个目录都是一个独立 Skill，包含 `SKILL.md` 以及必要的脚本、示例和参考资料。

## 已收录

| Skill | 用途 | 依赖 |
|---|---|---|
| [reference-request](reference-request/SKILL.md) · 推荐信请求邮件 | 根据真实经历撰写或修改中英文推荐信请求邮件，整理事实要点和跟进建议；可生成带来源的 HTML 批注展示 | 写作无需额外依赖；HTML 渲染需要 Python 3 标准库 |
| [resume-fix](resume-fix/SKILL.md) · 简历精批 | 基于真实经历诊断简历，逐轮追问后生成保留原 PDF 的双段精批 PDF 与 PNG | Python 3 和 `PyMuPDF==1.26.5` |
| [jd-decode](jd-decode/SKILL.md) · JD 拆解与面试准备 | 从 JD 提取核心职责、明确要求、加分项和可执行的 P0/P1/P2 面试准备清单；每条结论回链 JD 原文 | 无额外依赖 |

## 在 Codex 中安装

可以直接告诉 Codex：

> 请从 https://github.com/Zxyxyxy/codex-skills 安装 resume-fix，作为我的个人 skill。

也可以先克隆本仓库，再将需要的 Skill 目录导入所用工具的个人技能目录。只需安装具体 Skill 文件夹，无需把整个仓库作为一个 Skill 安装。

```bash
git clone https://github.com/Zxyxyxy/codex-skills.git
```

安装后可以这样调用：

> 用 $reference-request 帮我给课程老师写一封推荐信请求邮件。请先根据我提供的真实经历出稿，缺少的信息用占位符标出。

> 用 $reference-request 为我的现有邮件添加官方指南批注，保留原文，并生成 HTML 和纯文本版本。

> 用 $resume-fix 帮我优化这份简历。先根据经历逐轮追问，再生成保留原 PDF 的精批稿；不要虚构事实。

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
