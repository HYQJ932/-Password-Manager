# 密码管理器

一个功能完善的本地密码管理器，使用 AES 加密保护数据安全。

## 功能特性

- **主密码保护** — PBKDF2 + Fernet 加密，主密码解锁数据库
- **CRUD 操作** — 完整的添加/编辑/删除密码条目
- **实时搜索** — 按标题、用户名、网址、备注搜索
- **分类管理** — 自定义分类筛选
- **密码/用户名生成器** — 可自定义长度和字符类型
- **TOTP 2FA** — 内置双重验证码管理，支持 `otpauth://` URI 解析
- **一键复制** — 右键菜单快速复制密码/用户名/TOTP
- **记住密码** — Windows DPAPI 加密存储主密码，免登录
- **本地加密存储** — AES 加密，数据永不泄露

## 快速开始

### 方式一：直接运行 exe

1. 从 [Releases](../../releases) 页面下载最新的 `密码管理器.exe`
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
├── src/
│   ├── data_store.py    # 数据存储管理
│   ├── encryption.py    # 加密模块 (PBKDF2 + Fernet)
│   ├── generators.py    # 密码/用户名生成器
│   └── totp.py          # TOTP 2FA 模块
└── release/             # 打包好的 exe 文件
```

## 使用说明

### 添加 TOTP 2FA

1. 在目标网站开启两步验证
2. 获取 `otpauth://` URI 或密钥
3. 编辑对应账号，点击 TOTP 字段的「URI」按钮粘贴，或点击「生成」创建新密钥
4. 点击侧栏「🔑 2FA 验证码」查看所有验证码

### 记住密码

登录界面勾选「记住密码」，下次启动自动解锁。密码使用 Windows DPAPI 加密存储，仅当前用户可解密。

## 许可证

MIT
