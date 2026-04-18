# Password Manager

> [**中文**](README.md) · [**English**](README_EN.md)

A local-first, secure desktop password manager built with **Tauri 2 + React + Rust**.

All data is encrypted and stored locally. No cloud, no tracking, no telemetry.

---

## Features

- **AES-256-GCM encryption** with Argon2id key derivation
- **Master password** protection with Argon2 hash verification
- **Two entry types**: Login (username + password + URL) and API Key
- **Full CRUD** operations for vault entries
- **Password generator** with configurable length, character sets, and ambiguity exclusion
- **Username generator** with multiple formats (word1234, word_word, word.word)
- **Folder organization** and favorites
- **Search** across all entries (name, username, URL, API key)
- **Auto-lock** with configurable timeout (1/5/15/30 min or never)
- **Dark / Light mode** with CSS custom properties
- **i18n**: English & 简体中文
- **One-click copy** to clipboard
- **Apple HIG-inspired** UI design

---

## Security

1. Master password is hashed with Argon2 and stored for verification only
2. Encryption key is derived via Argon2id with a random 32-byte salt
3. All sensitive data is encrypted with AES-256-GCM before storage
4. On lock, the encryption key is zeroized from memory
5. No network access — the app is fully offline

---

## Roadmap

> The following features are planned and will be implemented gradually. All remain fully offline and local-only.

### Security Enhancements
- **Master password change** — Full re-encryption within transaction, rollback on failure
- **Windows Hello quick unlock** — Biometric convenience login
- **Shamir secret sharing backup** — QR code shares for print storage, ≥M shares to recover
- **Read-only / viewer password** — Independent password, view-only access
- **Local audit log** — Encrypted operation records, query/clear/export

### Data Management
- **Password history** — Auto-save last 5 password changes, one-click restore
- **Automatic backup** — Post-write backup with configurable retention policy
- **Attachment support** — Encrypted file attachments (recovery codes, certs, SSH keys, etc.)
- **Scheduled encrypted snapshots** — Daily/weekly encrypted JSON export to local path
- **Multi-vault** — Independent databases with separate master passwords (personal/work)

### Experience Improvements
- **System tray** — Background常驻, right-click menu for quick actions
- **Global hotkeys** — Ctrl+Shift+L to lock, Ctrl+Shift+Space for quick search
- **Command palette (Ctrl+K)** — Fuzzy search + quick commands
- **Recently used sorting** — Smart sort by last access time
- **AMOLED pure black theme** — Power saving and eye-friendly
- **Virtual scrolling** — Smooth scrolling with thousands of entries
- **Nested folders + tags** — Infinite tree hierarchy + many-to-many tag filtering

### Entry Types
- **SSH Key type** — Public/private key and passphrase management
- **Secure Note type** — Pure encrypted long-text storage

### Toolchain
- **CLI version** — Command-line tool for scripting and operations
- **Portable mode** — USB-ready, all data stored alongside the executable

---

## Sponsor

If you find this tool helpful, consider sponsoring to support continued development ❤️

Alipay is recommended, credit card / Huabei supported:

![Alipay QR Code](donate.jpg)

---

## License

**Proprietary — Source Available**

Copyright (c) 2026 [HYQJ932](https://github.com/HYQJ932). All rights reserved.

- Personal and educational use: **Free**
- Commercial use: **Requires a paid license**

See [LICENSE](./LICENSE) for full terms.
