import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response
from brotli_asgi import BrotliMiddleware
from functools import lru_cache
from pydantic import BaseModel
from circleutils import Collection
from datetime import datetime
from operator import itemgetter
import os
import sqlite3
import argparse


class TableData(BaseModel):
    columns: list[str]
    rows: list[tuple]


class CollectionGenerationRequest(BaseModel):
    database: str
    ids: list[int]


def read_tables_name(db_path: str) -> list[tuple[str]]:
    with sqlite3.connect(db_path) as db:
        cur = db.cursor()
        cur.execute("select type, name from sqlite_master where type in ('table', 'view');")
        return sorted(cur.fetchall(), key=itemgetter(1))


@lru_cache(maxsize=4)
def read_table_content(database: str, table: str) -> TableData:
    with sqlite3.connect(f"{ROOT_DIR}/db/{database}") as db:
        cur = db.cursor()

        cur.execute(f"PRAGMA table_info('{table}')")
        col_names = [row[1] for row in cur.fetchall()]

        cur.execute(f"select * from '{table}'")
        data = cur.fetchall()
    return TableData(columns=col_names, rows=data)


def enable_compression(app: FastAPI):
    app.add_middleware(
        BrotliMiddleware,
        quality=4,
        mode="text",
        lgwin=22,
        lgblock=0,
        minimum_size=400,
        gzip_fallback=True
    )


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
available_databases: list[str] = os.listdir(f"{ROOT_DIR}/db")
available_tables: dict[str, list[tuple[str]]] = {
    name: read_tables_name(f"{ROOT_DIR}/db/{name}")
    for name in available_databases
}
templates = Jinja2Templates(directory="templates")

app = FastAPI(docs_url=None, redoc_url=None)
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


@app.get("/api/table/read")
async def handle_read_table_content(database: str, table: str) -> TableData:
    if database not in available_databases or not any([table == name for _, name in available_tables[database]]):
        raise FileNotFoundError

    return read_table_content(database, table)


@app.post("/api/collection/create")
async def handle_create_collection(post_data: CollectionGenerationRequest) -> Response:
    if post_data.database not in available_databases:
        raise FileNotFoundError
    
    with sqlite3.connect(f"{ROOT_DIR}/db/{post_data.database}") as db:
        placeholder = ",".join(["?"]*len(post_data.ids))
        cur = db.cursor()
        cur.execute(f"select checksum from beatmap where id in ({placeholder})", post_data.ids)
        hashes = [x[0] for x in cur.fetchall()]
     
    date_int = int(datetime.now().strftime("%Y%m%d"))
    content = {"export": hashes}
    
    collection = Collection(date=date_int, content=content)
    return Response(content=collection.to_bytes(), media_type="binary/octet-stream")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CircleDB webview")
    parser.add_argument('--add-compression', help="Add brotli compression", action="store_true")
    args = parser.parse_args()
    
    if args.add_compression:
        enable_compression(app)
    
    uvicorn.run(app, port=60727)
