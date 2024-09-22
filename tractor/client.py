# ping
# "Why did the database administrator buy a tractor? Because he needed to manage large fields!" - gpt o1

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional, Literal
from fasthtml.common import *

def quote(s: str): return f"'{s}'"

@dataclass
class DatabaseInfo: driver: Literal["SQLite"]; name:str; version:str; location:str

@dataclass
class DatabaseTable: name:str; number_of_rows:int

@dataclass
class DatabaseColumn: name:str; is_pk:bool

@dataclass
class DatabaseRow: table_name:str; id: any; columns: List[DatabaseColumn]; attributes: Dict[str, any]

@patch
def __ft__(self: DatabaseColumn): return Div(cls='hs-dropdown relative inline-flex w-full cursor-pointer')(Span(self.name, cls='px-5 py-2.5 text-start w-full flex items-center gap-x-1 text-sm font-normal text-stone-500 focus:outline-none focus:bg-stone-100 dark:text-neutral-500 dark:focus:bg-neutral-700'))

class DatabaseConnection:
    def get_database_info(): raise NotImplementedError
    def list_tables(self) -> List[DatabaseTable]: raise NotImplementedError
    def count_rows(self, table_name: str) -> int: raise NotImplementedError
    def list_rows(self, table_name: str, limit: int, offset: int) -> List[DatabaseRow]: raise NotImplementedError
    def get_row_by_id(self, table_name: str, id: any) -> Optional[DatabaseRow]: raise NotImplementedError

class TractorSQL3(DatabaseConnection):
    hide_tables: List[str]= ["sqlite_stat1"]
    def __init__(self, connection: sqlite3.Connection): self.connection = connection
    def get_columns(self, table_name: str) -> List[DatabaseColumn]: return [DatabaseColumn(name=c[1], is_pk=c[5] == 1) for c in self.connection.execute(f"PRAGMA table_info({table_name});").fetchall()]
    def get_database_info(self) -> DatabaseInfo:
        d = self.connection.execute("SELECT * FROM pragma_database_list;").fetchall()
        return DatabaseInfo(driver="SQLite", name=d[0][1], location=d[0][2], version=self.connection.execute("SELECT sqlite_version();").fetchone()[0])
    def list_tables(self) -> List[DatabaseTable]:
        return [DatabaseTable(name=t[0], number_of_rows=self.count_rows(t[0])) for t in self.connection.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name not IN ({','.join(map(lambda t: quote(t), self.hide_tables))}) ORDER BY name;").fetchall()]
    def count_rows(self, table_name: str) -> int: return self.connection.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
    def list_rows(self, table_name: str, limit: int, offset: int) -> List[DatabaseRow]:
        columns = self.get_columns(table_name)
        pk = next(c for c in columns if c.is_pk)
        # TODO: figure out how to handle cases where there is no primary key
        rows = self.connection.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset};").fetchall()
        def build_row(row):
            attributes={columns[i].name: row[i] for i in range(len(columns))}
            id = row[0] if pk is None else attributes[pk.name]
            return DatabaseRow(table_name=table_name, id=id, columns=columns, attributes=attributes)
        return [build_row(row) for row in rows]
    def get_row_by_id(self, table_name: str, id: any) -> Optional[DatabaseRow]:
        columns = self.get_columns(table_name)
        pk = next(c for c in columns if c.is_pk)
        # TODO: figure out how to handle cases where there is no primary key
        if pk is None: return None
        rows = self.connection.execute(f"SELECT * FROM {table_name} WHERE {pk.name} = {id};").fetchall()
        return DatabaseRow(table_name=table_name, id=rows[0][0], columns=columns, attributes={columns[i].name: rows[0][i] for i in range(len(columns))}) if len(rows) != 0 else None

class Tractor:
    @staticmethod
    def from_sqlite3(connection: sqlite3.Connection) -> DatabaseConnection: return TractorSQL3(connection=connection)

def connect_tractor(app: FastHTML, connection: sqlite3.Connection, limit: int = 100) -> FastHTML:
    rt = app.route
    tractor = Tractor.from_sqlite3(connection)
    with open("tractor.js", "r") as f: app.hdrs = listify(app.hdrs) + [Script(code=f.read())]

    def layout(*args):
        return Html(
            Head(
                Title("Tractor Devtools"),
                Script(src="https://unpkg.com/htmx.org@next/dist/htmx.min.js"),
                Script(src="/__tractor__/public/preline.min.js"),
                Link(rel="preconnect", href="https://fonts.googleapis.com"),
                Link(
                    rel="stylesheet",
                    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
                ),
                Link(rel="stylesheet", href="/__tractor__/public/main.min.css"),
            ),
            Body(cls="h-screen", *args)
        )

    @rt('/__tractor__')
    def get():
        db_info = tractor.get_database_info()

        @patch
        def __ft__(self: DatabaseTable):
            # TODO: figure out a cleaner way to do this?
            on_table_change = """document.querySelector("#right").innerHTML = "" """
            return A(
                onClick=on_table_change, 
                data_table_name=self.name,
                hx_get=f"/__tractor__/table/{self.name}?limit={limit}&offset=0",
                hx_target="#table", 
                cls='flex items-center gap-x-1 py-2 px-3 text-sm border border-transparent text-white rounded-lg hover:bg-white/10 focus:outline-none focus:bg-white/10')(
                self.name,
                Span(self.number_of_rows, cls='ms-auto py-px px-1.5 font-medium text-[10px] leading-4 bg-gray-700 text-white rounded-md dark:bg-neutral-700')
            )

        return layout(
            Div(style="border-bottom: solid 1px rgb(156, 163, 175);", cls='fixed z-[60] p-4 left-0 right-0 flex flex-col justify-center bg-white border-bottom border-gray-400 shadow-sm dark:bg-neutral-800 dark:border-neutral-700')(
                P(f"🚜 {db_info.driver} {db_info.version}  database: {db_info.name} ({db_info.location})", cls="font-medium text-stone-800 dark:text-neutral-200"),
            ),
            Aside(id='hs-pro-sidebar', style="top:56px;", tabindex='-1', aria_label='Sidebar', cls='hs-overlay [--auto-close:lg] hs-overlay-open:translate-x-0 -translate-x-full transition-all duration-300 transform w-[260px] hidden fixed inset-y-0 start-0 z-[60] bg-gray-900 lg:block lg:translate-x-0 lg:end-auto lg:bottom-0 dark:bg-neutral-950')(
                Div(cls='flex flex-col h-full max-h-full')(
                    Div(cls='h-[calc(100%-109px)] overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-white/30')(
                        Nav(data_hs_accordion_always_open='', cls='w-full flex flex-col flex-wrap pb-3')(
                            Div(cls='pt-3 border-t border-gray-800 dark:border-neutral-800')(
                                Div(id='preline-accordion', data_hs_accordion_always_open='', cls='hs-accordion-group pt-2 px-3 mt-3 space-y-1 border-t border-gray-800 first:border-transparent first:pt-0 dark:border-neutral-800')(
                                    Div(id='hs-pro-files-accordion-preline', cls='hs-accordion active')(
                                        Button(type='button', aria_expanded='true', aria_controls='hs-pro-files-accordion-preline-sub', cls='hs-accordion-toggle w-full text-start flex items-center gap-x-1 py-2 px-3 text-sm border border-transparent text-white rounded-lg hover:bg-white/10 focus:outline-none focus:bg-white/10')(
                                            Span(cls='me-2 flex justify-center items-center size-3.5')(
                                                Span(cls='size-2.5 inline-block bg-yellow-500 rounded-full')
                                            ),
                                            "Tables",
                                            NotStr("""<svg class="hs-accordion-active:-rotate-180 shrink-0 mt-1 size-3.5 ms-auto transition" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"></path></svg>""")
                                        ),
                                        Div(id='hs-pro-files-accordion-preline-sub', role='region', aria_labelledby='hs-pro-files-accordion-preline', cls='hs-accordion-content w-full overflow-hidden transition-[height] duration-300')(
                                            Ul(data_hs_accordion_always_open='', cls='ps-7 my-1 space-y-1.5 relative before:absolute before:top-0 before:start-[19px] before:w-0.5 before:h-full before:bg-white/10')(
                                                *[table for table in tractor.list_tables()]
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        Div(cls='lg:hidden absolute top-3 -end-3 z-10')(
                            Button(type='button', data_hs_overlay='#hs-pro-sidebar', cls='w-6 h-7 inline-flex justify-center items-center gap-x-2 text-sm font-medium rounded-md border border-gray-800 bg-gray-900 text-gray-400 hover:bg-gray-800 focus:outline-none focus:bg-gray-800 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-950 dark:border-neutral-800 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800')(
                                NotStr("""<svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 8 3 12 7 16"></polyline><line x1="21" x2="11" y1="12" y2="12"></line><line x1="21" x2="11" y1="6" y2="6"></line><line x1="21" x2="11" y1="18" y2="18"></line></svg>""")
                            )
                        )
                    )
                )
            ),
            Main(id='content', style="padding-top:56px;", cls='h-screen flex lg:ps-[260px]')(
                Div(Div(cls='p-5 flex flex-col justify-center items-center text-center')(
                    NotStr("""<svg class="w-48 mx-auto mb-4" width="178" height="90" viewBox="0 0 178 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="27" y="50.5" width="124" height="39" rx="7.5" fill="currentColor" class="fill-white dark:fill-neutral-800"></rect>
                        <rect x="27" y="50.5" width="124" height="39" rx="7.5" stroke="currentColor" class="stroke-stone-50 dark:stroke-neutral-700/10"></rect>
                        <rect x="34.5" y="58" width="24" height="24" rx="4" fill="currentColor" class="fill-stone-50 dark:fill-neutral-700/30"></rect>
                        <rect x="66.5" y="61" width="60" height="6" rx="3" fill="currentColor" class="fill-stone-50 dark:fill-neutral-700/30"></rect>
                        <rect x="66.5" y="73" width="77" height="6" rx="3" fill="currentColor" class="fill-stone-50 dark:fill-neutral-700/30"></rect>
                        <rect x="19.5" y="28.5" width="139" height="39" rx="7.5" fill="currentColor" class="fill-white dark:fill-neutral-800"></rect>
                        <rect x="19.5" y="28.5" width="139" height="39" rx="7.5" stroke="currentColor" class="stroke-stone-100 dark:stroke-neutral-700/30"></rect>
                        <rect x="27" y="36" width="24" height="24" rx="4" fill="currentColor" class="fill-stone-100 dark:fill-neutral-700/70"></rect>
                        <rect x="59" y="39" width="60" height="6" rx="3" fill="currentColor" class="fill-stone-100 dark:fill-neutral-700/70"></rect>
                        <rect x="59" y="51" width="92" height="6" rx="3" fill="currentColor" class="fill-stone-100 dark:fill-neutral-700/70"></rect>
                        <g filter="url(#filter9)">
                        <rect x="12" y="6" width="154" height="40" rx="8" fill="currentColor" class="fill-white dark:fill-neutral-800" shape-rendering="crispEdges"></rect>
                        <rect x="12.5" y="6.5" width="153" height="39" rx="7.5" stroke="currentColor" class="stroke-stone-100 dark:stroke-neutral-700/60" shape-rendering="crispEdges"></rect>
                        <rect x="20" y="14" width="24" height="24" rx="4" fill="currentColor" class="fill-stone-200 dark:fill-neutral-700 "></rect>
                        <rect x="52" y="17" width="60" height="6" rx="3" fill="currentColor" class="fill-stone-200 dark:fill-neutral-700"></rect>
                        <rect x="52" y="29" width="106" height="6" rx="3" fill="currentColor" class="fill-stone-200 dark:fill-neutral-700"></rect>
                        </g>
                        <defs>
                        <filter id="filter9" x="0" y="0" width="178" height="64" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
                        <feFlood flood-opacity="0" result="BackgroundImageFix"></feFlood>
                        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"></feColorMatrix>
                        <feOffset dy="6"></feOffset>
                        <feGaussianBlur stdDeviation="6"></feGaussianBlur>
                        <feComposite in2="hardAlpha" operator="out"></feComposite>
                        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.03 0"></feColorMatrix>
                        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_1187_14810"></feBlend>
                        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_1187_14810" result="shape"></feBlend>
                        </filter>
                        </defs>
                    </svg>"""),
                    Div(cls='max-w-sm mx-auto')(
                        P("👈 Pick a table", cls='mt-2 font-medium text-stone-800 dark:text-neutral-200')
                    )
                ), id="table", cls="relative", style="flex-grow: 2; overflow-x: auto; padding-bottom: 45px;"),
                Div(id="right", cls="border-gray-400", style="min-width: 300px; border-left: solid 1px rgb(156, 163, 175);"),
            ),
        )
    
    @rt("/__tractor__/table/{table_name}")
    def get(table_name: str, request: Request):
        limit, offset, total_rows = int(request.query_params["limit"]), int(request.query_params["offset"]), tractor.count_rows(table_name)
        rows = tractor.list_rows(table_name=table_name, limit=limit, offset=offset)
        return Table(cls='min-w-full table-fixed divide-y divide-stone-200 dark:divide-neutral-700')(
            Thead(
                Tr(*[Th(col, cls="sticky top-0 bg-white") for col in rows[0].columns]),
            ),
            Tbody(cls='divide-y divide-stone-200 dark:divide-neutral-700')(
                *[
                    Tr(
                        *[
                            Td(data_row=k, cls='size-px whitespace-nowrap px-4 py-2')(
                                Span(v, cls='text-sm decoration-2 hover:underline font-medium focus:outline-none focus:underline dark:text-green-400 dark:hover:text-green-500')
                            ) for k, v in row.attributes.items()
                        ],
                        hx_get=f"/__tractor__/record?t={table_name}&id={row.id}", hx_target="#right"
                    ) for row in rows
                ]
            ),
        ), Nav(aria_label='Pagination', cls='fixed bottom-0 bg-white flex mt-5 gap-x-1')(
            Button(
                disabled=offset == 0,
                hx_get=f"/__tractor__/table/{table_name}?limit={limit}&offset={offset - limit}",
                hx_target="#table", type='button', aria_label='Previous', cls='min-h-[38px] min-w-[38px] py-2 px-2.5 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-stone-800 hover:bg-stone-100 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:bg-stone-100 dark:text-white dark:hover:bg-white/10 dark:focus:bg-neutral-700')(
                NotStr("""<svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"></path></svg>"""),
                Span("Previous", cls='sr-only')
            ),
            Div(cls='flex items-center gap-x-1')(
                Span(f"{offset + 1}-{min(offset + limit, total_rows)}", aria_current='page', cls='min-h-[38px] min-w-[38px] flex justify-center items-center text-stone-500 dark:text-neutral-500 py-2 px-3 text-sm rdisabled:opacity-50 disabled:pointer-events-none'),
                Span("of", cls='min-h-[38px] flex justify-center items-center text-stone-500 py-2 px-1.5 text-sm dark:text-neutral-500'),
                Span(f"{total_rows} rows", cls='min-h-[38px] flex justify-center items-center text-stone-500 py-2 px-1.5 text-sm dark:text-neutral-500')
            ),
            Button(
                disabled=offset + limit >= total_rows,
                hx_get=f"/__tractor__/table/{table_name}?limit={limit}&offset={offset + limit}",
                hx_target="#table",
                type='button', aria_label='Next', cls='min-h-[38px] min-w-[38px] py-2 px-2.5 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-stone-800 hover:bg-stone-100 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:bg-stone-100 dark:text-white dark:hover:bg-white/10 dark:focus:bg-neutral-700')(
                Span("Next", cls='sr-only'),
                NotStr("""<svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"></path></svg>""")
            )
        ) if len(rows) != 0 else None 

    @rt("/__tractor__/record")
    def get(request: Request):
        row = tractor.get_row_by_id(table_name=request.query_params["t"], id=request.query_params["id"])
        return Div(cls='p-4 flex flex-col gap-y-4')(
            *[
                Div(cls='flex items-center gap-x-2')(
                    P(k, cls='min-w-20 text-sm text-gray-500 dark:text-neutral-500'),
                    Div(cls='grow')(
                        P(v, cls='font-medium text-sm text-gray-800 dark:text-neutral-200')
                    )
                )   for k, v in row.attributes.items()
            ],
        ) if row is not None else None
    
    @rt("/__tractor__/public/{fname:path}.{ext:static}")
    async def get(fname: str, ext: str): return FileResponse(f"{Path(os.path.realpath(__file__)).parent.parent}/public/{fname}.{ext}")

    return app
