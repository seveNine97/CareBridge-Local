# CareBridge Local
面向基层医护与社区健康工作者的离线医疗助手，主打“免装 Ollama、可下载即用、真实可部署、真正有 RAG、能讲出强 impact 故事”。

**Summary**
- 这次不做“通用聊天网页”，而是做一个桌面优先的真实产品：`桌面 App + 公共演示站` 双交付。桌面 App 是主产品，公共站负责 live demo、下载分发、故事说明和评委快速试用。
- 产品定位锁定为 `基层医疗助手 / Community Health Worker Copilot`，主要服务弱网或断网环境中的乡村诊所、流动医疗点、NGO 一线人员；它辅助采集病情、检索本地指南、生成转诊建议和患者教育说明，但不宣称替代医生诊断。
- 当前仓库要视为“原型参考”，不是继续堆功能的基础：现有 [app.py:294](/C:/Users/seveNine/Desktop/offline-gemma-assistant/repo/app.py#L294) 只做文档入库，聊天在 [app.py:465](/C:/Users/seveNine/Desktop/offline-gemma-assistant/repo/app.py#L465) 仅把历史消息发给 `ollama.chat()`，没有把检索结果注入回答，所以 README 里的 RAG 叙事并未真正闭环。
- 参赛叙事主轴按 `Health & Sciences` 来写，技术实现按 `llama.cpp` 特别赛道来设计，安全叙事额外覆盖 `Safety & Trust` 角度。

**产品定义**
- 主产品名称建议：`CareBridge Local`。中文可用“离线基层医疗助手”作为副标题。
- 核心用户流固定为 5 步：`新建病例` -> `录入症状/体征/风险因素` -> `上传照片或本地文档` -> `Gemma 4 生成结构化分诊与依据` -> `导出转诊单/患者说明/随访清单`。
- 首发必须落地的 6 个能力：
- `结构化分诊`：输出 `紧急转诊 / 尽快就医 / 居家观察` 三档，并列出红旗症状、缺失信息、下一步动作。
- `真实 RAG`：检索本地医疗指南、药品说明、急救 SOP、妇幼/儿科/慢病资料，并在回答中展示 citation chips。
- `多模态输入`：支持拍照上传处方、药盒、化验单、伤口/皮疹图片；如果本地多模态路径稳定，就在桌面端直接跑；若 Windows 本地多模态不稳定，则桌面版保留文档/图片上传入口，完整多模态演示放到公共 demo 站。
- `低识字率输出`：一键切换“医护版摘要”和“患者版说明”，患者版用更简单语言，默认中英双语，后续可扩展本地语言包。
- `病例导出`：生成 referral summary、患者须知、药物提醒单、随访 checklist，可导出 PDF/JSON。
- `安全护栏`：胸痛、呼吸困难、婴幼儿高热、孕期出血、严重脱水、意识障碍等走硬规则优先，不允许模型“自由发挥”。
- 明确不做的事：
- 不做开放式“万能医生”定位。
- 不做线上联网依赖才能用的核心功能。
- 不把“用户自己装 Ollama”作为交付前提。
- 不把“上传文档但没有引用证据”的伪 RAG 再做一遍。

**技术架构**
- 桌面端采用 `Tauri 2 + React + TypeScript`，做真正的安装包，而不是 localhost 原型。
- 本地编排服务采用 `FastAPI + Pydantic`，单独打包成 sidecar；这样既能复用你现有 Python 能力，也方便做 RAG、PDF 处理、规则引擎和评测脚本。
- 模型运行时采用 `llama.cpp` sidecar 作为生产方案，App 内部直接拉起 `llama-server`，前端和本地编排服务都通过本地 API 调用它；用户不需要单独安装 Ollama。
- 运行时抽象统一成 `InferenceProvider`，只实现两个 provider：
- `LlamaCppProvider`：生产默认、比赛主路径、最终打包。
- `OllamaProvider`：仅开发调试保留，方便你前期快速联调，但不进入最终用户路径。
- 模型包采用双档：
- `Balanced`：默认 `ggml-org/gemma-4-E4B-it-GGUF`，用于 16GB RAM 级别机器。
- `Compatibility`：低配回退 `ggml-org/gemma-4-E2B-it-GGUF`，用于更弱设备。
- Embedding 模型统一改为 `EmbeddingGemma`，替换上次的 `nomic-embed-text`，这样生成与检索都能形成 Gemma 家族叙事。
- 数据层拆成两类：
- `SQLite`：保存病例、配置、导出记录、知识包 manifest、评测结果。
- `本地向量索引`：保存 chunk embedding 与 metadata；实现必须包含 dense 检索、关键词检索、citation metadata，不再做“只存不检”的结构。
- 公共演示站采用 `Next.js`，部署到 Vercel/Cloud Run 一类平台；它只承担 4 件事：产品故事、交互式 demo、下载入口、技术说明，不替代桌面产品。

**接口与类型**
- 桌面 UI 与本地服务之间固定使用本地 HTTP/WebSocket 合同，避免把业务逻辑写死在前端。
- 首批 API 固定为：
- `GET /health`：检查本地服务、模型、索引、知识包状态。
- `POST /runtime/start`：按设备能力启动 E4B 或 E2B。
- `POST /cases`：创建病例并返回 `case_id`。
- `POST /triage/run`：输入结构化症状、体征、附件，返回 `TriageAssessment`。
- `POST /chat/stream`：流式问答，必须支持 citations 与 safety alerts。
- `POST /knowledge/import`：导入本地 PDF/TXT/MD/图片并生成 chunk、metadata、索引。
- `POST /export/referral`：导出转诊单与患者说明。
- 核心类型固定为：
- `PatientCase`：患者基础信息、风险因素、附件引用。
- `TriageAssessment`：分诊级别、红旗症状、缺失信息、建议动作、禁忌提醒。
- `EvidenceCitation`：来源文档、页码/段落、知识包版本、可信等级。
- `KnowledgePackManifest`：知识包名称、版本、语言、区域、来源许可、更新时间。
- `ModelProfile`：runtime、模型名、量化版本、预计内存、当前状态。

**实现阶段**
- `阶段 1：重构仓库`
- 新结构固定为 `apps/desktop`、`apps/web`、`services/local-core` 三部分；旧 Streamlit 原型移入 `legacy`，只保留最少参考代码。
- 先把“UI、业务编排、本地推理”拆开，再开始写新功能，避免继续把全部逻辑塞进一个 `app.py`。
- `阶段 2：本地推理与免 Ollama 分发`
- 做 Model Manager：检测 RAM/CPU、检查模型完整性、自动选 E4B/E2B、支持断点下载和离线导入。
- 发布两种安装物：
- `Lite Installer`：App + runtime，不带大模型，首启一键下载模型包。
- `Field Bundle`：App + 模型包 + 基础知识包，可通过 U 盘/局域网直接导入，适合真正离线场景。
- `阶段 3：真实医疗 RAG`
- 先内置 1 套基础知识包：急救、发热/腹泻/呼吸道症状、孕产妇红旗、儿童常见问题、基础用药说明。
- 知识包设计成可插拔：后续可以导入地区化 SOP、乡镇卫生院表单、药品目录、NGO 培训资料。
- 问答链路固定为：`意图分类` -> `红旗规则预检查` -> `检索` -> `生成结构化答复` -> `citation 校验` -> `UI 展示`。
- `阶段 4：比赛亮点功能`
- 加入 `Guided Intake Wizard`，不只聊天，改为表单 + 聊天混合。
- 加入 `Explain for Patient`，把医护结论自动翻译成患者可执行说明。
- 加入 `Prescription / Lab / Wound Analyzer`，把图像与文档变成结构化字段。
- 加入 `Referral Pack Export`，一键导出医生摘要、患者须知、随访清单。
- 加入 `Offline Knowledge Pack Import`，展示真实落地性，而不是比赛演示专用壳子。
- `阶段 5：参赛交付`
- 公共站必须展示：价值主张、真实离线架构图、1 分钟快速试用、完整视频、下载链接、FAQ。
- Kaggle write-up 不写“我做了一个聊天机器人”，而是写“我做了一个面向基层医护的离线临床辅助产品”，重点讲 impact、低资源环境、隐私、可分发性、真实用户路径。
- Demo 视频固定用 3 个场景：`儿童发热`、`孕妇危险信号`、`药盒/处方识别 + 患者说明生成`。

**测试与验收**
- 必做功能测试：
- 断网启动 App，仍可完成一次完整病例创建、问答、导出。
- 导入 20 份以上 PDF/TXT/图片资料后，检索回答必须出现 citations。
- 切换 E4B/E2B 后，接口合同和 UI 不变。
- 必做医疗安全测试：
- 对胸痛、呼吸困难、意识障碍、孕期出血、婴儿高热、严重外伤等场景，必须稳定触发 `紧急转诊`，且禁止输出“继续观察即可”。
- 对缺失关键体征的数据，必须优先追问，不能直接给结论。
- 对药物剂量或诊断类高风险问题，没有依据时必须降级为“请核对指南/转诊”，不能瞎编。
- 必做 RAG 测试：
- 至少构建 50 个基准病例问答，统计 citation 覆盖率、检索命中率、无依据回答率。
- 必须加一组“伪相似文档”对抗测试，防止模型被错误 chunk 带偏。
- 必做性能测试：
- 在标准 16GB Windows 设备上，简单问答首 token 体验要可接受，分诊回复不能长时间卡死。
- 首次安装后，模型检查、知识包加载、二次启动都要有明确进度反馈。
- 参赛验收标准：
- 有公开网站。
- 有可下载桌面包。
- 有真实离线演示视频。
- 有公开仓库。
- 有技术 write-up。
- 有 3 个能打动评委的医疗场景演示。

**Assumptions**
- 首发只保证 Windows 10/11；macOS/Linux 放到后续迭代，不进入本次比赛核心范围。
- 默认目标设备是 16GB RAM 的普通笔记本；低配兼容依赖 E2B 回退。
- 默认语言是中文 + 英文；知识包和 UI 都按多语言可扩展设计。
- 生产交付默认走 `llama.cpp`，不是隐藏安装 Ollama；Ollama 只保留为开发调试通道。
- 如果本地 Gemma 4 多模态在 Windows 上验证不稳，不阻塞 MVP：桌面端先保证文本/文档/RAG/分诊闭环，多模态完整体验放到公共 demo 站展示。
- 医疗定位始终是“基层临床辅助与患者教育”，不是“替代医生做诊断”。

**参考依据**
- 比赛主页：[Kaggle Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
- 公开索引到的比赛要求与评审维度镜像： [Slashpage indexed overview](https://slashpage.com/haebom/36nj8v2wkgj1km5ykq9z?lang=en&tl=en)
- 官方 Gemma 4 介绍： [Google Blog: Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/)
- 官方边缘能力与函数调用方向： [Google Developers Blog: Gemma 4 on the edge](https://developers.googleblog.com/en/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
- 官方 GGUF 分发： [ggml-org/gemma-4-E4B-it-GGUF](https://huggingface.co/ggml-org/gemma-4-E4B-it-GGUF) 、 [ggml-org/gemma-4-E2B-it-GGUF](https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF)
- 官方嵌入模型文档： [EmbeddingGemma docs](https://ai.google.dev/gemma/docs/embeddinggemma)
