import { useState, useEffect } from "react";
import { useI18n } from "../hooks/useI18n";
import type { AppSettings, Folder, Language } from "../types";

interface SettingsProps {
  settings: AppSettings;
  folders: Folder[];
  onSaveSettings: (s: AppSettings) => Promise<void>;
  onSaveFolder: (f: Folder) => Promise<void>;
  onDeleteFolder: (id: string) => Promise<void>;
}

export default function Settings({
  settings,
  folders,
  onSaveSettings,
  onSaveFolder,
  onDeleteFolder,
}: SettingsProps) {
  const { t, lang, setLang } = useI18n();
  const [local, setLocal] = useState(settings);
  const [newFolder, setNewFolder] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setLocal(settings);
  }, [settings]);

  const handleSave = async () => {
    await onSaveSettings(local);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleAddFolder = async () => {
    if (!newFolder.trim()) return;
    await onSaveFolder({
      id: crypto.randomUUID(),
      name: newFolder.trim(),
    });
    setNewFolder("");
  };

  const handleDeleteFolder = async (id: string) => {
    if (confirm(t("deleteFolder"))) {
      await onDeleteFolder(id);
    }
  };

  const handleLanguageChange = async (l: Language) => {
    setLang(l);
    const updated = { ...local, language: l };
    setLocal(updated);
    await onSaveSettings(updated);
  };

  return (
    <div className="settings">
      <h2>{t("settings")}</h2>

      <div className="settings-section">
        <h3>{t("language")}</h3>
        <div className="type-toggle" style={{ maxWidth: 200 }}>
          <button
            className={`type-btn ${lang === "zh" ? "active" : ""}`}
            onClick={() => handleLanguageChange("zh")}
          >
            中文
          </button>
          <button
            className={`type-btn ${lang === "en" ? "active" : ""}`}
            onClick={() => handleLanguageChange("en")}
          >
            English
          </button>
        </div>
      </div>

      <div className="settings-section">
        <h3>{t("security")}</h3>
        <div className="field-group">
          <label>{t("autoLock")}</label>
          <select
            value={local.autoLockMinutes}
            onChange={(e) => setLocal({ ...local, autoLockMinutes: parseInt(e.target.value) })}
          >
            <option value={1}>1 {t("minutes")}</option>
            <option value={5}>5 {t("minutes")}</option>
            <option value={15}>15 {t("minutes")}</option>
            <option value={30}>30 {t("minutes")}</option>
            <option value={0}>{t("never")}</option>
          </select>
        </div>
      </div>

      <div className="settings-section">
        <h3>{t("appearance")}</h3>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={local.darkMode}
            onChange={(e) => setLocal({ ...local, darkMode: e.target.checked })}
          />
          {t("darkMode")}
        </label>
      </div>

      <div className="settings-section">
        <h3>{t("folders")}</h3>
        <div className="folder-add">
          <input
            type="text"
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
            placeholder={t("newFolder")}
            onKeyDown={(e) => e.key === "Enter" && handleAddFolder()}
          />
          <button className="btn-primary" onClick={handleAddFolder}>{t("addFolder")}</button>
        </div>
        <div className="folder-list">
          {folders.map((f) => (
            <div key={f.id} className="folder-item">
              <span>{f.name}</span>
              <button className="btn-icon delete-btn" onClick={() => handleDeleteFolder(f.id)}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          ))}
          {folders.length === 0 && <p className="text-muted">{t("noFolders")}</p>}
        </div>
      </div>

      <div className="settings-footer">
        <button className="btn-primary" onClick={handleSave}>
          {saved ? t("saved") : t("saveSettings")}
        </button>
      </div>
    </div>
  );
}
