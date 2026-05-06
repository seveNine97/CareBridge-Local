# CareBridge Local 产品化实施计划

## 一、项目概述

### 目标
将 CareBridge Local 打造成一个可分发的离线医疗问诊应用，对标蚂蚁阿福等在线问诊产品，实现：
- **桌面端**：Windows 可执行安装包
- **网页端**：可部署的Web应用
- **完全离线**：无需网络即可使用
- **本地大模型**：使用Gemma进行AI问答

### 当前状态分析

| 组件 | 状态 | 说明 |
|------|------|------|
| 后端服务 (FastAPI) | 🟡 部分完成 | 核心API完成，需打包 |
| 桌面前端 (React) | 🟡 部分完成 | UI完整，需Tauri配置 |
| Web前端 (Next.js) | 🟢 基本完成 | 可直接部署 |
| 知识库 | 🔴 待扩展 | 仅5篇基础文档 |
| 大模型集成 | 🔴 未配置 | 需用户手动配置 |
| 分诊规则 | 🟢 已完成 | 基础规则完善 |

---

## 二、架构设计

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户设备                                  │
│  ┌─────────────────────┐     ┌────────────────────────────────┐ │
│  │   桌面应用 (Tauri)   │     │       网页应用 (PWA)           │ │
│  │  ┌───────────────┐  │     │  ┌──────────────────────────┐  │ │
│  │  │ React 前端    │  │     │  │      Next.js 前端        │  │ │
│  │  └───────────────┘  │     │  └──────────────────────────┘  │ │
│  │  ┌───────────────┐  │     │         ↑                      │ │
│  │  │ HTTP API 调用 │  │     │         │ (Service Worker)     │ │
│  │  └───────────────┘  │     │         ↓                      │ │
│  └─────────┬───────────┘     └────────────────────────────────┘ │
│            │                                                  │ │
│            ↓                                                  │ │
│  ┌─────────────────────────────────────────────────────────┐   │ │
│  │              本地 FastAPI 服务 (PyInstaller打包)          │   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │ │
│  │  │ 用户管理  │ │ 病历管理 │ │ 分诊引擎  │ │ 知识检索   │  │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │ │
│  │  │ 知识导入  │ │ 转诊导出 │ │ AI对话   │ │ 会话管理   │  │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │ │
│  └─────────────────────────┬───────────────────────────────┘   │ │
│                            │                                     │ │
│  ┌─────────────────────────┴─────────────────────────────────┐   │ │
│  │              SQLite 数据库 (内置)                           │   │ │
│  └───────────────────────────────────────────────────────────┘   │ │
│                            │                                     │ │
│  ┌─────────────────────────┴─────────────────────────────────┐   │ │
│  │        本地 LLM 运行时 (llama.cpp + Gemma)                  │   │ │
│  └───────────────────────────────────────────────────────────┘   │ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、实施阶段

### 阶段一：核心功能完善 (Week 1-2)

#### 1.1 后端服务增强

**1.1.1 用户认证模块** (`services/local-core/carebridge_local_core/auth.py` - 新建)

```
功能：
- 简单 PIN 码登录（4-6位数字）
- 用户会话管理
- 病历数据隔离

实现：
- 使用 hashlib 存储 PIN 码哈希
- JWT Token 管理会话
- SQLite 存储用户信息
```

**1.1.2 会话管理模块** (`services/local-core/carebridge_local_core/session.py` - 新建)

```
功能：
- 保持对话上下文
- 会话历史存储
- 多会话支持
```

**1.1.3 增强分诊规则** (`services/local-core/carebridge_local_core/triage.py` - 扩展)

```
扩展内容：
- 症状关键词库扩展到 100+ 项
- 年龄相关风险评估
- 妊娠特殊情况处理
```

#### 1.2 数据模型扩展 (`services/local-core/carebridge_local_core/models.py` - 修改)

```python
# 新增模型
class User(BaseModel):
    user_id: str
    username: str
    pin_hash: str
    created_at: datetime
    
class ChatSession(BaseModel):
    session_id: str
    user_id: str
    case_id: str | None
    messages: list[ChatMessage]
    created_at: datetime
    updated_at: datetime
    
class ChatMessage(BaseModel):
    message_id: str
    role: str
    content: str
    citations: list[EvidenceCitation]
    created_at: datetime
```

---

### 阶段二：前端界面升级 (Week 2-3)

#### 2.1 桌面应用 UI 重构 (`apps/desktop/src/`)

**2.1.1 新建组件结构**

```
apps/desktop/src/
├── components/
│   ├── Layout/ (Sidebar, Header, Layout)
│   ├── Auth/ (Login, PinInput)
│   ├── Chat/ (ChatWindow, MessageBubble, InputBox)
│   ├── Triage/ (TriageForm, VitalsInput, TriageResult)
│   ├── Case/ (CaseList, CaseDetail, CaseForm)
│   ├── Knowledge/ (KnowledgePanel, DocViewer)
│   └── Common/ (Button, Card, Modal, Toast)
├── contexts/
│   ├── AuthContext.tsx
│   ├── ChatContext.tsx
│   └── AppContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useChat.ts
│   └── useTriage.ts
├── pages/
│   ├── Login.tsx
│   ├── Home.tsx
│   ├── Chat.tsx
│   ├── Triage.tsx
│   ├── Cases.tsx
│   ├── Knowledge.tsx
│   └── Settings.tsx
└── services/
    ├── api.ts
    ├── authService.ts
    └── chatService.ts
```

#### 2.2 Web应用增强 (`apps/web/`)

**新增Web页面**

```
apps/web/app/
├── chat/page.tsx
├── triage/page.tsx
├── cases/page.tsx
└── knowledge/page.tsx
```

**添加PWA支持**

```javascript
// next.config.mjs 添加 next-pwa
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});
```

---

### 阶段三：知识库建设 (Week 3)

#### 3.1 扩展知识库内容

```
knowledge-packs/
├── base-health/              # 已有(5篇)
├── common-illnesses/         # 新建 - 常见疾病(7篇)
├── chronic-diseases/         # 新建 - 慢性病(4篇)
├── maternal-child/           # 新建 - 妇幼保健(5篇)
├── emergency/                # 新建 - 急救(5篇)
└── medicines/                # 新建 - 用药指南(4篇)
```

**文档格式标准**

```markdown
---
title: 儿童发热处理指南
category: pediatric
keywords: [发热, 发烧, 体温, 儿童]
last_updated: 2024-01-01
---

# 儿童发热处理指南

## 定义
体温超过 38°C 视为发热

## 危险信号 ⚠️
- 体温 > 40°C
- 持续发热 > 3 天
- 抽搐、皮疹、意识改变

## 家庭护理建议
1. 补充水分
2. 物理降温
3. 适时使用退烧药

## 何时就医
出现任何危险信号时应立即就医
```

---

### 阶段四：桌面应用打包 (Week 4)

#### 4.1 Tauri 配置完善 (`apps/desktop/src-tauri/tauri.conf.json`)

```json
{
  "productName": "CareBridge",
  "version": "1.0.0",
  "identifier": "com.carebridge.app",
  "build": { "devtools": true },
  "app": {
    "windows": [{
      "title": "CareBridge - 离线医疗助手",
      "width": 1200,
      "height": 800,
      "minWidth": 900,
      "minHeight": 600,
      "center": true
    }]
  },
  "bundle": {
    "active": true,
    "targets": ["nsis"],
    "windows": {
      "nsis": {
        "installMode": "currentUser",
        "languages": ["SimpChinese", "English"]
      }
    }
  }
}
```

#### 4.2 添加系统托盘 (`apps/desktop/src-tauri/src/main.rs`)

```rust
fn main() {
    tauri::Builder::default()
        .system_tray(SystemTray::new().with_menu(
            SystemTrayMenu::new()
                .add_item(SystemTrayMenuItem::with_id("show", "打开 CareBridge", true, None::<&str>))
                .add_item(SystemTrayMenuItem::with_id("quit", "退出", true, None::<&str>))
        ))
        .on_system_tray_event(|app, event| {
            match event {
                SystemTrayEvent::LeftClick { .. } => {
                    let _ = app.get_window("main").show();
                }
                _ => {}
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

#### 4.3 后端服务打包 (`scripts/build-backend.ps1`)

```powershell
# 打包后端为单文件可执行程序
pyinstaller --name CareBridgeService `
    --onefile `
    --console `
    --add-data "knowledge-packs;knowledge-packs" `
    --hidden-import=uvicorn `
    --hidden-import=fastapi `
    --hidden-import=pydantic `
    --collect-all uvicorn `
    --collect-all fastapi `
    services/local-core/carebridge_local_core/__main__.py
```

---

### 阶段五：功能增强 (Week 4-5)

#### 5.1 语音输入 (可选)

```typescript
// apps/desktop/src/utils/speech.ts
export const useSpeechRecognition = () => {
  const recognition = useMemo(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    return new SpeechRecognition();
  }, []);
  // 支持离线语音识别
};
```

#### 5.2 医疗机构管理 (`services/local-core/carebridge_local_core/facilities.py`)

```python
class FacilityManager:
    def add_facility(self, facility: Facility) -> None:
        # 添加医疗机构信息
    def search_nearby(self, lat: float, lon: float, radius_km: float) -> list[Facility]:
        # 搜索附近医院
```

#### 5.3 PDF导出 (`services/local-core/carebridge_local_core/pdf_exporter.py`)

```python
def export_pdf(self, case: PatientCase, triage: TriageAssessment) -> str:
    # 使用 reportlab 生成 PDF 转诊单
```

---

### 阶段六：测试与发布 (Week 5-6)

#### 6.1 测试清单

| 模块 | 测试项 | 验收标准 |
|------|--------|----------|
| 用户认证 | PIN码登录/登出 | 正确验证 |
| 病例管理 | CRUD操作 | 数据持久化 |
| 分诊 | 症状评估 | 规则正确触发 |
| 知识检索 | 关键词搜索 | 相关结果准确 |
| AI对话 | 流式响应 | 响应正常 |
| 转诊导出 | HTML/PDF生成 | 文件正确 |

#### 6.2 发布清单

- [ ] 代码仓库打标签
- [ ] 版本号更新
- [ ] 构建安装包
- [ ] 测试验证通过
- [ ] 用户文档编写

---

## 四、文件清单

### 需要新建的文件 (共约45个)

```
services/local-core/carebridge_local_core/
├── auth.py                    # 用户认证
├── session.py                 # 会话管理
├── facilities.py              # 医疗机构
├── pdf_exporter.py            # PDF导出

apps/desktop/src/
├── components/ (15个组件文件)
├── contexts/ (3个上下文)
├── hooks/ (4个自定义钩子)
├── pages/ (7个页面)
├── services/ (2个服务)
└── utils/ (3个工具文件)

apps/web/app/
├── chat/page.tsx
├── triage/page.tsx
├── cases/page.tsx
└── knowledge/page.tsx

knowledge-packs/ (新增约26个文档)
```

### 需要修改的文件 (共约10个)

```
services/local-core/carebridge_local_core/
├── models.py
├── app.py
├── triage.py
├── config.py
└── storage.py

apps/desktop/
├── src-tauri/tauri.conf.json
├── src-tauri/src/main.rs
├── src/App.tsx
├── src/api.ts
├── src/styles.css
└── package.json

apps/web/
├── next.config.mjs
```

---

## 五、技术依赖

### Python
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
pypdf>=3.0.0
httpx>=0.25.0
pyinstaller>=6.0.0
reportlab>=4.0.0
```

### 前端
```
React 18.x
TypeScript 5.x
@tauri-apps/api 2.x
react-router-dom 6.x
zustand
react-query
```

---

## 六、里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 阶段一 | Week 1-2 | 后端功能完善 |
| 阶段二 | Week 2-3 | 前端界面升级 |
| 阶段三 | Week 3 | 知识库扩展 |
| 阶段四 | Week 4 | 桌面应用打包 |
| 阶段五 | Week 4-5 | 功能增强 |
| 阶段六 | Week 5-6 | 测试发布 |

---

## 七、API端点汇总

```
认证: POST /auth/login, POST /auth/logout, GET /auth/me
会话: GET /sessions, GET /sessions/{id}, DELETE /sessions/{id}
病例: GET/POST/PUT/DELETE /cases, GET /cases/{id}
分诊: POST /triage/run
知识: GET /knowledge/packs, GET /knowledge/search, POST /knowledge/import
聊天: POST /chat/stream
导出: POST /export/referral, GET /exports
```



