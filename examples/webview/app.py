from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import sqlite3


class TableData(BaseModel):
    columns: list[str]
    rows: list[tuple]


def read_tables_name(db_path: str) -> list[tuple[str]]:
    with sqlite3.connect(db_path) as db:
        cur = db.cursor()
        cur.execute("select type, name from sqlite_master where type in ('table', 'view');")
        return cur.fetchall()


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
available_databases: list[str] = os.listdir(f"{ROOT_DIR}/db")
available_tables: dict[str, list[tuple[str]]] = {
    name: read_tables_name(f"{ROOT_DIR}/db/{name}")
    for name in available_databases
}
templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def page_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "databases": available_databases,
            "db_to_tables": available_tables
        }
    )


@app.get("/api/read_table_content")
async def read_table_content(database: str, table: str) -> TableData:
    if database not in available_databases or not any([table == name for _, name in available_tables[database]]):
        raise FileNotFoundError

    with sqlite3.connect(f"{ROOT_DIR}/db/{database}") as db:
        cur = db.cursor()

        cur.execute(f"PRAGMA table_info('{table}')")
        col_names = [row[1] for row in cur.fetchall()]

        cur.execute(f"select * from '{table}'")
        data = cur.fetchall()
    return TableData(columns=col_names, rows=data)

