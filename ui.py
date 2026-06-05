"""
ui.py — Streamlit frontend for the Text-to-SQL app.

Drop this file next to your existing app.py and db.py, then run:
    streamlit run ui.py

Pages
-----
1. Database Connect  — configure & test MySQL connection, view live schema
2. API Connect       — enter Groq API key & choose model
3. Query             — natural-language → SQL → executed results
"""

import streamlit as st
import pandas as pd
import mysql.connector
from groq import Groq

import db
import app as backend

# ─────────────────────────────────────────────────────────────────────────────
# Page config  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskSQL · Natural Language to SQL",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
code, pre, .stCode * { font-family: 'IBM Plex Mono', monospace !important; }

[data-testid="stSidebar"] { background:#080c10 !important; border-right:1px solid #1c2330; }
[data-testid="stSidebar"] * { color:#c9d1d9 !important; }
[data-testid="stSidebar"] .stButton>button {
    background:transparent; border:1px solid #21262d; color:#c9d1d9 !important;
    border-radius:6px; font-family:'Space Grotesk',sans-serif;
    font-size:0.85rem; text-align:left; transition:all .15s;
}
[data-testid="stSidebar"] .stButton>button:hover { background:#161b22; border-color:#30363d; }

.main .block-container { padding-top:2rem; max-width:1100px; }

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background:#0d1117 !important; border:1px solid #21262d !important;
    color:#e6edf3 !important; border-radius:8px !important;
    font-family:'Space Grotesk',sans-serif !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color:#58a6ff !important; box-shadow:0 0 0 3px rgba(88,166,255,.15) !important;
}

.stButton>button[kind="primary"] {
    background:#58a6ff !important; color:#0d1117 !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
    font-family:'Space Grotesk',sans-serif !important; transition:all .15s;
}
.stButton>button[kind="primary"]:hover { background:#388bfd !important; }

.stButton>button[kind="secondary"] {
    background:transparent !important; color:#c9d1d9 !important;
    border:1px solid #21262d !important; border-radius:8px !important;
    font-family:'Space Grotesk',sans-serif !important; transition:all .15s;
}
.stButton>button[kind="secondary"]:hover { border-color:#444c56 !important; background:#161b22 !important; }

[data-testid="stMetric"] { background:#0d1117 !important; border:1px solid #21262d !important; border-radius:10px !important; padding:.8rem !important; }
[data-testid="stMetricValue"] { font-family:'IBM Plex Mono',monospace !important; }

#MainMenu, footer, header { visibility:hidden; }
hr { border-color:#21262d; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session-state defaults  (pre-filled from your db.py values)
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "page":           "db_connect",
    # DB — mirrors the hardcoded values in db.py
    "db_host":        "localhost",
    "db_port":        "3306",
    "db_user":        "root",
    "db_password":    "1234",
    "db_name":        "company_db",
    "db_connected":   False,
    "conn":           None,
    "schema_text":    "",      # same text that db_schema() writes to schema.txt
    "schema_tables":  {},      # {table: [{"name","type","tag"}, ...]}
    # API — mirrors the hardcoded values in app.py
    "api_key":        "",
    "model":          "openai/gpt-oss-120b",
    "api_connected":  False,
    # Query history
    "query_history":  [],      # list of result dicts
    "sel_history":    None,    # which entry is being viewed
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Core helpers removed — logic lives in db.py (db_schema, execute_query)
# and app.py (create_query). Imported above as `db` and `backend`.


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def _sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='padding:1rem 0 .5rem;'>
          <span style='font-size:1.4rem;font-weight:700;letter-spacing:-.03em;color:#58a6ff;'>AskSQL</span><br/>
          <span style='font-size:.7rem;color:#444c56;letter-spacing:.1em;text-transform:uppercase;'>Text · to · SQL</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        # ── navigation ────────────────────────────────────────────────────────
        st.markdown("<p style='font-size:.7rem;color:#444c56;letter-spacing:.1em;text-transform:uppercase;'>Navigation</p>", unsafe_allow_html=True)

        nav_items = [
            ("db_connect",  "⬡  Database Connect"),
            ("api_connect", "◈  API / Model"),
            ("query",       "⟡  Query Interface"),
        ]
        for key, label in nav_items:
            locked = (key == "query" and not (
                st.session_state["db_connected"] and st.session_state["api_connected"]
            ))
            is_active = st.session_state["page"] == key
            btn_label = label + ("  🔒" if locked else "")
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if is_active else "secondary",
                         disabled=locked):
                st.session_state["page"]        = key
                st.session_state["sel_history"] = None
                st.rerun()

        st.divider()

        # ── status dots ───────────────────────────────────────────────────────
        st.markdown("<p style='font-size:.7rem;color:#444c56;letter-spacing:.1em;text-transform:uppercase;'>Status</p>", unsafe_allow_html=True)
        db_dot  = "#3fb950" if st.session_state["db_connected"]  else "#f85149"
        api_dot = "#3fb950" if st.session_state["api_connected"] else "#f85149"
        db_lbl  = f"{st.session_state['db_name']}@{st.session_state['db_host']}" if st.session_state["db_connected"] else "Not connected"
        api_lbl = st.session_state["model"] if st.session_state["api_connected"] else "Not configured"
        st.markdown(f"""
        <div style='font-size:.8rem;line-height:2.4;'>
          <span style='display:inline-block;width:8px;height:8px;border-radius:50%;background:{db_dot};margin-right:7px;'></span>DB
          <span style='color:#444c56;font-size:.73rem;margin-left:4px;'>{db_lbl}</span><br/>
          <span style='display:inline-block;width:8px;height:8px;border-radius:50%;background:{api_dot};margin-right:7px;'></span>API
          <span style='color:#444c56;font-size:.73rem;margin-left:4px;'>{api_lbl}</span>
        </div>
        """, unsafe_allow_html=True)

        # ── query history ─────────────────────────────────────────────────────
        history = st.session_state["query_history"]
        if history:
            st.divider()
            st.markdown("<p style='font-size:.7rem;color:#444c56;letter-spacing:.1em;text-transform:uppercase;'>Query History</p>", unsafe_allow_html=True)

            for i, entry in enumerate(reversed(history[-20:])):
                real_idx = len(history) - 1 - i
                icon     = "✓" if not entry.get("error") and not entry.get("clarify") else ("⚠" if entry.get("clarify") else "✗")
                short_q  = entry["question"][:32] + ("…" if len(entry["question"]) > 32 else "")
                if st.button(f"{icon}  {short_q}", key=f"hist_{real_idx}", use_container_width=True):
                    st.session_state["page"]        = "query"
                    st.session_state["sel_history"] = real_idx
                    st.rerun()

            if st.button("🗑  Clear history", use_container_width=True):
                st.session_state["query_history"] = []
                st.session_state["sel_history"]   = None
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Page 1 — Database Connect
# ─────────────────────────────────────────────────────────────────────────────

def _page_db_connect():
    st.markdown("<h1 style='font-size:1.9rem;font-weight:700;letter-spacing:-.04em;margin-bottom:.2rem;'>Database Connection</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;margin-bottom:1.5rem;'>Fields are pre-filled from your <code>db.py</code>. Edit and hit Connect — values persist for the session.</p>", unsafe_allow_html=True)

    if st.session_state["db_connected"]:
        st.success(
            f"Connected to **{st.session_state['db_name']}** "
            f"on `{st.session_state['db_host']}:{st.session_state['db_port']}`",
            icon="✅",
        )

    with st.form("db_form", border=True):
        st.markdown("##### Connection Details")

        c1, c2 = st.columns([3, 1])
        host = c1.text_input("Host", value=st.session_state["db_host"], placeholder="localhost")
        port = c2.text_input("Port", value=st.session_state["db_port"], placeholder="3306")

        c3, c4 = st.columns(2)
        user     = c3.text_input("Username", value=st.session_state["db_user"],     placeholder="root")
        password = c4.text_input("Password", value=st.session_state["db_password"], placeholder="••••••••", type="password")

        db_name = st.text_input("Database Name", value=st.session_state["db_name"], placeholder="company_db")

        cb1, cb2, _ = st.columns([1, 1, 4])
        connect_btn    = cb1.form_submit_button("Connect",    type="primary", use_container_width=True)
        disconnect_btn = cb2.form_submit_button("Disconnect", use_container_width=True)

    # ── connect ───────────────────────────────────────────────────────────────
    if connect_btn:
        st.session_state.update({
            "db_host": host, "db_port": port,
            "db_user": user, "db_password": password, "db_name": db_name,
        })
        with st.spinner("Connecting to MySQL…"):
            try:
                new_conn = mysql.connector.connect(
                    host=host, port=int(port),
                    user=user, password=password, database=db_name,
                )
                schema_text, schema_tables = db.db_schema(new_conn)
                st.session_state.update({
                    "conn": new_conn, "db_connected": True,
                    "schema_text": schema_text, "schema_tables": schema_tables,
                })
                st.success(f"Connected! {len(schema_tables)} table(s) found.", icon="✅")
                st.rerun()
            except mysql.connector.Error as e:
                st.session_state["db_connected"] = False
                st.error(f"Connection failed: {e}", icon="❌")

    # ── disconnect ────────────────────────────────────────────────────────────
    if disconnect_btn and st.session_state["db_connected"]:
        try:
            st.session_state["conn"].close()
        except Exception:
            pass
        st.session_state.update({
            "conn": None, "db_connected": False,
            "schema_text": "", "schema_tables": {},
        })
        st.info("Disconnected.", icon="ℹ️")
        st.rerun()

    # ── live schema cards (shown only when connected) ─────────────────────────
    if st.session_state["db_connected"] and st.session_state["schema_tables"]:
        st.divider()

        hc1, hc2 = st.columns([6, 1])
        hc1.markdown("#### Schema Overview")
        if hc2.button("↻ Refresh", type="secondary"):
            with st.spinner("Refreshing…"):
                schema_text, schema_tables = db.db_schema(st.session_state["conn"])
                st.session_state.update({"schema_text": schema_text, "schema_tables": schema_tables})
                st.success("Schema refreshed and schema.txt updated.", icon="✅")
                st.rerun()

        tables = st.session_state["schema_tables"]
        cols   = st.columns(min(len(tables), 3))

        for i, (tbl, columns) in enumerate(tables.items()):
            with cols[i % 3]:
                rows_html = ""
                for col in columns:
                    if col["tag"] == "[PK]":
                        icon, color = "🔑", "#e3b341"
                    elif col["tag"].startswith("[FK"):
                        icon, color = "🔗", "#79c0ff"
                        fk_target   = col["tag"].replace("[FK = ", "").rstrip("]")
                    else:
                        icon, color = "·", "#8b949e"
                        fk_target   = None
                    rows_html += (
                        f"<div style='display:flex;align-items:center;gap:5px;"
                        f"padding:3px 0;border-bottom:1px solid #161b22;'>"
                        f"<span style='font-size:.7rem;'>{icon}</span>"
                        f"<span style='flex:1;font-size:.78rem;color:#e6edf3;'>{col['name']}</span>"
                        f"<span style='color:#444c56;font-size:.68rem;font-family:\"IBM Plex Mono\",monospace;'>"
                        f"{col['type'].split('(')[0]}</span>"
                        f"</div>"
                    )
                    if col["tag"].startswith("[FK"):
                        rows_html += (
                            f"<div style='padding-left:1.1rem;color:#444c56;font-size:.68rem;"
                            f"font-family:\"IBM Plex Mono\",monospace;'>→ {fk_target}</div>"
                        )
                st.markdown(f"""
                <div style='background:#0d1117;border:1px solid #21262d;border-radius:10px;
                            overflow:hidden;margin-bottom:.75rem;'>
                  <div style='background:#161b22;padding:.5rem .9rem;font-size:.8rem;font-weight:600;
                              color:#58a6ff;text-transform:uppercase;letter-spacing:.05em;'>{tbl}</div>
                  <div style='padding:.5rem .9rem;'>{rows_html}</div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page 2 — API / Model Config
# ─────────────────────────────────────────────────────────────────────────────

def _page_api_connect():
    st.markdown("<h1 style='font-size:1.9rem;font-weight:700;letter-spacing:-.04em;margin-bottom:.2rem;'>API Configuration</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;margin-bottom:1.5rem;'>Enter your Groq API key and choose the model to use for SQL generation.</p>", unsafe_allow_html=True)

    if st.session_state["api_connected"]:
        st.success(f"API ready — model: `{st.session_state['model']}`", icon="✅")

    with st.form("api_form", border=True):
        st.markdown("##### Groq API Settings")

        api_key = st.text_input(
            "Groq API Key",
            value=st.session_state["api_key"],
            type="password",
            placeholder="gsk_••••••••••••••••••••••••••••••••",
            help="Get a free key at console.groq.com — no credit card required.",
        )
        model = st.text_input(
            "Model",
            value=st.session_state["model"],
            placeholder="openai/gpt-oss-120b",
        )
        st.markdown("""
        <p style='font-size:.8rem;color:#8b949e;margin-top:.3rem;'>
          Recommended free models: <code>openai/gpt-oss-120b</code> &nbsp;·&nbsp;
          <code>llama3-70b-8192</code> &nbsp;·&nbsp; <code>mixtral-8x7b-32768</code>
        </p>
        """, unsafe_allow_html=True)

        cb1, cb2, _ = st.columns([1, 1, 4])
        save_btn  = cb1.form_submit_button("Save & Connect", type="primary", use_container_width=True)
        clear_btn = cb2.form_submit_button("Clear",                          use_container_width=True)

    if save_btn:
        if not api_key.strip():
            st.error("API key cannot be empty.", icon="❌")
        else:
            with st.spinner("Verifying key…"):
                try:
                    Groq(api_key=api_key.strip()).models.list()  # lightweight probe
                    st.session_state.update({
                        "api_key":       api_key.strip(),
                        "model":         model.strip() or "openai/gpt-oss-120b",
                        "api_connected": True,
                    })
                    st.success("API key verified and saved.", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.session_state["api_connected"] = False
                    st.error(f"Verification failed: {e}", icon="❌")

    if clear_btn:
        st.session_state.update({"api_key": "", "api_connected": False})
        st.info("API key cleared.", icon="ℹ️")
        st.rerun()

    st.markdown("""
    <div style='background:#0d1117;border:1px solid #21262d;border-radius:10px;
                padding:1.25rem;margin-top:1.5rem;max-width:520px;'>
      <div style='font-size:.75rem;font-weight:600;color:#58a6ff;text-transform:uppercase;
                  letter-spacing:.06em;margin-bottom:.6rem;'>How it works</div>
      <div style='font-size:.85rem;color:#8b949e;line-height:1.8;'>
        Your question + live schema → Groq LLM → raw SQL → executed on your MySQL DB → results shown here.<br/><br/>
        The key lives only in your browser session and is sent exclusively to the Groq API.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Page 3 — Query Interface
# ─────────────────────────────────────────────────────────────────────────────

def _schema_diagram():
    """Compact schema cards shown at the top of the query page."""
    tables = st.session_state["schema_tables"]
    if not tables:
        return
    with st.expander("📐  Schema Diagram", expanded=True):
        ncols = min(len(tables), 4)
        cols  = st.columns(ncols)
        for i, (tbl, columns) in enumerate(tables.items()):
            with cols[i % ncols]:
                rows_html = ""
                for col in columns:
                    if col["tag"] == "[PK]":
                        badge = "<span style='background:#2d333b;color:#e3b341;font-size:.62rem;padding:1px 5px;border-radius:4px;margin-left:4px;'>PK</span>"
                    elif col["tag"].startswith("[FK"):
                        badge = "<span style='background:#1f3145;color:#79c0ff;font-size:.62rem;padding:1px 5px;border-radius:4px;margin-left:4px;'>FK</span>"
                    else:
                        badge = ""
                    rows_html += (
                        f"<div style='display:flex;align-items:center;padding:3px 0;"
                        f"border-bottom:1px solid #161b22;'>"
                        f"<span style='flex:1;font-size:.77rem;color:#e6edf3;'>{col['name']}</span>"
                        f"<span style='color:#444c56;font-size:.67rem;font-family:\"IBM Plex Mono\",monospace;'>"
                        f"{col['type'].split('(')[0]}</span>{badge}"
                        f"</div>"
                    )
                st.markdown(f"""
                <div style='background:#0d1117;border:1px solid #21262d;border-radius:10px;
                            overflow:hidden;margin-bottom:.5rem;'>
                  <div style='background:#161b22;padding:.45rem .9rem;font-size:.77rem;font-weight:600;
                              color:#58a6ff;text-transform:uppercase;letter-spacing:.05em;'>{tbl}</div>
                  <div style='padding:.5rem .9rem;'>{rows_html}</div>
                </div>
                """, unsafe_allow_html=True)


def _render_result(entry):
    """Render the SQL + execution result for one history entry."""
    st.markdown(
        f"<p style='color:#8b949e;font-size:.85rem;margin-bottom:.5rem;'>❝ {entry['question']}</p>",
        unsafe_allow_html=True,
    )

    if entry.get("error"):
        st.error(f"**Error:** {entry['error']}", icon="❌")
        if entry.get("sql"):
            st.code(entry["sql"], language="sql")
        return

    if entry.get("clarify"):
        st.warning(f"**Clarification needed:** {entry['clarify']}", icon="🤔")
        return

    st.code(entry["sql"], language="sql")

    result = entry.get("result")
    if not result:
        return

    st.caption(result["message"])

    if result["with_rows"] and result["rows"]:
        df = pd.DataFrame(result["rows"], columns=result["columns"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # one-click CSV export
        st.download_button(
            label="⬇  Export CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="query_result.csv",
            mime="text/csv",
        )
    else:
        st.info(result["message"], icon="ℹ️")


def _page_query():
    db_name = st.session_state["db_name"]
    model   = st.session_state["model"]
    st.markdown("<h1 style='font-size:1.9rem;font-weight:700;letter-spacing:-.04em;margin-bottom:.2rem;'>Query Interface</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#8b949e;margin-bottom:1rem;'>DB: <code>{db_name}</code> &nbsp;·&nbsp; Model: <code>{model}</code></p>",
        unsafe_allow_html=True,
    )

    # schema diagram
    _schema_diagram()
    st.divider()

    # ── input form ────────────────────────────────────────────────────────────
    st.markdown("#### Ask a Question")
    with st.form("query_form", clear_on_submit=True):
        question = st.text_area(
            "question",
            placeholder="e.g.  Show all employees in Engineering sorted by salary descending",
            height=90,
            label_visibility="collapsed",
        )
        c1, c2, _ = st.columns([1, 1, 5])
        run_btn   = c1.form_submit_button("▶  Run Query",   type="primary", use_container_width=True)
        clear_btn = c2.form_submit_button("Clear History",                  use_container_width=True)

    if clear_btn:
        st.session_state["query_history"] = []
        st.session_state["sel_history"]   = None
        st.rerun()

    # ── process new query ─────────────────────────────────────────────────────
    if run_btn and question.strip():
        entry = {
            "question": question.strip(),
            "sql":      None,
            "result":   None,
            "clarify":  None,
            "error":    None,
        }

        with st.spinner("Asking the LLM…"):
            try:
                sql = backend.create_query(question.strip(), api_key=st.session_state["api_key"])
            except Exception as e:
                entry["error"] = f"LLM error: {e}"
                st.session_state["query_history"].append(entry)
                st.session_state["sel_history"] = len(st.session_state["query_history"]) - 1
                st.rerun()

        if sql.upper().startswith("CLARIFY"):
            entry["clarify"] = sql.split(":", 1)[1].strip().rstrip(";")
        else:
            entry["sql"] = sql
            with st.spinner("Executing SQL…"):
                try:
                    result = db.execute_query(st.session_state["conn"], sql)
                    # db.execute_query refreshes schema internally; sync session state
                    st.session_state["schema_text"]   = result["schema_text"]
                    st.session_state["schema_tables"] = result["schema_tables"]
                    entry["result"] = result
                except Exception as e:
                    entry["error"] = str(e)

        st.session_state["query_history"].append(entry)
        st.session_state["sel_history"] = len(st.session_state["query_history"]) - 1
        st.rerun()

    # ── display result ────────────────────────────────────────────────────────
    history = st.session_state["query_history"]
    sel     = st.session_state.get("sel_history")

    if history:
        st.divider()

        target = history[sel] if (sel is not None and 0 <= sel < len(history)) else history[-1]

        hc1, hc2 = st.columns([6, 1])
        hc1.markdown("#### Result")
        if sel is not None and sel < len(history) - 1:
            if hc2.button("Latest ↓", use_container_width=True):
                st.session_state["sel_history"] = len(history) - 1
                st.rerun()

        _render_result(target)

        # collapsible full history table
        if len(history) > 1:
            with st.expander(f"📋  All queries ({len(history)})", expanded=False):
                for i, e in enumerate(reversed(history)):
                    real_i = len(history) - 1 - i
                    icon   = "✓" if not e.get("error") and not e.get("clarify") else ("⚠" if e.get("clarify") else "✗")
                    rows   = e["result"]["row_count"] if e.get("result") else "—"
                    a, b, c = st.columns([6, 1, 1])
                    a.markdown(f"`{icon}` {e['question'][:72]}")
                    b.caption(f"{rows} rows")
                    if c.button("View", key=f"view_{real_i}", use_container_width=True):
                        st.session_state["sel_history"] = real_i
                        st.rerun()
    else:
        st.markdown("""
        <div style='text-align:center;padding:3rem 0;color:#444c56;'>
          <div style='font-size:2.5rem;margin-bottom:.5rem;'>⟡</div>
          <div>Type your first question above and hit Run Query</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

_sidebar()

_PAGES = {
    "db_connect":  _page_db_connect,
    "api_connect": _page_api_connect,
    "query":       _page_query,
}
_PAGES[st.session_state["page"]]()