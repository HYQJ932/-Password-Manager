import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useVault } from "./hooks/useVault";
import { I18nContext } from "./hooks/useI18n";
import { translations } from "./i18n/translations";
import type { Lang } from "./i18n/translations";
import LockScreen from "./components/LockScreen";
import Sidebar from "./components/Sidebar";
import VaultList from "./components/VaultList";
import VaultDetail from "./components/VaultDetail";
import Generator from "./components/Generator";
import Settings from "./components/Settings";
import type { VaultEntry, View, VaultFilter } from "./types";

export default function App() {
  const vault = useVault();
  const [view, setView] = useState<View>("vault");
  const [filter, setFilter] = useState<VaultFilter>("all");
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<VaultEntry | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const idleTimerRef = useRef<number | null>(null);
  const [lang, setLangState] = useState<Lang>("zh");

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    vault.checkInitialized().catch((e) => {
      console.error("Init error:", e);
      setError(String(e));
    });
  }, []);

  // Sync language from settings
  useEffect(() => {
    if (vault.settings.language) {
      setLangState(vault.settings.language);
    }
  }, [vault.settings.language]);

  // Auto-lock timer
  useEffect(() => {
    if (vault.locked || vault.settings.autoLockMinutes === 0) return;

    const resetTimer = () => {
      if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current);
      idleTimerRef.current = window.setTimeout(() => {
        vault.lock();
      }, vault.settings.autoLockMinutes * 60 * 1000);
    };

    const events = ["mousedown", "keydown", "scroll", "mousemove"];
    events.forEach((e) => window.addEventListener(e, resetTimer));
    resetTimer();

    return () => {
      events.forEach((e) => window.removeEventListener(e, resetTimer));
      if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current);
    };
  }, [vault.locked, vault.settings.autoLockMinutes]);

  // Dark mode
  useEffect(() => {
    document.body.classList.toggle("dark", vault.settings.darkMode);
  }, [vault.settings.darkMode]);

  const handleSearch = useCallback(
    async (q: string) => {
      setSearchQuery(q);
      await vault.searchEntries(q);
    },
    [vault.searchEntries]
  );

  const handleNewEntry = () => {
    setSelectedEntry(null);
    setIsCreating(true);
  };

  const handleSelectEntry = (entry: VaultEntry) => {
    setSelectedEntry(entry);
    setIsCreating(false);
  };

  const handleSave = async (entry: VaultEntry) => {
    await vault.saveEntry(entry);
    setIsCreating(false);
    if (entry.id) {
      setSelectedEntry(entry);
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setSelectedEntry(null);
  };

  const handleSetLang = useCallback((l: Lang) => {
    setLangState(l);
  }, []);

  const t = useCallback(
    (key: keyof typeof translations.en): string => {
      return translations[lang]?.[key] ?? translations.en[key] ?? key;
    },
    [lang]
  );

  const i18nValue = useMemo(() => ({ lang, t, setLang: handleSetLang }), [lang, t, handleSetLang]);

  // Show toast error for vault errors
  useEffect(() => {
    if (vault.lastError) {
      console.error(vault.lastError);
      // Show inline toast
      const toast = document.createElement("div");
      toast.textContent = vault.lastError;
      toast.style.cssText = `
        position: fixed; top: 16px; right: 16px; z-index: 9999;
        padding: 12px 20px; border-radius: 12px; background: #ff3b30; color: white;
        font-size: 14px; font-family: -apple-system, sans-serif;
        box-shadow: 0 4px 16px rgba(255,59,48,0.3); max-width: 400px;
        word-break: break-word; cursor: pointer;
      `;
      toast.onclick = () => toast.remove();
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 8000);
    }
  }, [vault.lastError]);

  // Show filtered entries
  const displayedEntries = selectedFolder
    ? vault.entries.filter((e) => e.folder === selectedFolder)
    : vault.entries;

  if (error) {
    return (
      <div style={{ padding: 40, fontFamily: "monospace" }}>
        <h2>出错了</h2>
        <pre style={{ color: "red", whiteSpace: "pre-wrap" }}>{error}</pre>
      </div>
    );
  }

  if (vault.initialized === null) return null;

  if (vault.locked) {
    return (
      <I18nContext.Provider value={i18nValue}>
        <LockScreen
          initialized={vault.initialized}
          onSetup={vault.setupPassword}
          onUnlock={vault.unlock}
        />
      </I18nContext.Provider>
    );
  }

  return (
    <I18nContext.Provider value={i18nValue}>
      <div className="app-layout">
        <Sidebar
          view={view}
          filter={filter}
          folders={vault.folders}
          selectedFolder={selectedFolder}
          onViewChange={setView}
          onFilterChange={setFilter}
          onFolderSelect={setSelectedFolder}
          onLock={vault.lock}
        />
        <main className="main-content">
          {view === "vault" && (
            <div className="vault-layout">
              <VaultList
                entries={displayedEntries}
                filter={filter}
                selectedId={selectedEntry?.id || null}
                searchQuery={searchQuery}
                onSearch={handleSearch}
                onSelect={handleSelectEntry}
                onNew={handleNewEntry}
              />
              <VaultDetail
                entry={selectedEntry}
                isNew={isCreating}
                folders={vault.folders}
                onSave={handleSave}
                onDelete={vault.deleteEntry}
                onCancel={handleCancel}
              />
            </div>
          )}
          {view === "generator" && <Generator />}
          {view === "settings" && (
            <Settings
              settings={vault.settings}
              folders={vault.folders}
              onSaveSettings={vault.saveSettings}
              onSaveFolder={vault.saveFolder}
              onDeleteFolder={vault.deleteFolder}
            />
          )}
        </main>
      </div>
    </I18nContext.Provider>
  );
}
