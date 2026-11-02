import html
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------- setup
ROOT = Path(__file__).parent / "workspace"
ROOT.mkdir(exist_ok=True)
ROOT = ROOT.resolve()

st.set_page_config(page_title="Workspace files", page_icon="🗂️", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap');

:root {
  --ink: #16303A;
  --muted: #5F7783;
  --paper: #EDF0F2;
  --card: #FFFFFF;
  --line: #D5DCE1;
  --brand: #1E4D5C;
  --brand-dark: #153844;
  --amber: #E8A33D;
}

.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp li, .stApp h1, .stApp h2, .stApp h3 {
  font-family: 'Figtree', system-ui, sans-serif;
}
.stApp { background: var(--paper); color: var(--ink); }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }

/* page header */
.top { display: flex; justify-content: space-between; align-items: flex-end;
       margin-bottom: 1.6rem; gap: 1rem; flex-wrap: wrap; }
.top h1 { font-size: 1.85rem; font-weight: 700; letter-spacing: -0.015em;
          margin: 0; padding: 0; color: var(--ink); }
.top .path { color: var(--muted); font-size: .88rem; margin-top: .3rem; word-break: break-all; }
.counts { display: flex; gap: 1.6rem; font-size: .95rem; color: var(--muted); }
.counts b { color: var(--ink); font-weight: 700; font-size: 1.15rem; margin-right: .25rem; }

/* explorer */
.panel { background: var(--card); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.panel-head { padding: .85rem 1.1rem; border-bottom: 1px solid var(--line);
              font-weight: 600; font-size: .95rem; }
.row { display: flex; align-items: center; gap: .65rem; padding: .55rem 1.1rem;
       border-bottom: 1px solid #EEF1F3; font-size: .93rem; }
.row:last-child { border-bottom: none; }
.row:hover { background: #F6F8F9; }
.row svg { flex: none; }
.row .name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row .meta { color: var(--muted); font-size: .82rem; text-align: right; white-space: nowrap; }
.row .when { color: #8CA0AA; font-size: .8rem; width: 6.5rem; text-align: right; white-space: nowrap; }
.empty { padding: 2.6rem 1.4rem; text-align: center; color: var(--muted); font-size: .95rem; line-height: 1.5; }
.empty b { color: var(--ink); display: block; margin-bottom: .2rem; font-size: 1rem; }

/* widgets */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 7px; font-weight: 600; border: 1px solid var(--line);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--brand); border-color: var(--brand); color: #fff;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
  background: var(--brand-dark); border-color: var(--brand-dark); color: #fff;
}
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
  border-radius: 7px; background: #fff; border-color: var(--line);
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--brand); box-shadow: 0 0 0 1px var(--brand); }
[data-testid="stForm"] { border: none; padding: 0; background: transparent; }
.stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { padding: .5rem 0; font-weight: 600; color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--ink); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--amber); height: 3px; }
.stRadio [role="radiogroup"] { gap: .4rem 1.2rem; }
</style>
""",
    unsafe_allow_html=True,
)

FOLDER_ICON = (
    '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M2 6a2 2 0 0 1 2-2h5l2 2h9a2 2 0 0 1 '
    '2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2z" fill="#E8A33D"/></svg>'
)
FILE_ICON = (
    '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 2h8l6 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1'
    '-2-2V4a2 2 0 0 1 2-2z" fill="#9DB4BF"/><path d="M14 2v6h6z" fill="#6F8D9A"/></svg>'
)


# ---------------------------------------------------------------- helpers
def safe_path(name: str):
    """Return a path inside ROOT, or None if the name is empty or escapes ROOT."""
    name = name.strip().strip("/\\")
    if not name:
        return None
    p = (ROOT / name).resolve()
    if p == ROOT or ROOT not in p.parents:
        return None
    return p


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def list_folders():
    return sorted(rel(p) for p in ROOT.rglob("*") if p.is_dir())


def list_files():
    return sorted(rel(p) for p in ROOT.rglob("*") if p.is_file())


def read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def flash(message: str):
    st.session_state["flash"] = message
    st.rerun()


def pick(label, options, key):
    return st.selectbox(label, options, key=key)


if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"))

# ---------------------------------------------------------------- header
folders, files = list_folders(), list_files()
st.markdown(
    f"""<div class="top"><div><h1>Workspace files</h1>
<div class="path">{html.escape(str(ROOT))}</div></div>
<div class="counts"><span><b>{len(folders)}</b>folders</span><span><b>{len(files)}</b>files</span></div></div>""",
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 1], gap="large")

# ---------------------------------------------------------------- explorer
with left:
    rows = []
    for p in sorted(ROOT.rglob("*"), key=lambda x: x.relative_to(ROOT).parts):
        depth = len(p.relative_to(ROOT).parts) - 1
        st_ = p.stat()
        when = datetime.fromtimestamp(st_.st_mtime).strftime("%d %b, %H:%M")
        if p.is_dir():
            icon, meta = FOLDER_ICON, f"{sum(1 for _ in p.iterdir())} items"
        else:
            icon, meta = FILE_ICON, human_size(st_.st_size)
        rows.append(
            f'<div class="row" style="padding-left:{1.1 + depth * 1.4}rem">{icon}'
            f'<span class="name">{html.escape(p.name)}</span>'
            f'<span class="meta">{meta}</span><span class="when">{when}</span></div>'
        )
    body = "".join(rows) or (
        '<div class="empty"><b>Nothing here yet</b>'
        "Create a folder or a file from the panel on the right.</div>"
    )
    st.markdown(f'<div class="panel"><div class="panel-head">Contents</div>{body}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- actions
with right:
    tab_folder, tab_file = st.tabs(["Folders", "Files"])

    # ----- folders
    with tab_folder:
        action = st.radio("Folder action", ["Create", "Rename", "Delete"], horizontal=True,
                          key="folder_action", label_visibility="collapsed")

        if action == "Create":
            with st.form("folder_create", clear_on_submit=True):
                name = st.text_input("Folder name", placeholder="projects/2026")
                ok = st.form_submit_button("Create folder", type="primary")
            if ok:
                p = safe_path(name)
                if p is None:
                    st.error("Enter a folder name. It has to stay inside the workspace.")
                elif p.exists():
                    st.error(f"“{name}” already exists. Choose a different name.")
                else:
                    p.mkdir(parents=True)
                    flash(f"Created folder {rel(p)}")

        elif action == "Rename":
            if not folders:
                st.info("No folders to rename yet.")
            else:
                sel = pick("Folder", folders, "folder_rename_sel")
                with st.form("folder_rename"):
                    new = st.text_input("New name", value=sel)
                    ok = st.form_submit_button("Rename folder", type="primary")
                if ok:
                    target = safe_path(new)
                    if target is None:
                        st.error("Enter a valid new name.")
                    elif target.exists():
                        st.error(f"“{new}” already exists.")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        (ROOT / sel).rename(target)
                        flash(f"Renamed to {rel(target)}")

        else:
            if not folders:
                st.info("No folders to delete.")
            else:
                sel = pick("Folder", folders, "folder_delete_sel")
                count = sum(1 for _ in (ROOT / sel).rglob("*"))
                st.caption(f"Contains {count} item(s). Deleting is permanent.")
                sure = st.checkbox("Delete this folder and everything inside it", key="folder_confirm")
                if st.button("Delete folder", disabled=not sure, key="folder_delete_btn"):
                    try:
                        shutil.rmtree(ROOT / sel)
                        st.session_state.pop("folder_confirm", None)
                        flash(f"Deleted folder {sel}")
                    except PermissionError:
                        st.error("Permission denied. Close the folder in other programs and try again.")

    # ----- files
    with tab_file:
        action = st.radio("File action", ["Create", "Read", "Edit", "Delete"], horizontal=True,
                          key="file_action", label_visibility="collapsed")

        if action == "Create":
            with st.form("file_create", clear_on_submit=True):
                name = st.text_input("File name", placeholder="notes.txt")
                data = st.text_area("Content", height=180)
                ok = st.form_submit_button("Create file", type="primary")
            if ok:
                p = safe_path(name)
                if p is None:
                    st.error("Enter a file name with an extension, like notes.txt.")
                elif p.exists():
                    st.error(f"“{name}” already exists. Choose a different name.")
                else:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(data, encoding="utf-8")
                    flash(f"Created file {rel(p)}")

        elif not files:
            st.info("No files yet. Create one first.")

        elif action == "Read":
            sel = pick("File", files, "file_read_sel")
            content = read_text(ROOT / sel)
            if content is None:
                st.error("This file isn't plain text, so it can't be shown here.")
            else:
                st.text_area("Content", value=content, height=260, disabled=True, key=f"view_{sel}")
                st.download_button("Download", data=content, file_name=Path(sel).name)

        elif action == "Edit":
            mode = st.radio("Edit mode", ["Rename", "Overwrite", "Append"], horizontal=True, key="file_edit_mode")
            sel = pick("File", files, "file_edit_sel")
            p = ROOT / sel

            if mode == "Rename":
                with st.form("file_rename"):
                    new = st.text_input("New name", value=sel)
                    ok = st.form_submit_button("Rename file", type="primary")
                if ok:
                    target = safe_path(new)
                    if target is None:
                        st.error("Enter a valid new name with an extension.")
                    elif target.exists():
                        st.error(f"“{new}” already exists.")
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        p.rename(target)
                        flash(f"Renamed to {rel(target)}")

            elif mode == "Overwrite":
                current = read_text(p)
                if current is None:
                    st.error("This file isn't plain text, so it can't be edited here.")
                else:
                    with st.form("file_overwrite"):
                        data = st.text_area("New content", value=current, height=220, key=f"ow_{sel}")
                        ok = st.form_submit_button("Save changes", type="primary")
                    if ok:
                        p.write_text(data, encoding="utf-8")
                        flash(f"Saved {sel}")

            else:
                with st.form("file_append", clear_on_submit=True):
                    data = st.text_area("Text to add at the end", height=140)
                    ok = st.form_submit_button("Add to file", type="primary")
                if ok:
                    if not data:
                        st.error("Write something to add first.")
                    else:
                        with open(p, "a", encoding="utf-8") as fs:
                            fs.write(data)
                        flash(f"Added text to {sel}")

        else:
            sel = pick("File", files, "file_delete_sel")
            st.caption(f"{human_size((ROOT / sel).stat().st_size)}. Deleting is permanent.")
            sure = st.checkbox("Delete this file", key="file_confirm")
            if st.button("Delete file", disabled=not sure, key="file_delete_btn"):
                (ROOT / sel).unlink()
                st.session_state.pop("file_confirm", None)
                flash(f"Deleted file {sel}")