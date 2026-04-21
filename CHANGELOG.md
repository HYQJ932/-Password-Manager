# 更新日志

本文件记录密码管理器的所有重要变更。
格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [3.1.1] - 2026-04-22

**安全强化版本**。修复多项潜在攻击面与用户体验问题，共 18 项变更，全部通过 13 个 Rust 测试 + 2 个 TypeScript 测试。变更分四个批次交付：

- **R1 P0 安全硬伤**：`setup_master_password` 长度校验 · 乱码修复 · CSP · aes-gcm `zeroize` feature
- **R2 P1 密码学 + 健壮性**：常量时间比较 · unlock 退避 · 强度对齐 · unwrap 清理 · 错误消息中文化
- **R3 P2 质量 + UX**：启动日志 · Argon2 参数固化 · VACUUM · 移除「永不锁定」 · 剪贴板自动清空 · .gitignore
- **R4 P3 工程化**：Settings i18n 清理 · HTML lang 动态化 · Vitest 测试骨架

### 🔒 安全

- **主密码验证改用常量时间比较**：`argon2::PasswordVerifier::verify_password` 取代字符串相等比较，消除理论性时序侧信道
- **AES key schedule 零化**：`aes-gcm` 启用 `zeroize` feature，`Aes256Gcm` Drop 时清除内部 key schedule（此前仅清了主密钥）
- **显式 Content Security Policy 白名单**：`tauri.conf.json` 从 `"csp": null` 改为严格白名单（`default-src 'self'`、`script-src 'self'`、`connect-src 'self' ipc:` 等）
- **主密码长度后端校验**：`setup_master_password` 后端拒绝 `< 8` 字符，不再依赖前端 JS 校验
- **unlock 失败指数退避**：0 / 0 / 1 / 2 / 4 / 8 / 16 / 32 / 60 秒（上限 60s），对抗脚本穷举
- **Argon2 参数固化为常量**：`m=19456, t=2, p=1` 不再依赖 crate 默认值，防止依赖升级让旧 vault 无法解密

### 🛠 改进

- 所有面向用户的错误消息中文化（`crypto.rs` / `commands.rs` / `db.rs`，共 ~50 条）
- 密码强度评估器对齐前端，基于**实际字符**而非配置项打分
- `db.rs` 16 处 `.lock().unwrap()` 改为 `.map_err(...)`，mutex 毒化时不再 panic，优雅返回错误
- `reset_vault` commit 后追加 `VACUUM`，彻底回收物理文件中的敏感数据残留
- **剪贴板 30 秒自动清空**：仅当剪贴板内容未被新复制覆盖时才清除，避免错误覆盖用户正常剪贴
- **启动失败写日志**：release 模式 stderr 不可见，失败信息改写到 `%APPDATA%\com.password-manager.app\startup-error.log`
- 移除「永不锁定」自动锁定选项；旧设置（0 分钟）自动迁移为 5 分钟并弹出一次性迁移通知
- 顶层切换语言同步保存到后端；HTML `lang` 属性跟随界面语言变为 `zh-CN` / `en`
- `Settings.tsx` 硬编码中英文字符串改走 i18n 系统；`FolderTreeRow` 独立 `useI18n`

### 🐛 修复

- `useVault.ts` 两处中文错误消息乱码（UTF-8 字节被错误按 GBK 显示导致的伪字符）

### 🧪 测试

新增 5 个后端测试 + 2 个前端测试：

- `crypto::verify_master_password_should_reject_wrong_password`
- `crypto::verify_master_password_should_return_err_for_invalid_hash_format`
- `crypto::argon2_params_should_match_recommended_defaults`
- `commands::compute_backoff_should_grow_exponentially_and_cap_at_60s`
- `generators::evaluate_strength_should_score_by_actual_characters`
- `flattenTree` 前端用例（深度优先展平 + 空输入，Vitest）

### 🔧 维护

- 新增 Tauri 命令 `consume_migration_notice`
- `.gitignore` 加入 `/password-manager.exe`（发布走 Releases 附件，不入仓库）
- 清理 Rust 源文件中的英文 rustdoc 注释，按新规范「默认不写；需要时中文」
- `CryptoManager::verify_master_password_with_salt` 重命名为 `verify_master_password`，移除无用的 salt 参数（PHC 格式 hash 已含 salt）

### ⚠️ 破坏性说明

- **「永不锁定」选项已移除**：用过此选项的用户启动后会看到一次性 toast 提示，自动锁定时间被迁移为 5 分钟，可在设置中自行调整
- 其余变更均**向后兼容**，现有 `vault.db` 可直接使用，无需迁移数据

## [3.1.0] - 更早

首个公开版本。
