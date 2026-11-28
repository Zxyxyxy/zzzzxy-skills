# Calibration and Efficient Use / 校准与高效使用

## First-use calibration / 首次校准

Keep the first one to five completed applications in one task so the agent can build a verified profile and the user can correct its choices. The user may end calibration at any time by saying “calibration complete”; do not invent an automatic graduation test. / 前一至五份完成的网申留在同一个任务中，用于建立已核验档案并让用户纠正填写方式。用户可随时回复“校准完成”结束校准；不得自行设置自动毕业条件。

Show this short tip once at the beginning, in the user's language: / 开始时仅提示一次，并使用用户的语言：

> First-use tip: I will first connect to or open a controllable browser and inspect existing tabs; an application URL is optional. Keep the first 1–5 applications in this task. I will fill and verify each draft, then you can review it. If you want me to remember a correction, name the exact field or content to learn. Say “calibration complete” when the result is stable. I will always stop before final submission.
>
> 首次使用技巧：我会先连接或打开可控浏览器并检查已有标签页，网申链接不是必需。前 1–5 份网申建议留在当前任务中。我会逐份填写并核验，你可随后人工检查；如需记住某项改动，请明确说出要学习的字段或内容。满意后回复“校准完成”。我始终会在最终提交前停下。

After every calibration draft, use one short prompt: / 每份校准草稿完成后只问一次：

> The draft is filled and verified. Did you edit it manually? If you want me to learn, tell me the exact field or content and where the rule applies. Unmentioned changes will not be learned.
>
> 草稿已经填写并核验。你是否手动修改过？如果需要我学习，请明确告诉我要学习的字段或内容，以及适用范围；未点名的改动不会被学习。

## Explicit learning only / 仅显式学习

Treat phrases such as “learn this field,” “remember this wording for product roles,” or “always fill this website this way” as authorization limited to the named content and stated scope. Do not scan unrelated fields for changes. If the user reports a fact correction, update the verified profile and source ledger. If the user reports a choice or writing preference, record a concise rule with one of these scopes: `global`, `role`, `site`, or `current_application`. When scope is missing, use `site` or `role` based on the immediate context; never default to `global`. / “学习这个字段”“产品岗以后这样写”“这个网站始终这样填”等指令，只授权学习点名内容及明确范围。不得扫描无关字段寻找改动。事实纠正写入已核验档案和来源账本；选择或表达偏好写成简短规则，范围使用 `global`、`role`、`site` 或 `current_application`。未说明范围时，根据当前语境保守使用 `site` 或 `role`，绝不默认全局。

Do not run periodic calibration, infer habits from repeated behavior, or promote a one-off answer into reusable memory. After calibration, wait for an explicit learning request; ordinary application completion updates only the application record. / 不进行周期性校准，不从重复行为自动推断习惯，也不把单次回答升级为长期记忆。校准结束后只响应明确的学习请求；普通网申完成时仅更新本次申请记录。

## Low-context production / 低上下文生产

After calibration: / 校准完成后：

1. Use one fresh task per company-role application when practical, while reusing the same authorized profile files and authenticated browser profile. / 条件允许时，每个“公司—岗位”使用一个新任务，同时复用同一套授权档案和已登录浏览器配置。
2. Load the compact verified profile, applicable preference rules, current job description, selected resume, and only the evidence needed for missing or conflicting fields. / 只加载精简档案、适用偏好、当前岗位说明、选定简历，以及解决缺失或冲突字段所需的证据。
3. Do not load the calibration transcript, historical screenshots, completed forms, or all original documents unless a specific conflict requires them. / 除非解决具体冲突，不加载校准对话、历史截图、已完成表单或全部原始文件。
4. Inspect the live page once, then use targeted field reads and verification instead of repeatedly capturing the entire page. / 先检查一次当前页面，之后使用定向字段读取与核验，避免反复抓取整页。
5. Save a compact application record containing company, role, URL, resume variant, attachments, unresolved fields, verification result, and submission state. / 保存精简申请记录：公司、岗位、链接、简历版本、附件、未解决字段、核验结果和提交状态。
6. Separate preparation from browser writing if several tasks are open. Only one task should control the same browser profile at a time. / 同时存在多个任务时，可并行准备内容，但同一时刻只能有一个任务控制同一个浏览器配置。

These rules reduce repeated context; they do not justify skipping evidence checks, required fields, draft verification, or final-submit confirmation. / 这些规则用于减少重复上下文，不得因此跳过证据核验、必填字段、草稿检查或最终提交确认。
