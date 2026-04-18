# 密码管理器

> [**English**](README.md) · [**中文**](README_CN.md)

一款本地优先的安全桌面密码管理器，基于 **Tauri 2 + React + Rust** 构建。

所有数据加密后仅存储在本地，无云端、无追踪、无遥测。

---

## 下载

**最新版本: v3.0.0**

- [下载 Windows 版本](https://github.com/HYQJ932/-Password-Manager/releases/tag/v3.0.0)
- [查看所有版本](https://github.com/HYQJ932/-Password-Manager/releases)

---

## 功能特性

- **AES-256-GCM 加密** + Argon2id 密钥派生
- **主密码保护** + Argon2 哈希验证
- **两种条目类型**：登录凭据（用户名 + 密码 + URL）和 API 密钥
- **完整增删改查** 操作
- **密码生成器**：可配置长度、字符集、排除歧义字符
- **用户名生成器**：多种格式（word1234 / word_word / word.word）
- **文件夹分类** 与收藏功能
- **全局搜索**：按名称/用户名/URL/API Key 搜索
- **自动锁定**：可配置超时时间（1/5/15/30 分钟或永不）
- **深色 / 浅色主题** 切换
- **中英双语** 界面
- **一键复制** 到剪贴板
- **Apple HIG 风格** 界面设计

---

## 安全机制

1. 主密码仅存储 Argon2 哈希值，用于验证
2. 加密密钥通过 Argon2id + 随机 32 字节盐值派生
3. 所有敏感数据以 AES-256-GCM 加密后存储
4. 锁定时密钥从内存中安全清除
5. 完全离线运行，无网络访问

---

## 架构

```
┌──────────────────────────────────────────┐
│           React 前端 (TypeScript)          │
│                                          │
│  LockScreen · Sidebar · VaultList        │
│  VaultDetail · Generator · Settings      │
│                                          │
│        ↕  Tauri IPC (invoke)             │
├──────────────────────────────────────────┤
│            Rust 后端 (Tauri 2)            │
│                                          │
│  commands.rs — 16 个 IPC 命令处理         │
│  crypto.rs   — AES-256-GCM + Argon2id   │
│  db.rs       — SQLite 数据层             │
│  models.rs   — 数据模型 (serde)          │
│  generators.rs — 密码/用户名生成器        │
│                                          │
│  存储: 本地 SQLite (vault.db)             │
└──────────────────────────────────────────┘
```

---

## 技术栈

| 层级 | 技术 |
|-----|------|
| 前端 | React 18, TypeScript, Vite 6 |
| 后端 | Rust, Tauri 2 |
| 数据库 | SQLite (rusqlite, bundled) |
| 加密 | AES-256-GCM (aes-gcm 0.10) |
| 密钥派生 | Argon2id (argon2 0.5) |

---

## 前置要求

- [Node.js](https://nodejs.org/) >= 18
- [Rust](https://www.rust-lang.org/tools/install) >= 1.70
- [Tauri CLI](https://v2.tauri.app/start/prerequisites/)

Windows 用户还需要：
- Microsoft Visual Studio C++ Build Tools
- WebView2（Windows 10/11 已预装）

---

## 开发

```bash
# 安装依赖
npm install

# 开发模式运行
npm run tauri dev

# 构建生产版本
npm run tauri build
```

---

## 项目结构

```
password-manager/
├── src/                        # React 前端
│   ├── components/             # UI 组件
│   │   ├── LockScreen.tsx      # 锁屏界面
│   │   ├── Sidebar.tsx         # 侧边栏导航
│   │   ├── VaultList.tsx       # 条目列表
│   │   ├── VaultDetail.tsx     # 条目详情编辑
│   │   ├── Generator.tsx       # 密码/用户名生成器
│   │   └── Settings.tsx        # 设置页面
│   ├── hooks/                  # React hooks
│   │   ├── useVault.ts         # 保险库状态管理
│   │   ├── useI18n.ts          # 国际化
│   │   └── useClipboard.ts     # 剪贴板
│   ├── i18n/
│   │   └── translations.ts     # 翻译字典
│   ├── styles/
│   │   └── index.css           # 全局样式
│   ├── App.tsx                 # 根组件
│   ├── main.tsx                # 入口
│   └── types.ts                # 类型定义
├── src-tauri/                  # Rust 后端
│   └── src/
│       ├── main.rs             # 应用入口
│       ├── commands.rs         # 命令处理
│       ├── crypto.rs           # 加密模块
│       ├── db.rs               # 数据库层
│       ├── models.rs           # 数据模型
│       └── generators.rs       # 生成器
├── index.html                  # Vite 入口 HTML
├── package.json
├── tsconfig.json
├── vite.config.ts
└── LICENSE
```

---

## 更新日志

### v3.0.0 (2026-04-19)

从 v2.0.0 (Python) 完全重写至 Tauri 2 + React + Rust。

**功能**

- AES-256-GCM 加密 + Argon2id 密钥派生
- 主密码保护
- 两种条目类型：登录凭据 & API 密钥
- 完整增删改查
- 密码 & 用户名生成器
- 文件夹分类与收藏
- 搜索、自动锁定、深色模式、双语
- 完全离线运行

### 即将推出

> 暂未实现，将在后续版本中陆续推出。

- 生物识别解锁（Windows Hello / Touch ID）
- 密码泄露检测（Have I Been Pwned API）
- 导入/导出功能（CSV, JSON, 1Password, LastPass）
- TOTP 双因素认证支持
- 可选云端同步（端到端加密）
- 浏览器扩展集成
- 已有密码强度分析
- 自定义字段类型（备注、电话等）
- 多保险库支持

---

## 许可证

**专有软件 — 源码可见**

Copyright (c) 2026 [HYQJ932](https://github.com/HYQJ932). All rights reserved.

- 个人和学习用途：**免费**
- 商业用途：**需购买授权**

详见 [LICENSE](./LICENSE)。商业授权请通过 [GitHub](https://github.com/HYQJ932) 联系。
