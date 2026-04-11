# 密码管理器

一个功能完善的本地密码管理器，使用 AES-256 加密保护数据安全。

## 功能特性

- **主密码保护** — PBKDF2 派生密钥 + AES-256-GCM 加密
- **CRUD 操作** — 完整的添加/编辑/删除密码条目
- **实时搜索** — 按标题、用户名、网址、备注搜索
- **分类管理** — 自定义分类筛选
- **密码/用户名生成器** — 可自定义长度和字符类型
- **密码强度检测** — 实时评估密码强度（zxcvbn），纯本地
- **OTP 双因素认证** — 支持 TOTP（基于时间）和 HOTP（基于计数器），独立验证码面板
- **密码分享** — 生成 6 位分享码 + 加密数据，对方输入即可获取
- **导入导出** — 支持 1Password / LastPass / Bitwarden CSV 格式，OTP 批量导入导出
- **一键复制** — 右键菜单 + 字段旁 📋 按钮快速复制
- **记住密码** — Windows DPAPI 加密存储主密码，免登录
- **本地加密存储** — AES-256-GCM 加密，数据永不泄露

## 快速开始

### 方式一：直接运行 exe

1. 从 [Releases](../../releases) 页面下载最新的 `PasswordManager.exe`
2. 双击运行，首次启动设置主密码即可使用

### 方式二：从源码运行

**环境要求**：Python 3.10+

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

## 构建 exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "密码管理器" main.py
```

构建产物位于 `dist/` 目录。

## 项目结构

```
├── main.py              # 主入口（UI + 登录窗口）
├── requirements.txt     # Python 依赖
├── .gitignore           # Git 忽略规则
├── README.md            # 本文件
├── src/
│   ├── data_store.py    # 数据存储管理
│   ├── encryption.py    # 加密模块 (AES-256-GCM + PBKDF2)
│   ├── generators.py    # 密码/用户名生成器
│   └── totp.py          # OTP 模块 (TOTP + HOTP)
└── release/             # 打包好的 exe 文件
```

## 使用说明

### 添加 OTP 双因素认证

1. 在目标网站开启两步验证
2. 获取 `otpauth://` URI 或密钥
3. 编辑对应账号，在 OTP 区域选择类型（TOTP / HOTP），点击「URI」粘贴或点击「生成」创建新密钥
4. 点击侧栏「🔑 OTP 验证码」查看所有验证码

### 导入/导出 OTP

- **导入**：点击侧栏「📥 导入 OTP」，粘贴 `otpauth://` URI（每行一个），自动解析并添加账号
- **导出**：点击侧栏「📤 导出 OTP」，将所有 OTP 导出为 `otpauth://` URI 到剪贴板

### 导入/导出 CSV

- **导入**：点击侧栏「📥 导入 CSV」，粘贴 1Password / LastPass / Bitwarden 导出的 CSV 内容
- **导出**：点击侧栏「📤 导出 CSV」，将全部账号导出为 CSV 到剪贴板

### 密码分享

1. 右键点击要分享的账号，选择「分享」
2. 复制生成的 6 位分享码和加密数据
3. 对方打开密码管理器，点击侧栏「📨 接收分享」
4. 输入分享码和加密数据，即可获取账号信息

### 记住密码

登录界面勾选「记住密码」，下次启动自动解锁。密码使用 Windows DPAPI 加密存储，仅当前用户可解密。

## 许可证

MIT
