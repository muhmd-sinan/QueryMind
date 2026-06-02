import mysql.connector
from pathlib import Path


def db_schema(conn):
    """
    Returns (schema_text, schema_tables).
    schema_text  — plain string written to schema.txt, used in LLM prompts.
    schema_tables — {table: [{"name", "type", "tag"}, ...]} used by ui.py for rendering.
    """
    cursor = conn.cursor()
    schema_text   = ""
    schema_tables = {}

    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        schema_text += f"Table: {table}\n"
        schema_text += "  Columns: "

        cursor.execute(f"""
           SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
           FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
           WHERE TABLE_SCHEMA = DATABASE()
           AND TABLE_NAME = '{table}'
           AND REFERENCED_TABLE_NAME IS NOT NULL
       """)
        fk_map = {}
        for fk in cursor.fetchall():
            fk_map[fk[0]] = f"{fk[1]}.{fk[2]}"

        cursor.execute(f"DESCRIBE `{table}`")
        column_entries = []
        table_cols     = []
        for col in cursor.fetchall():
            name     = col[0]
            datatype = col[1]

            tag = ""
            if col[3] == "PRI":
                tag = "[PK]"
            elif name in fk_map:
                tag = f"[FK = {fk_map[name]}]"

            column_entries.append(f"{name} ({datatype}){' ' + tag if tag else ''}")
            table_cols.append({"name": name, "type": datatype, "tag": tag})

        schema_text += ", ".join(column_entries) + "\n"
        schema_tables[table] = table_cols

    Path("schema.txt").write_text(schema_text, encoding="utf-8")
    print("Schema refreshed and saved to schema.txt")

    cursor.close()
    return schema_text, schema_tables


def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)

    # Consume the active result set before issuing any other query on this connection.
    if cursor.with_rows:
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
    else:
        columns = []
        results = []

    conn.commit()
    schema_text, schema_tables = db_schema(conn)

    if cursor.with_rows:
        message = f"Query executed successfully. {len(results)} row(s) returned."
        row_count = len(results)
    else:
        message = f"Query executed successfully. {cursor.rowcount} row(s) affected."
        row_count = cursor.rowcount

    cursor.close()
    return {
        "query": query,
        "with_rows": bool(columns),
        "columns": columns,
        "rows": results,
        "row_count": row_count,
        "message": message,
        "schema_text": schema_text,
        "schema_tables": schema_tables,
    }