use crate::crypto::CryptoManager;
use crate::models::*;
use base64::Engine;
use rusqlite::{Connection, params};
use std::path::PathBuf;
use std::sync::Mutex;

pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn new(db_path: &PathBuf) -> Result<Self, String> {
        let conn = Connection::open(db_path).map_err(|e| format!("Failed to open DB: {}", e))?;

        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS vault_entries (
                id TEXT PRIMARY KEY,
                entry_type TEXT NOT NULL,
                encrypted_data TEXT NOT NULL,
                folder TEXT,
                favorite INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS auth (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            );"
        ).map_err(|e| format!("Failed to create tables: {}", e))?;

        Ok(Self { conn: Mutex::new(conn) })
    }

    pub fn is_initialized(&self) -> Result<bool, String> {
        let conn = self.conn.lock().unwrap();
        let count: i64 = conn
            .query_row("SELECT COUNT(*) FROM auth", [], |row| row.get(0))
            .map_err(|e| format!("Query failed: {}", e))?;
        Ok(count > 0)
    }

    pub fn setup_auth(&self, password_hash: &str, salt: &[u8]) -> Result<(), String> {
        let salt_b64 = base64::engine::general_purpose::STANDARD.encode(salt);
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO auth (id, password_hash, salt) VALUES (1, ?1, ?2)",
            params![password_hash, salt_b64],
        ).map_err(|e| format!("Failed to store auth: {}", e))?;
        Ok(())
    }

    pub fn get_auth(&self) -> Result<(String, Vec<u8>), String> {
        let conn = self.conn.lock().unwrap();
        let (hash, salt_b64): (String, String) = conn
            .query_row(
                "SELECT password_hash, salt FROM auth WHERE id = 1",
                [],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )
            .map_err(|e| format!("Auth not found: {}", e))?;
        let salt = base64::engine::general_purpose::STANDARD
            .decode(&salt_b64)
            .map_err(|e| format!("Invalid salt: {}", e))?;
        Ok((hash, salt))
    }

    pub fn save_entry(&self, entry: &VaultEntry, crypto: &CryptoManager) -> Result<(), String> {
        let data = serde_json::to_string(entry).map_err(|e| e.to_string())?;
        let encrypted = crypto.encrypt(&data)?;
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR REPLACE INTO vault_entries (id, entry_type, encrypted_data, folder, favorite, created_at, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                entry.id,
                serde_json::to_string(&entry.entry_type).unwrap().trim_matches('"'),
                encrypted,
                entry.folder,
                entry.favorite as i64,
                entry.created_at,
                entry.updated_at,
            ],
        ).map_err(|e| format!("Failed to save entry: {}", e))?;
        Ok(())
    }

    pub fn get_all_entries(&self, crypto: &CryptoManager) -> Result<Vec<VaultEntry>, String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn
            .prepare("SELECT encrypted_data FROM vault_entries ORDER BY favorite DESC, updated_at DESC")
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([], |row| {
                let encrypted: String = row.get(0)?;
                Ok(encrypted)
            })
            .map_err(|e| e.to_string())?;

        let mut entries = Vec::new();
        for row in rows {
            let encrypted = row.map_err(|e| e.to_string())?;
            let decrypted = crypto.decrypt(&encrypted)?;
            let entry: VaultEntry =
                serde_json::from_str(&decrypted).map_err(|e| e.to_string())?;
            entries.push(entry);
        }
        Ok(entries)
    }

    pub fn get_entry(&self, id: &str, crypto: &CryptoManager) -> Result<Option<VaultEntry>, String> {
        let conn = self.conn.lock().unwrap();
        let result: Option<String> = conn
            .query_row(
                "SELECT encrypted_data FROM vault_entries WHERE id = ?1",
                params![id],
                |row| row.get(0),
            )
            .ok();

        match result {
            Some(encrypted) => {
                let decrypted = crypto.decrypt(&encrypted)?;
                let entry: VaultEntry =
                    serde_json::from_str(&decrypted).map_err(|e| e.to_string())?;
                Ok(Some(entry))
            }
            None => Ok(None),
        }
    }

    pub fn delete_entry(&self, id: &str) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM vault_entries WHERE id = ?1", params![id])
            .map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn search_entries(&self, query: &str, crypto: &CryptoManager) -> Result<Vec<VaultEntry>, String> {
        let all = self.get_all_entries(crypto)?;
        let q = query.to_lowercase();
        Ok(all
            .into_iter()
            .filter(|e| {
                e.name.to_lowercase().contains(&q)
                    || e.username.as_ref().map_or(false, |u| u.to_lowercase().contains(&q))
                    || e.url.as_ref().map_or(false, |u| u.to_lowercase().contains(&q))
                    || e.api_key.as_ref().map_or(false, |u| u.to_lowercase().contains(&q))
            })
            .collect())
    }

    pub fn save_setting(&self, key: &str, value: &str) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?1, ?2)",
            params![key, value],
        ).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn get_setting(&self, key: &str) -> Result<Option<String>, String> {
        let conn = self.conn.lock().unwrap();
        conn.query_row(
            "SELECT value FROM settings WHERE key = ?1",
            params![key],
            |row| row.get(0),
        ).ok().map_or(Ok(None), |v: String| Ok(Some(v)))
    }

    pub fn save_folder(&self, folder: &Folder) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR IGNORE INTO folders (id, name) VALUES (?1, ?2)",
            params![folder.id, folder.name],
        ).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn get_all_folders(&self) -> Result<Vec<Folder>, String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn
            .prepare("SELECT id, name FROM folders ORDER BY name COLLATE NOCASE")
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map([], |row| {
                Ok(Folder {
                    id: row.get(0)?,
                    name: row.get(1)?,
                })
            })
            .map_err(|e| e.to_string())?;

        let mut folders = Vec::new();
        for row in rows {
            folders.push(row.map_err(|e| e.to_string())?);
        }
        Ok(folders)
    }

    pub fn delete_folder(&self, id: &str) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM folders WHERE id = ?1", params![id])
            .map_err(|e| e.to_string())?;
        Ok(())
    }
}
