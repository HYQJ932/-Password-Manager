# Password Manager

> [**English**](README.md) · [**中文**](README_CN.md)

A local-first, secure desktop password manager built with **Tauri 2 + React + Rust**.

All data is encrypted and stored locally. No cloud, no tracking, no telemetry.

---

## Download

**Latest Release: v3.0.0**

- [Download for Windows](https://github.com/HYQJ932/-Password-Manager/releases/tag/v3.0.0)
- [View all releases](https://github.com/HYQJ932/-Password-Manager/releases)

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

## Architecture

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

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite 6 |
| Backend | Rust, Tauri 2 |
| Database | SQLite (rusqlite, bundled) |
| Encryption | AES-256-GCM (aes-gcm 0.10) |
| Key Derivation | Argon2id (argon2 0.5) |

---

## Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- [Rust](https://www.rust-lang.org/tools/install) >= 1.70
- [Tauri CLI](https://v2.tauri.app/start/prerequisites/)

On Windows, you also need:
- Microsoft Visual Studio C++ Build Tools
- WebView2 (pre-installed on Windows 10/11)

---

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev

# Build for production
npm run tauri build
```

---

## Project Structure

```
password-manager/
├── src/                        # React frontend
│   ├── components/             # UI components
│   │   ├── LockScreen.tsx      # Lock/unlock screen
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   ├── VaultList.tsx       # Entry list
│   │   ├── VaultDetail.tsx     # Entry detail & editor
│   │   ├── Generator.tsx       # Password/username generator
│   │   └── Settings.tsx        # Settings page
│   ├── hooks/                  # React hooks
│   │   ├── useVault.ts         # Vault state management
│   │   ├── useI18n.ts          # i18n context hook
│   │   └── useClipboard.ts     # Clipboard helper
│   ├── i18n/
│   │   └── translations.ts     # EN/CN translation dict
│   ├── styles/
│   │   └── index.css           # Global styles
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Entry point
│   └── types.ts                # TypeScript types
├── src-tauri/                  # Rust backend
│   └── src/
│       ├── main.rs             # Tauri app entry
│       ├── commands.rs         # IPC command handlers
│       ├── crypto.rs           # Encryption module
│       ├── db.rs               # SQLite data layer
│       ├── models.rs           # Data models
│       └── generators.rs       # Generators
├── index.html                  # Vite entry HTML
├── package.json
├── tsconfig.json
├── vite.config.ts
└── LICENSE
```

---

## Changelog

### v3.0.0 (2026-04-19)

Complete rewrite from v2.0.0 (Python) to Tauri 2 + React + Rust.

**Features**

- AES-256-GCM encryption with Argon2id key derivation
- Master password protection
- Two entry types: Login and API Key
- Full CRUD operations
- Password & username generator
- Folder organization and favorites
- Search, auto-lock, dark mode, i18n
- Fully offline

### Planned Features

> Not yet implemented, coming in future releases.

- Biometric unlock (Windows Hello / Touch ID)
- Password breach detection (Have I Been Pwned API)
- Import/Export (CSV, JSON, 1Password, LastPass)
- TOTP (Two-Factor Authentication) support
- Cloud sync (optional, end-to-end encrypted)
- Browser extension integration
- Password strength analyzer
- Custom field types (notes, phone, etc.)
- Multi-vault support

---

## License

**Proprietary — Source Available**

Copyright (c) 2026 [HYQJ932](https://github.com/HYQJ932). All rights reserved.

- Personal and educational use: **Free**
- Commercial use: **Requires a paid license**

See [LICENSE](./LICENSE) for full terms. For commercial licensing, contact via [GitHub](https://github.com/HYQJ932).
