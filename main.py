import customtkinter as ctk
import pyperclip
import webbrowser
import json
import os
from src.data_store import DataStore
from src.generators import generate_password, generate_username
from src.totp import generate_totp_secret, get_totp_code, get_totp_uri, verify_totp


def parse_otpauth_uri(uri: str) -> dict:
    """Parse an otpauth:// URI and extract account info.

    Returns dict with keys: type, secret, issuer, account, digits, algorithm, period
    """
    import re
    from urllib.parse import unquote, urlparse, parse_qs

    result = {}
    uri = uri.strip()
    parsed = urlparse(uri)

    if parsed.scheme != "otpauth":
        return result

    result["type"] = parsed.hostname or "totp"  # totp or hotp
    # Path is like /Issuer:AccountName or /AccountName
    path = unquote(parsed.path).lstrip("/")
    if ":" in path:
        parts = path.split(":", 1)
        result["issuer"] = parts[0].strip()
        result["account"] = parts[1].strip()
    else:
        result["account"] = path

    params = parse_qs(parsed.query)
    result["secret"] = params.get("secret", [""])[0]
    result["issuer"] = result.get("issuer", params.get("issuer", [""])[0])
    result["digits"] = params.get("digits", ["6"])[0]
    result["algorithm"] = params.get("algorithm", ["SHA1"])[0]
    result["period"] = params.get("period", ["30"])[0]

    return result


# --- Remember-me: secure storage via Windows DPAPI ---
REMEMBER_FILE = "remember.bin"

def _save_remember(password: str):
    """Save password encrypted via Windows DPAPI."""
    try:
        import win32crypt
        blob = win32crypt.CryptProtectData(
            password.encode("utf-16-le"),
            "PasswordManager",
            None, None, None, 0
        )
        with open(REMEMBER_FILE, "wb") as f:
            f.write(blob)
    except Exception:
        pass

def _load_remember() -> str:
    """Load and decrypt saved password via Windows DPAPI."""
    if not os.path.exists(REMEMBER_FILE):
        return ""
    try:
        import win32crypt
        with open(REMEMBER_FILE, "rb") as f:
            blob = f.read()
        result = win32crypt.CryptUnprotectData(blob, None, None, None, 0)
        return result[1].decode("utf-16-le")
    except Exception:
        return ""

def _delete_remember():
    """Remove saved password file."""
    if os.path.exists(REMEMBER_FILE):
        os.remove(REMEMBER_FILE)


class PasswordManagerApp:
    """Main password manager application window."""

    def __init__(self):
        self.store = DataStore()
        self.current_entry_id = None

        # Setup main window
        self.window = ctk.CTk()
        self.window.title("密码管理器")
        self.window.geometry("1100x700")
        self.window.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Data
        self.entries = []
        self.filtered_entries = []
        self.categories = []
        self.selected_category = "全部"

        # Build UI
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.window, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=1)

        # Main area
        self.main_area = ctk.CTkFrame(self.window, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        # Title
        title = ctk.CTkLabel(
            self.sidebar, text="密码管理器",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(20, 10))

        # Add button
        add_btn = ctk.CTkButton(
            self.sidebar, text="+ 添加密码",
            command=self._show_add_dialog, width=180,
        )
        add_btn.pack(pady=5)

        # Generator button
        gen_btn = ctk.CTkButton(
            self.sidebar, text="密码生成器",
            command=self._show_generator, width=180,
        )
        gen_btn.pack(pady=5)

        # TOTP button
        totp_btn = ctk.CTkButton(
            self.sidebar, text="🔑 2FA 验证码",
            command=self._show_totp_panel, width=180,
        )
        totp_btn.pack(pady=5)

        # Separator
        sep = ctk.CTkFrame(self.sidebar, height=2, fg_color="#444444")
        sep.pack(fill="x", padx=10, pady=10)

        # Category label
        cat_label = ctk.CTkLabel(
            self.sidebar, text="分类",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        cat_label.pack(pady=(0, 5))

        # Category list (scrollable)
        self.cat_frame = ctk.CTkScrollableFrame(
            self.sidebar, width=180, height=300,
        )
        self.cat_frame.pack(padx=10, fill="both", expand=True)

        self._build_categories()

        # Manage categories button
        manage_cat_btn = ctk.CTkButton(
            self.sidebar, text="管理分类",
            command=self._manage_categories, width=180,
        )
        manage_cat_btn.pack(pady=5)

        # Lock button
        lock_btn = ctk.CTkButton(
            self.sidebar, text="锁定",
            fg_color="#c0392b", hover_color="#e74c3c",
            command=self._lock, width=180,
        )
        lock_btn.pack(pady=(10, 10))

    def _build_categories(self):
        """Build category buttons in sidebar."""
        for widget in self.cat_frame.winfo_children():
            widget.destroy()

        self.categories = self.store.get_categories()

        # "All" button
        all_btn = ctk.CTkButton(
            self.cat_frame, text="全部",
            fg_color="#1f6feb" if self.selected_category == "全部" else "#333333",
            command=lambda: self._select_category("全部"),
        )
        all_btn.pack(fill="x", padx=5, pady=2)

        for cat in self.categories:
            btn = ctk.CTkButton(
                self.cat_frame, text=cat,
                fg_color="#1f6feb" if self.selected_category == cat else "#333333",
                command=lambda c=cat: self._select_category(c),
            )
            btn.pack(fill="x", padx=5, pady=2)

    def _select_category(self, category: str):
        self.selected_category = category
        self._build_categories()
        self._filter_entries()

    def _build_main_area(self):
        # Top bar
        top_bar = ctk.CTkFrame(self.main_area)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_bar.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(top_bar, text="搜索:")
        search_label.pack(side="left", padx=(5, 5))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_entries())
        search_entry = ctk.CTkEntry(
            top_bar, textvariable=self.search_var,
            placeholder_text="搜索标题、用户名、网址...",
            width=300,
        )
        search_entry.pack(side="left", padx=5)

        # Table header
        header_frame = ctk.CTkFrame(self.main_area)
        header_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        header_frame.grid_columnconfigure(0, weight=2)
        header_frame.grid_columnconfigure(1, weight=2)
        header_frame.grid_columnconfigure(2, weight=2)
        header_frame.grid_columnconfigure(3, weight=1)
        header_frame.grid_columnconfigure(4, weight=1)

        headers = ["标题", "用户名", "TOTP", "分类", "操作"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame, text=h,
                font=ctk.CTkFont(weight="bold", size=13),
            )
            lbl.grid(row=0, column=i, padx=5, pady=5, sticky="w")

        # Scrollable entry list
        self.entry_frame = ctk.CTkScrollableFrame(self.main_area)
        self.entry_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.entry_frame.grid_columnconfigure(0, weight=2)
        self.entry_frame.grid_columnconfigure(1, weight=2)
        self.entry_frame.grid_columnconfigure(2, weight=2)
        self.entry_frame.grid_columnconfigure(3, weight=1)
        self.entry_frame.grid_columnconfigure(4, weight=1)

    def _load_entries(self):
        self.entries = self.store.get_entries()
        self._filter_entries()

    def _filter_entries(self):
        query = self.search_var.get().lower()
        self.filtered_entries = []

        for e in self.entries:
            if self.selected_category != "全部" and e.get("category", "") != self.selected_category:
                continue
            if query:
                searchable = (
                    e.get("title", "") + e.get("username", "") +
                    e.get("url", "") + e.get("notes", "")
                ).lower()
                if query not in searchable:
                    continue
            self.filtered_entries.append(e)

        self._render_entries()

    def _render_entries(self):
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        for row, entry in enumerate(self.filtered_entries):
            self._render_entry_row(entry, row)

    def _render_entry_row(self, entry, row):
        # Title
        title_frame = ctk.CTkFrame(self.entry_frame, fg_color="transparent")
        title_frame.grid(row=row, column=0, sticky="w", padx=5, pady=3)
        title_frame.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            title_frame, text=entry.get("title", ""),
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        # Username (masked)
        user_frame = ctk.CTkFrame(self.entry_frame, fg_color="transparent")
        user_frame.grid(row=row, column=1, sticky="w", padx=5, pady=3)

        user_lbl = ctk.CTkLabel(
            user_frame, text=entry.get("username", ""),
            anchor="w",
        )
        user_lbl.grid(row=0, column=0, sticky="w")

        # TOTP
        totp_frame = ctk.CTkFrame(self.entry_frame, fg_color="transparent")
        totp_frame.grid(row=row, column=2, sticky="w", padx=5, pady=3)

        secret = entry.get("totp_secret", "")
        if secret:
            code, remaining = get_totp_code(secret)
            totp_text = f"{code} ({remaining}s)" if code else "无"
        else:
            totp_text = "无"

        totp_lbl = ctk.CTkLabel(
            totp_frame, text=totp_text,
            text_color="#2ecc71" if secret else "#888888",
            font=ctk.CTkFont(family="monospace", size=13),
            anchor="w",
        )
        totp_lbl.grid(row=0, column=0, sticky="w")

        # Category
        cat_lbl = ctk.CTkLabel(
            self.entry_frame, text=entry.get("category", ""),
            anchor="w",
        )
        cat_lbl.grid(row=row, column=3, sticky="w", padx=5, pady=3)

        # Action buttons
        action_frame = ctk.CTkFrame(self.entry_frame, fg_color="transparent")
        action_frame.grid(row=row, column=4, sticky="e", padx=5, pady=3)

        copy_user_btn = ctk.CTkButton(
            action_frame, text="用户名", width=55, height=25,
            font=ctk.CTkFont(size=10),
            command=lambda e=entry: self._copy(e.get("username", "")),
        )
        copy_user_btn.pack(side="left", padx=2)

        copy_pass_btn = ctk.CTkButton(
            action_frame, text="密码", width=55, height=25,
            font=ctk.CTkFont(size=10),
            command=lambda e=entry: self._copy(e.get("password", "")),
        )
        copy_pass_btn.pack(side="left", padx=2)

        copy_totp_btn = ctk.CTkButton(
            action_frame, text="TOTP", width=55, height=25,
            font=ctk.CTkFont(size=10),
            command=lambda e=entry: self._copy_totp(e),
        )
        copy_totp_btn.pack(side="left", padx=2)

        # Bind right-click and double-click on the row
        for frame in [title_frame, user_frame, totp_frame, action_frame,
                      title_lbl, user_lbl, totp_lbl, cat_lbl]:
            frame.bind("<Button-3>", lambda evt, e=entry: self._show_context_menu(evt, e))
            frame.bind("<Double-1>", lambda evt, e=entry: self._open_url(e))

        self.entry_frame.grid_rowconfigure(row, weight=1)

    def _copy(self, text: str):
        if text:
            pyperclip.copy(text)

    def _copy_totp(self, entry):
        secret = entry.get("totp_secret", "")
        code, _ = get_totp_code(secret)
        if code:
            pyperclip.copy(code)

    def _show_context_menu(self, event, entry):
        """Show right-click context menu."""
        menu = ctk.CTkToplevel(self.window)
        menu.title("")
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)

        menu.geometry(f"+{event.x_root}+{event.y_root}")

        # Background frame
        bg = ctk.CTkFrame(menu, fg_color="#2b2b2b", corner_radius=8)
        bg.pack(fill="both", expand=True)

        actions = [
            ("复制用户名", lambda: (self._copy(entry.get("username", "")), menu.destroy())),
            ("复制密码", lambda: (self._copy(entry.get("password", "")), menu.destroy())),
            ("复制TOTP", lambda: (self._copy_totp(entry), menu.destroy())),
            ("编辑", lambda: (self._show_edit_dialog(entry), menu.destroy())),
            ("删除", lambda: (self._delete_entry(entry), menu.destroy())),
        ]

        url = entry.get("url", "").strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            actions.append(("打开网址", lambda: (webbrowser.open(url), menu.destroy())))

        for text, cmd in actions:
            btn = ctk.CTkButton(
                bg, text=text, width=140, height=30,
                fg_color="transparent", hover_color="#444444",
                anchor="w", command=cmd,
            )
            btn.pack(fill="x", padx=5, pady=2)

        # Auto-close after 5 seconds
        def auto_close():
            try:
                menu.destroy()
            except Exception:
                pass

        self.window.after(5000, auto_close)

    def _open_url(self, entry):
        url = entry.get("url", "").strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)

    def _show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("添加密码")
        dialog.geometry("500x580")
        dialog.transient(self.window)
        dialog.grab_set()

        fields = {}
        row = 0

        labels = [
            ("标题", "title", ""),
            ("用户名", "username", ""),
            ("密码", "password", ""),
            ("网址", "url", ""),
            ("分类", "category", self.categories[0] if self.categories else "默认"),
            ("备注", "notes", ""),
            ("TOTP密钥", "totp_secret", ""),
        ]

        for label, key, default in labels:
            lbl = ctk.CTkLabel(dialog, text=label)
            lbl.grid(row=row, column=0, padx=15, pady=8, sticky="w")

            if key == "category":
                combo = ctk.CTkComboBox(dialog, values=self.categories, width=300)
                combo.set(default)
                combo.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                fields[key] = combo
            elif key == "password":
                frame = ctk.CTkFrame(dialog, fg_color="transparent")
                frame.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                entry = ctk.CTkEntry(frame, width=220, show="*")
                entry.pack(side="left")
                show_var = ctk.BooleanVar(value=False)
                show_btn = ctk.CTkCheckBox(
                    frame, text="显示", width=50,
                    variable=show_var,
                    command=lambda e=entry, v=show_var: e.configure(
                        show="" if v.get() else "*"
                    ),
                )
                show_btn.pack(side="left", padx=5)
                gen_btn = ctk.CTkButton(
                    frame, text="生成", width=50,
                    command=lambda e=entry: e.delete(0, "end") or e.insert(0, generate_password()),
                )
                gen_btn.pack(side="left", padx=2)
                fields[key] = entry
            elif key == "totp_secret":
                frame = ctk.CTkFrame(dialog, fg_color="transparent")
                frame.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                entry = ctk.CTkEntry(frame, width=220)
                entry.pack(side="left")
                gen_totp_btn = ctk.CTkButton(
                    frame, text="生成", width=50,
                    command=lambda e=entry: e.delete(0, "end") or e.insert(0, generate_totp_secret()),
                )
                gen_totp_btn.pack(side="left", padx=2)

                def _parse_uri():
                    from tkinter import simpledialog
                    uri = simpledialog.askstring("从 URI 解析", "粘贴 otpauth:// URI:")
                    if uri:
                        info = parse_otpauth_uri(uri)
                        if info.get("secret"):
                            entry.delete(0, "end")
                            entry.insert(0, info["secret"])

                parse_btn = ctk.CTkButton(
                    frame, text="URI", width=50,
                    command=_parse_uri,
                )
                parse_btn.pack(side="left", padx=2)
                fields[key] = entry
            elif key == "notes":
                entry = ctk.CTkTextbox(dialog, width=300, height=60)
                entry.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                fields[key] = entry
            else:
                entry = ctk.CTkEntry(dialog, width=300)
                entry.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                if key == "username":
                    gen_user_btn = ctk.CTkButton(
                        dialog, text="生成用户名", width=70,
                        command=lambda e=entry: e.delete(0, "end") or e.insert(0, generate_username()),
                    )
                    gen_user_btn.grid(row=row, column=2, padx=5, pady=8)
                fields[key] = entry

            row += 1

        # User style selector for username generation
        def save():
            data = {}
            for key, widget in fields.items():
                if isinstance(widget, ctk.CTkTextbox):
                    data[key] = widget.get("1.0", "end-1c")
                elif isinstance(widget, ctk.CTkComboBox):
                    data[key] = widget.get()
                else:
                    data[key] = widget.get()
            data.setdefault("category", "默认")
            self.store.add_entry(data)
            self._load_entries()
            dialog.destroy()

        save_btn = ctk.CTkButton(
            dialog, text="保存", width=120, height=35,
            command=save,
        )
        save_btn.grid(row=row, column=0, columnspan=3, pady=15)

    def _show_edit_dialog(self, entry):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("编辑密码")
        dialog.geometry("500x580")
        dialog.transient(self.window)
        dialog.grab_set()

        fields = {}
        row = 0

        labels = [
            ("标题", "title", entry.get("title", "")),
            ("用户名", "username", entry.get("username", "")),
            ("密码", "password", entry.get("password", "")),
            ("网址", "url", entry.get("url", "")),
            ("分类", "category", entry.get("category", "默认")),
            ("备注", "notes", entry.get("notes", "")),
            ("TOTP密钥", "totp_secret", entry.get("totp_secret", "")),
        ]

        for label, key, default in labels:
            lbl = ctk.CTkLabel(dialog, text=label)
            lbl.grid(row=row, column=0, padx=15, pady=8, sticky="w")

            if key == "category":
                combo = ctk.CTkComboBox(dialog, values=self.categories, width=300)
                combo.set(default)
                combo.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                fields[key] = combo
            elif key == "password":
                frame = ctk.CTkFrame(dialog, fg_color="transparent")
                frame.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                entry_w = ctk.CTkEntry(frame, width=220, show="*")
                entry_w.insert(0, default)
                entry_w.pack(side="left")
                show_var = ctk.BooleanVar(value=False)
                show_btn = ctk.CTkCheckBox(
                    frame, text="显示", width=50,
                    variable=show_var,
                    command=lambda e=entry_w, v=show_var: e.configure(
                        show="" if v.get() else "*"
                    ),
                )
                show_btn.pack(side="left", padx=5)
                gen_btn = ctk.CTkButton(
                    frame, text="生成", width=50,
                    command=lambda e=entry_w: e.delete(0, "end") or e.insert(0, generate_password()),
                )
                gen_btn.pack(side="left", padx=2)
                fields[key] = entry_w
            elif key == "totp_secret":
                frame = ctk.CTkFrame(dialog, fg_color="transparent")
                frame.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                entry_w = ctk.CTkEntry(frame, width=220)
                entry_w.insert(0, default)
                entry_w.pack(side="left")
                gen_totp_btn = ctk.CTkButton(
                    frame, text="生成", width=50,
                    command=lambda e=entry_w: e.delete(0, "end") or e.insert(0, generate_totp_secret()),
                )
                gen_totp_btn.pack(side="left", padx=2)

                def _parse_uri_edit():
                    from tkinter import simpledialog
                    uri = simpledialog.askstring("从 URI 解析", "粘贴 otpauth:// URI:")
                    if uri:
                        info = parse_otpauth_uri(uri)
                        if info.get("secret"):
                            entry_w.delete(0, "end")
                            entry_w.insert(0, info["secret"])
                        if info.get("account") and not fields.get("username", "").get():
                            if isinstance(fields.get("username"), ctk.CTkEntry):
                                fields["username"].delete(0, "end")
                                fields["username"].insert(0, info["account"])
                        if info.get("issuer") and not fields.get("title", "").get():
                            if isinstance(fields.get("title"), ctk.CTkEntry):
                                fields["title"].delete(0, "end")
                                fields["title"].insert(0, info["issuer"])

                parse_btn = ctk.CTkButton(
                    frame, text="URI", width=50,
                    command=_parse_uri_edit,
                )
                parse_btn.pack(side="left", padx=2)
                fields[key] = entry_w
            elif key == "notes":
                entry_w = ctk.CTkTextbox(dialog, width=300, height=60)
                entry_w.insert("1.0", default)
                entry_w.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                fields[key] = entry_w
            else:
                entry_w = ctk.CTkEntry(dialog, width=300)
                entry_w.insert(0, default)
                entry_w.grid(row=row, column=1, padx=15, pady=8, sticky="w")
                if key == "username":
                    gen_user_btn = ctk.CTkButton(
                        dialog, text="生成", width=60,
                        command=lambda e=entry_w: e.delete(0, "end") or e.insert(0, generate_username()),
                    )
                    gen_user_btn.grid(row=row, column=2, padx=5, pady=8)
                fields[key] = entry_w

            row += 1

        def save():
            data = {}
            for key, widget in fields.items():
                if isinstance(widget, ctk.CTkTextbox):
                    data[key] = widget.get("1.0", "end-1c")
                elif isinstance(widget, ctk.CTkComboBox):
                    data[key] = widget.get()
                else:
                    data[key] = widget.get()
            self.store.update_entry(entry["id"], data)
            self._load_entries()
            dialog.destroy()

        save_btn = ctk.CTkButton(
            dialog, text="保存", width=120, height=35,
            command=save,
        )
        save_btn.grid(row=row, column=0, columnspan=3, pady=15)

    def _delete_entry(self, entry):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("确认删除")
        dialog.geometry("350x150")
        dialog.transient(self.window)
        dialog.grab_set()

        lbl = ctk.CTkLabel(
            dialog, text=f"确定要删除 \"{entry.get('title', '')}\" 吗？",
            font=ctk.CTkFont(size=14),
        )
        lbl.pack(pady=20)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        def confirm():
            self.store.delete_entry(entry["id"])
            self._load_entries()
            dialog.destroy()

        ctk.CTkButton(
            btn_frame, text="删除", fg_color="#c0392b", width=80,
            command=confirm,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="取消", fg_color="#555555", width=80,
            command=dialog.destroy,
        ).pack(side="left", padx=10)

    def _show_generator(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("密码生成器")
        dialog.geometry("420x400")
        dialog.transient(self.window)
        dialog.grab_set()

        # Password display
        pass_var = ctk.StringVar(value="")
        pass_display = ctk.CTkEntry(
            dialog, textvariable=pass_var, width=320, height=40,
            font=ctk.CTkFont(family="monospace", size=16),
        )
        pass_display.pack(pady=15)

        # Length
        len_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        len_frame.pack(pady=5)

        ctk.CTkLabel(len_frame, text="长度:").pack(side="left", padx=5)
        len_var = ctk.IntVar(value=16)
        len_slider = ctk.CTkSlider(
            len_frame, from_=4, to=64, number_of_steps=60,
            variable=len_var, width=200,
        )
        len_slider.pack(side="left", padx=5)
        len_label = ctk.CTkLabel(len_frame, text="16")
        len_label.pack(side="left", padx=5)

        def update_len_label(*_):
            len_label.configure(text=str(int(len_var.get())))

        len_var.trace_add("write", update_len_label)

        # Options
        upper_var = ctk.BooleanVar(value=True)
        lower_var = ctk.BooleanVar(value=True)
        digits_var = ctk.BooleanVar(value=True)
        symbols_var = ctk.BooleanVar(value=True)

        opts = [
            ("大写字母 (A-Z)", upper_var),
            ("小写字母 (a-z)", lower_var),
            ("数字 (0-9)", digits_var),
            ("符号 (!@#$...)", symbols_var),
        ]

        for text, var in opts:
            cb = ctk.CTkCheckBox(dialog, text=text, variable=var)
            cb.pack(anchor="w", padx=30, pady=3)

        # Generate button
        def do_generate():
            pwd = generate_password(
                length=int(len_var.get()),
                use_upper=upper_var.get(),
                use_lower=lower_var.get(),
                use_digits=digits_var.get(),
                use_symbols=symbols_var.get(),
            )
            pass_var.set(pwd)

        gen_btn = ctk.CTkButton(
            dialog, text="生成密码", width=150, height=40,
            command=do_generate,
        )
        gen_btn.pack(pady=15)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(
            btn_frame, text="复制", width=80,
            command=lambda: pyperclip.copy(pass_var.get()),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="关闭", width=80,
            command=dialog.destroy,
        ).pack(side="left", padx=10)

        # Generate on open
        do_generate()

    def _manage_categories(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("管理分类")
        dialog.geometry("350x400")
        dialog.transient(self.window)
        dialog.grab_set()

        # Add new category
        add_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=10)

        new_cat_entry = ctk.CTkEntry(add_frame, placeholder_text="新分类名称", width=200)
        new_cat_entry.pack(side="left", padx=5)

        def add_cat():
            name = new_cat_entry.get().strip()
            if name:
                self.store.add_category(name)
                self._build_categories()
                new_cat_entry.delete(0, "end")

        ctk.CTkButton(add_frame, text="添加", width=60, command=add_cat).pack(
            side="left", padx=5
        )

        # List categories
        cat_list_frame = ctk.CTkScrollableFrame(dialog, width=300, height=280)
        cat_list_frame.pack(padx=15, pady=10, fill="both", expand=True)

        def refresh_list():
            for w in cat_list_frame.winfo_children():
                w.destroy()
            cats = self.store.get_categories()
            for cat in cats:
                row_frame = ctk.CTkFrame(cat_list_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(row_frame, text=cat).pack(side="left", padx=5)
                if cat != "默认":
                    ctk.CTkButton(
                        row_frame, text="删除", width=50, height=25,
                        fg_color="#c0392b", hover_color="#e74c3c",
                        command=lambda c=cat: (
                            self.store.delete_category(c),
                            refresh_list(),
                            self._build_categories(),
                        ),
                    ).pack(side="right", padx=5)

        refresh_list()

        ctk.CTkButton(dialog, text="关闭", command=dialog.destroy).pack(pady=10)

    def _show_totp_panel(self):
        """Show a dedicated TOTP codes panel with countdown timers."""
        # Collect all entries with TOTP secrets
        totp_entries = [e for e in self.entries if e.get("totp_secret", "").strip()]

        # Create floating window
        totp_win = ctk.CTkToplevel(self.window)
        totp_win.title("2FA 验证码")
        totp_win.geometry("480x600")
        totp_win.resizable(True, True)
        totp_win.minsize(350, 300)
        totp_win.attributes("-topmost", True)

        # Header
        ctk.CTkLabel(
            totp_win, text="双重验证码 (2FA)",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            totp_win, text="点击验证码即可复制到剪贴板",
            font=ctk.CTkFont(size=11), text_color="#888888",
        ).pack(pady=(0, 10))

        # Scrollable frame for TOTP items
        scroll = ctk.CTkScrollableFrame(totp_win)
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        # Store widgets for refresh
        totp_widgets = []

        def render_totp_items():
            for w in scroll.winfo_children():
                w.destroy()
            totp_widgets.clear()

            if not totp_entries:
                ctk.CTkLabel(
                    scroll, text="暂无 2FA 验证码\n编辑账号并填入 TOTP 密钥即可添加",
                    font=ctk.CTkFont(size=14), text_color="#888888",
                ).pack(pady=50)
                return

            for entry in totp_entries:
                title = entry.get("title", "未命名")
                username = entry.get("username", "")
                secret = entry.get("totp_secret", "").strip()

                # Container
                container = ctk.CTkFrame(scroll, fg_color="#2a2a2a", corner_radius=10)
                container.pack(fill="x", pady=4, padx=2)

                # Info row
                info_frame = ctk.CTkFrame(container, fg_color="transparent")
                info_frame.pack(fill="x", padx=10, pady=(10, 2))

                ctk.CTkLabel(
                    info_frame, text=title,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w",
                ).pack(side="left")

                if username:
                    ctk.CTkLabel(
                        info_frame, text=username,
                        font=ctk.CTkFont(size=11), text_color="#888888",
                        anchor="w",
                    ).pack(side="left", padx=(10, 0))

                # Code + remaining
                code_frame = ctk.CTkFrame(container, fg_color="transparent")
                code_frame.pack(fill="x", padx=10, pady=5)

                code_label = ctk.CTkLabel(
                    code_frame, text="------",
                    font=ctk.CTkFont(family="monospace", size=28, weight="bold"),
                    text_color="#2ecc71",
                    anchor="center",
                )
                code_label.pack(fill="x")

                time_frame = ctk.CTkFrame(container, fg_color="transparent")
                time_frame.pack(fill="x", padx=10, pady=(0, 10))

                time_label = ctk.CTkLabel(
                    time_frame, text="",
                    font=ctk.CTkFont(size=11), text_color="#888888",
                    anchor="w",
                )
                time_label.pack(side="left")

                # Progress bar (Canvas-based)
                progress_canvas = ctk.CTkCanvas(
                    time_frame, height=4, bg="#333333",
                    highlightthickness=0,
                )
                progress_canvas.pack(side="right", fill="x", expand=True)

                def make_update(widgets, sec):
                    def update():
                        code, remaining = get_totp_code(secret)
                        code_text = code or "------"
                        color = "#2ecc71" if remaining > 10 else "#f39c12" if remaining > 5 else "#e74c3c"
                        widgets["code"].configure(text=code_text, text_color=color)
                        widgets["time"].configure(text=f"剩余 {remaining}s")

                        # Update progress bar
                        progress = remaining / 30
                        w = int(progress * 120)
                        widgets["canvas"].delete("bar")
                        fill_color = color
                        widgets["canvas"].create_rectangle(0, 0, w, 4, fill=fill_color, tags="bar")

                        totp_win.after(1000, update)
                    return update

                widgets = {"code": code_label, "time": time_label, "canvas": progress_canvas}
                totp_widgets.append(widgets)

                # Click to copy
                def on_copy(clabel=code_label, sec=secret):
                    c, _ = get_totp_code(sec)
                    if c:
                        pyperclip.copy(c)
                        clabel.configure(text="✓ 已复制", text_color="#3498db")
                        totp_win.after(1500, lambda: on_copy_restore(clabel, sec))

                def on_copy_restore(clabel, sec):
                    c, _ = get_totp_code(sec)
                    if c:
                        clabel.configure(text=c)
                    else:
                        clabel.configure(text="------")

                code_label.bind("<Button-1>", lambda evt, f=on_copy: f())
                code_label.configure(cursor="hand2")

        render_totp_items()

        # Start refresh timers
        for widgets in totp_widgets:
            update_fn = None
            # Trigger first render
            code, remaining = get_totp_code(
                [e for e in totp_entries if e.get("totp_secret", "").strip()][0]
                if totp_entries else ""
            )

        # Simple approach: just trigger the first render cycle
        # We use the after mechanism built into update closures
        # Let me simplify
        def start_refresh_for(widgets, secret):
            def update():
                code, remaining = get_totp_code(secret)
                code_text = code or "------"
                color = "#2ecc71" if remaining > 10 else "#f39c12" if remaining > 5 else "#e74c3c"
                widgets["code"].configure(text=code_text, text_color=color)
                widgets["time"].configure(text=f"剩余 {remaining}s")
                progress = remaining / 30
                w = max(2, int(progress * 120))
                widgets["canvas"].delete("bar")
                widgets["canvas"].create_rectangle(0, 0, w, 4, fill=color, tags="bar")
                totp_win.after(1000, update)
            update()

        for i, entry in enumerate(totp_entries):
            if i < len(totp_widgets):
                start_refresh_for(totp_widgets[i], entry.get("totp_secret", "").strip())

        ctk.CTkButton(totp_win, text="关闭", command=totp_win.destroy, width=100).pack(pady=10)

    def _lock(self):
        self.window.destroy()
        show_login_window()

    def run(self):
        self._start_totp_refresh()
        self.window.mainloop()

    def _start_totp_refresh(self):
        """Refresh TOTP codes every second."""
        self._render_entries()
        self.window.after(1000, self._start_totp_refresh)


def show_login_window():
    """Show the login/create master password screen."""
    login_window = ctk.CTk()
    login_window.title("密码管理器 - 登录")
    login_window.geometry("400x380")
    login_window.resizable(True, True)
    login_window.minsize(350, 300)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    store = DataStore()

    # Title
    title = ctk.CTkLabel(
        login_window, text="密码管理器",
        font=ctk.CTkFont(size=24, weight="bold"),
    )
    title.pack(pady=(30, 5))

    subtitle = ctk.CTkLabel(
        login_window, text="输入主密码以继续",
        font=ctk.CTkFont(size=14),
        text_color="#888888",
    )
    subtitle.pack(pady=(0, 20))

    # Password entry
    pass_var = ctk.StringVar()

    frame = ctk.CTkFrame(login_window, fg_color="transparent")
    frame.pack(fill="x", padx=40)

    ctk.CTkLabel(frame, text="主密码:", font=ctk.CTkFont(size=14)).pack(
        side="left", padx=(0, 10)
    )

    pass_entry = ctk.CTkEntry(
        frame, textvariable=pass_var, show="*",
        width=240, height=35, font=ctk.CTkFont(size=14),
    )
    pass_entry.pack(side="left", padx=5)
    pass_entry.focus()

    # Show password toggle
    show_var = ctk.BooleanVar(value=False)

    def toggle_show():
        if show_var.get():
            pass_entry.configure(show="")
        else:
            pass_entry.configure(show="*")

    show_cb = ctk.CTkCheckBox(
        login_window, text="显示密码",
        variable=show_var, command=toggle_show,
    )
    show_cb.pack(pady=(10, 0))

    # Remember me checkbox
    saved_password = _load_remember()
    remember_var = ctk.BooleanVar(value=bool(saved_password))
    remember_cb = ctk.CTkCheckBox(
        login_window, text="记住密码",
        variable=remember_var,
    )
    remember_cb.pack(pady=5)

    # Status label
    status_var = ctk.StringVar(value="")
    status_lbl = ctk.CTkLabel(
        login_window, textvariable=status_var,
        text_color="#e74c3c",
    )
    status_lbl.pack(pady=5)

    # Auto-login if password is saved
    if saved_password and store.has_data():
        login_window.destroy()
        store.unlock(saved_password)
        app = PasswordManagerApp()
        app.store = store
        app.entries = store.get_entries()
        app.filtered_entries = list(app.entries)
        app._build_categories()
        app._render_entries()
        app.run()
        return

    def enter_password():
        password = pass_var.get()
        if not password:
            status_var.set("请输入主密码")
            return

        if store.has_data():
            if store.unlock(password):
                if remember_var.get():
                    _save_remember(password)
                else:
                    _delete_remember()
                login_window.destroy()
                app = PasswordManagerApp()
                app.store = store
                app.entries = store.get_entries()
                app.filtered_entries = list(app.entries)
                app._build_categories()
                app._render_entries()
                app.run()
            else:
                status_var.set("密码错误，请重试")
                pass_var.set("")
        else:
            # First time - create new
            store.create_new(password)
            if remember_var.get():
                _save_remember(password)
            else:
                _delete_remember()
            login_window.destroy()
            app = PasswordManagerApp()
            app.store = store
            app.entries = store.get_entries()
            app.filtered_entries = list(app.entries)
            app._build_categories()
            app._render_entries()
            app.run()

    # Enter key binding
    pass_entry.bind("<Return>", lambda e: enter_password())

    # Login button
    is_new = not store.has_data()
    btn_text = "创建主密码" if is_new else "解锁"
    if not is_new:
        subtitle.configure(text="输入主密码以解锁密码库")

    # Clear remember button (only if saved)
    if saved_password and not is_new:
        def clear_saved():
            _delete_remember()
            remember_var.set(False)
            status_var.set("已清除记忆，请重新登录")
            clear_btn.configure(state="disabled")
            pass_entry.focus()

        clear_btn = ctk.CTkButton(
            login_window, text="清除记忆",
            command=clear_saved,
            width=100, height=30,
            fg_color="#c0392b", hover_color="#e74c3c",
            font=ctk.CTkFont(size=12),
        )
        clear_btn.pack(pady=(5, 0))

    login_btn = ctk.CTkButton(
        login_window, text=btn_text,
        command=enter_password,
        width=200, height=40,
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    login_btn.pack(pady=15)

    # Warning for new users
    if not store.has_data():
        warn_lbl = ctk.CTkLabel(
            login_window,
            text="首次使用：此密码将用于加密您的数据\n请牢记此密码，丢失后将无法恢复！",
            text_color="#f39c12",
            font=ctk.CTkFont(size=12),
        )
        warn_lbl.pack(pady=10)

    login_window.mainloop()


def main():
    show_login_window()


if __name__ == "__main__":
    main()
