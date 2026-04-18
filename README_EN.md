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
