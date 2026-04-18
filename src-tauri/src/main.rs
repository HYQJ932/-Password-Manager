#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod crypto;
mod db;
mod generators;
mod models;

use commands::*;
use db::Database;
use std::sync::Mutex;
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let app_dir = app.path().app_data_dir()
                .expect("Failed to get app data dir");
            std::fs::create_dir_all(&app_dir)
                .expect("Failed to create app data dir");

            let db_path = app_dir.join("vault.db");
            let database = Database::new(&db_path)
                .expect("Failed to initialize database");

            app.manage(AppState {
                db: database,
                crypto: Mutex::new(None),
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            is_initialized,
            setup_master_password,
            unlock,
            lock,
            get_all_entries,
            get_entry,
            save_entry,
            delete_entry,
            search_entries,
            generate_password_cmd,
            generate_username_cmd,
            get_settings,
            save_settings,
            get_folders,
            save_folder,
            delete_folder,
        ])
        .run(tauri::generate_context!())
        .expect("Error while running application");
}
