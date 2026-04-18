use crate::crypto::{self, CryptoManager};
use crate::db::Database;
use crate::generators;
use crate::models::*;
use std::sync::Mutex;
use tauri::State;

pub struct AppState {
    pub db: Database,
    pub crypto: Mutex<Option<CryptoManager>>,
}

#[tauri::command]
pub fn is_initialized(state: State<AppState>) -> Result<bool, String> {
    state.db.is_initialized()
}

#[tauri::command]
pub fn setup_master_password(password: String, state: State<AppState>) -> Result<(), String> {
    if state.db.is_initialized()? {
        return Err("Master password already set".to_string());
    }
    let hash = CryptoManager::hash_master_password(&password)?;
    let salt = crypto::generate_salt();
    state.db.setup_auth(&hash, &salt)?;

    let key = CryptoManager::derive_key(&password, &salt)?;
    let cm = CryptoManager::new(&key);
    *state.crypto.lock().unwrap() = Some(cm);

    // Save default settings
    let settings = AppSettings::default();
    state.db.save_setting("auto_lock_minutes", &settings.auto_lock_minutes.to_string())?;
    state.db.save_setting("dark_mode", &settings.dark_mode.to_string())?;
    state.db.save_setting("language", &settings.language)?;

    Ok(())
}

#[tauri::command]
pub fn unlock(password: String, state: State<AppState>) -> Result<bool, String> {
    let (hash, salt) = state.db.get_auth()?;
    if !CryptoManager::verify_master_password(&password, &hash)? {
        return Ok(false);
    }
    let key = CryptoManager::derive_key(&password, &salt)?;
    let cm = CryptoManager::new(&key);
    *state.crypto.lock().unwrap() = Some(cm);
    Ok(true)
}

#[tauri::command]
pub fn lock(state: State<AppState>) {
    *state.crypto.lock().unwrap() = None;
}

fn with_crypto<F, R>(state: &State<AppState>, f: F) -> Result<R, String>
where
    F: FnOnce(&CryptoManager) -> Result<R, String>,
{
    let guard = state.crypto.lock().unwrap();
    match guard.as_ref() {
        Some(cm) => f(cm),
        None => Err("Vault is locked".to_string()),
    }
}

#[tauri::command]
pub fn get_all_entries(state: State<AppState>) -> Result<Vec<VaultEntry>, String> {
    with_crypto(&state, |cm| state.db.get_all_entries(cm))
}

#[tauri::command]
pub fn get_entry(id: String, state: State<AppState>) -> Result<Option<VaultEntry>, String> {
    with_crypto(&state, |cm| state.db.get_entry(&id, cm))
}

#[tauri::command]
pub fn save_entry(mut entry: VaultEntry, state: State<AppState>) -> Result<(), String> {
    let now = chrono::Utc::now().timestamp();
    if entry.id.is_empty() {
        entry.id = uuid::Uuid::new_v4().to_string();
        entry.created_at = now;
    }
    entry.updated_at = now;
    with_crypto(&state, |cm| state.db.save_entry(&entry, cm))
}

#[tauri::command]
pub fn delete_entry(id: String, state: State<AppState>) -> Result<(), String> {
    state.db.delete_entry(&id)
}

#[tauri::command]
pub fn search_entries(query: String, state: State<AppState>) -> Result<Vec<VaultEntry>, String> {
    with_crypto(&state, |cm| state.db.search_entries(&query, cm))
}

#[tauri::command]
pub fn generate_password_cmd(config: PasswordGeneratorConfig) -> GeneratedPassword {
    generators::generate_password(&config)
}

#[tauri::command]
pub fn generate_username_cmd(config: UsernameConfig) -> String {
    generators::generate_username(&config)
}

#[tauri::command]
pub fn get_settings(state: State<AppState>) -> Result<AppSettings, String> {
    let auto_lock = state.db.get_setting("auto_lock_minutes")?;
    let dark_mode = state.db.get_setting("dark_mode")?;
    let language = state.db.get_setting("language")?.unwrap_or_else(|| "zh".to_string());

    Ok(AppSettings {
        auto_lock_minutes: auto_lock.and_then(|v| v.parse().ok()).unwrap_or(5),
        dark_mode: dark_mode.and_then(|v| v.parse().ok()).unwrap_or(false),
        language,
    })
}

#[tauri::command]
pub fn save_settings(settings: AppSettings, state: State<AppState>) -> Result<(), String> {
    state.db.save_setting("auto_lock_minutes", &settings.auto_lock_minutes.to_string())?;
    state.db.save_setting("dark_mode", &settings.dark_mode.to_string())?;
    state.db.save_setting("language", &settings.language)?;
    Ok(())
}

#[tauri::command]
pub fn get_folders(state: State<AppState>) -> Result<Vec<Folder>, String> {
    state.db.get_all_folders()
}

#[tauri::command]
pub fn save_folder(folder: Folder, state: State<AppState>) -> Result<(), String> {
    state.db.save_folder(&folder)
}

#[tauri::command]
pub fn delete_folder(id: String, state: State<AppState>) -> Result<(), String> {
    state.db.delete_folder(&id)
}
