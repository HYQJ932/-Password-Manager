# 密码管理器 v3.1.1

> 安全、轻量的本地密码管理桌面应用，基于 Tauri 2 + React 18 + Rust 构建。

![version](https://img.shields.io/badge/version-3.1.1-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![tauri](https://img.shields.io/badge/Tauri-2-orange)
![rust](https://img.shields.io/badge/Rust-stable-red)

[English README](./README_EN.md) · [更新日志](./CHANGELOG.md)

## 功能特性

- 🔐 **主密码保护** — Argon2id 密钥派生 + AES-256-GCM 加密
- 📁 **文件夹管理** — 支持多级嵌套文件夹分类
- 🔍 **智能搜索** — 快速搜索名称、用户名、网址、API Key（全内存解密后过滤，不持久化明文索引）
- 🎲 **密码生成器** — 可配置长度、字符类型、排除易混淆字符
- 👤 **用户名生成器** — 生成随机用户名
- 🌙 **深色模式** — 一键切换明暗主题
- 🌐 **多语言** — 中文 / English 界面
- ⏱️ **自动锁定** — 空闲 1 / 5 / 15 / 30 分钟后自动锁定
- ⭐ **收藏标记** — 快速访问重要条目
- 📋 **剪贴板自动清空** — 复制的密码 30 秒后自动清除

## 安全特性

### 密码学
- ✅ **AES-256-GCM** 认证加密保护条目内容
- ✅ **Argon2id** 密钥派生（显式参数：m=19456 KiB · t=2 · p=1）
- ✅ 分离的 **hash_salt / encrypt_salt**，防彩虹表攻击
- ✅ **常量时间**密码验证（`argon2::PasswordVerifier::verify_password`）
- ✅ **内存密钥清零**：主密钥 + AES key schedule（启用 `zeroize` feature）

### 运行时保护
- ✅ 解锁失败**指数退避**（1→2→4→8→16→32→60 秒，上限 60s），对抗脚本穷举
- ✅ 严格的 **Content Security Policy** 白名单，默认只允许 `'self'`
- ✅ 主密码**后端长度校验**（至少 8 字符），不依赖前端
- ✅ 剪贴板 **30 秒自动清空**（仅当内容未被用户替换时清除）
- ✅ 所有面向用户的错误消息统一中文化

### 数据保护
- ✅ 数据库事务保证原子性（密码轮换、文件夹级联删除等）
- ✅ `reset_vault` 启用 `secure_delete` 并执行 `VACUUM`，彻底擦除物理页残留
- ✅ 密钥派生参数**固化为常量**，防止依赖升级破坏已有 vault 的可解密性
- ✅ 启动失败自动写日志到 `%APPDATA%\com.password-manager.app\startup-error.log`

## 下载安装

### 方式一：下载预构建版本（推荐）

前往 [Releases](https://github.com/HYQJ932/-Password-Manager/releases) 下载 `password-manager.exe`，双击即可运行。

首次启动需要设置主密码（至少 8 字符）。**请妥善保管，丢失后无法恢复数据**。

### 方式二：从源码构建

前置依赖：
- [Node.js](https://nodejs.org/) ≥ 18
- [Rust](https://rustup.rs/) ≥ 1.75
- Windows SDK（Windows）/ Xcode CLT（macOS）/ `webkit2gtk` 等（Linux）

```bash
git clone https://github.com/HYQJ932/-Password-Manager.git
cd -Password-Manager
npm install

# 开发模式（热重载）
npm run tauri dev

# 构建发布版本（含 installer）
npm run tauri build

# 只产出 exe 不打 installer
npm run tauri build -- --no-bundle
```

构建产物位于 `src-tauri/target/release/password-manager.exe`。

## 技术栈

- **前端**：React 18 · TypeScript · Vite 6
- **后端**：Rust · Tauri 2
- **数据库**：SQLite（`rusqlite`）
- **加密**：`aes-gcm 0.10` · `argon2 0.5` · `zeroize 1`
- **测试**：`cargo test`（13 项）· Vitest（前端）

## 运行测试

```bash
# 后端单元测试（密码学、数据库、迁移、退避算法等）
cd src-tauri && cargo test

# 前端测试
npm test
```

## 项目结构

```
├── src/                   # React 前端
│   ├── components/        # UI 组件
│   ├── hooks/             # 自定义 Hook（含 __tests__）
│   ├── i18n/              # 中英文词典
│   └── styles/            # 样式
├── src-tauri/             # Rust 后端
│   ├── src/
│   │   ├── commands.rs    # Tauri IPC 命令
│   │   ├── crypto.rs      # AES-GCM + Argon2id
│   │   ├── db.rs          # SQLite 持久化
│   │   ├── generators.rs  # 密码 / 用户名生成
│   │   └── models.rs      # 数据模型
│   ├── capabilities/      # Tauri 权限配置
│   └── tauri.conf.json    # 应用元数据 + CSP
└── vitest.config.ts       # 前端测试配置
```

## 数据库迁移

应用启动时会自动迁移旧版数据库（schema version v1 → v5）。  
如遇严重问题可删除 `%APPDATA%\com.password-manager.app\vault.db` 重新创建（**会丢失数据**）。

## 贡献

欢迎提 Issue 或 PR：
- 改动请附相应测试（`cargo test` 或 `npm test` 需通过）
- Commit message 遵循[约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)（`feat:` / `fix:` / `refactor:` / `docs:` / `test:` / `chore:`）
- 大改动请先在 Issue 讨论设计

## 更新日志

详见 [CHANGELOG.md](./CHANGELOG.md)。

## 许可证

MIT
