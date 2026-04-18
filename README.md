# Password Manager v3.0.0

A local-first, secure desktop password manager built with **Tauri 2 + React + Rust**.

All data is encrypted and stored locally. No cloud, no tracking, no telemetry.

一款本地优先的安全桌面密码管理器，基于 **Tauri 2 + React + Rust** 构建。所有数据加密后仅存储在本地，无云端、无追踪、无遥测。

---

## Download / 下载

**Latest Release: v3.0.0**

- [Download for Windows](https://github.com/HYQJ932/-Password-Manager/releases)
- [View all releases](https://github.com/HYQJ932/-Password-Manager/releases)

> Pre-built binaries are available in the [Releases](https://github.com/HYQJ932/-Password-Manager/releases) page.
> 预编译安装包请在 [Releases](https://github.com/HYQJ932/-Password-Manager/releases) 页面下载。

---

## Changelog / 更新日志

### v3.0.0 (2026-04-19)

**Core Features / 核心功能**

- AES-256-GCM encryption with Argon2id key derivation — AES-256-GCM 加密 + Argon2id 密钥派生
- Master password protection with Argon2 hash verification — 主密码保护 + Argon2 哈希验证
- Two entry types: Login (username + password + URL) and API Key — 两种条目类型：登录凭据 & API 密钥
- Full CRUD operations for vault entries — 密码条目完整增删改查
- Password generator with configurable length, character sets, and ambiguity exclusion — 可配置密码生成器
- Username generator with multiple formats (word1234, word_word, word.word) — 多格式用户名生成器
- Folder organization and favorites — 文件夹分类与收藏
- Search across all entries (name, username, URL, API key) — 全局搜索
- Auto-lock with configurable timeout (1/5/15/30 min or never) — 可配置自动锁定
- Dark / Light mode with CSS custom properties — 深色 / 浅色主题
- i18n: English & 简体中文 — 中英双语
- One-click copy to clipboard — 一键复制到剪贴板
- Apple HIG-inspired UI design — Apple 风格界面设计

**Security / 安全**

- All sensitive data encrypted with AES-256-GCM before storage — 所有敏感数据加密后存储
- Encryption key zeroized from memory on lock — 锁定时密钥从内存安全清除
- Fully offline, no network access — 完全离线运行

**Tech Stack / 技术栈**

- Frontend: React 18, TypeScript, Vite 6
- Backend: Rust, Tauri 2
- Database: SQLite (rusqlite, bundled)
- Encryption: AES-256-GCM (aes-gcm 0.10)
- Key Derivation: Argon2id (argon2 0.5)

---

### Planned Features / 即将推出

> The following features are not yet implemented but will be added in future releases.
> 以下功能暂未实现，将在后续版本中陆续推出。

- Biometric unlock (Windows Hello / Touch ID) — 生物识别解锁
- Password breach detection (Have I Been Pwned API) — 密码泄露检测
- Import/Export (CSV, JSON, 1Password, LastPass) — 导入/导出功能
- TOTP (Two-Factor Authentication) support — TOTP 双因素认证支持
- Cloud sync (optional, end-to-end encrypted) — 可选云端同步
- Browser extension integration — 浏览器扩展集成
- Password strength analyzer for existing entries — 已有密码强度分析
- Custom field types (notes, phone, etc.) — 自定义字段类型
- Multi-vault support — 多保险库支持

---

## Architecture / 架构

```
┌──────────────────────────────────────────┐
│           React Frontend (TypeScript)     │
│                                          │
│  LockScreen · Sidebar · VaultList        │
│  VaultDetail · Generator · Settings      │
│                                          │
│        ↕  Tauri IPC (invoke)             │
├──────────────────────────────────────────┤
│            Rust Backend (Tauri 2)         │
│                                          │
│  commands.rs — 16 IPC command handlers   │
│  crypto.rs   — AES-256-GCM + Argon2id   │
│  db.rs       — SQLite data layer         │
│  models.rs   — Data models (serde)       │
│  generators.rs — Password/username gen   │
│                                          │
│  Storage: local SQLite (vault.db)        │
└──────────────────────────────────────────┘
```

---

## Security / 安全机制

1. **Master password** is hashed with Argon2 and stored for verification only — 主密码仅存储 Argon2 哈希值
2. **Encryption key** is derived via Argon2id with a random 32-byte salt — 加密密钥通过 Argon2id + 随机盐值派生
3. **All sensitive data** is encrypted with AES-256-GCM before storage — 所有敏感数据加密后存储
4. **On lock**, the encryption key is zeroized from memory — 锁定时密钥从内存中安全清除
5. **No network access** — the app is fully offline — 完全离线，无网络访问

---

## Prerequisites / 前置要求

- [Node.js](https://nodejs.org/) >= 18
- [Rust](https://www.rust-lang.org/tools/install) >= 1.70
- [Tauri CLI](https://v2.tauri.app/start/prerequisites/)

On Windows, you also need:
- Microsoft Visual Studio C++ Build Tools
- WebView2 (pre-installed on Windows 10/11)

---

## Development / 开发

```bash
# Install dependencies / 安装依赖
npm install

# Run in development mode / 开发模式运行
npm run tauri dev

# Build for production / 构建生产版本
npm run tauri build
```

---

## Project Structure / 项目结构

```
password-manager/
├── src/                        # React frontend / 前端源码
│   ├── components/             # UI components / UI 组件
│   │   ├── LockScreen.tsx      # Lock/unlock screen / 锁屏界面
│   │   ├── Sidebar.tsx         # Navigation sidebar / 侧边栏导航
│   │   ├── VaultList.tsx       # Entry list / 条目列表
│   │   ├── VaultDetail.tsx     # Entry detail & editor / 条目详情编辑
│   │   ├── Generator.tsx       # Password/username generator / 生成器
│   │   └── Settings.tsx        # Settings page / 设置页面
│   ├── hooks/                  # React hooks
│   │   ├── useVault.ts         # Vault state management / 保险库状态管理
│   │   ├── useI18n.ts          # i18n context hook / 国际化
│   │   └── useClipboard.ts     # Clipboard helper / 剪贴板
│   ├── i18n/
│   │   └── translations.ts     # EN/CN translation dict / 翻译字典
│   ├── styles/
│   │   └── index.css           # Global styles / 全局样式
│   ├── App.tsx                 # Root component / 根组件
│   ├── main.tsx                # Entry point / 入口
│   └── types.ts                # TypeScript types / 类型定义
├── src-tauri/                  # Rust backend / 后端源码
│   └── src/
│       ├── main.rs             # Tauri app entry / 应用入口
│       ├── commands.rs         # IPC command handlers / 命令处理
│       ├── crypto.rs           # Encryption module / 加密模块
│       ├── db.rs               # SQLite data layer / 数据库层
│       ├── models.rs           # Data models / 数据模型
│       └── generators.rs       # Generators / 生成器
├── index.html                  # Vite entry HTML
├── package.json
├── tsconfig.json
├── vite.config.ts
└── LICENSE
```

---

## License / 许可证

**Proprietary — Source Available**

Copyright (c) 2026 [HYQJ932](https://github.com/HYQJ932). All rights reserved.

- Personal and educational use: **Free** / 个人和学习用途：**免费**
- Commercial use: **Requires a paid license** / 商业用途：**需购买授权**

See [LICENSE](./LICENSE) for full terms. For commercial licensing, contact via [GitHub](https://github.com/HYQJ932).

详见 [LICENSE](./LICENSE)。商业授权请通过 [GitHub](https://github.com/HYQJ932) 联系。
