from fasthtml.common import *
from tractor import connect_tractor

app = FastHTMLWithLiveReload(
    hdrs=(picolink,
        # `Style` is an `FT` object, which are 3-element lists consisting of:
        # (tag_name, children_list, attrs_dict).
        # FastHTML composes them from trees and auto-converts them to HTML when needed.
        # You can also use plain HTML strings in handlers and headers,
        # which will be auto-escaped, unless you use `NotStr(...string...)`.
        Style(':root { --pico-font-size: 100%; }'),
        # Have a look at fasthtml/js.py to see how these Javascript libraries are added to FastHTML.
        # They are only 5-10 lines of code each, and you can add your own too.
        SortableJS('.sortable'),
    )
)
rt = app.route
db = database('data/tractor.db')

connect_tractor(app, db.conn)

@rt('/')
def get(): return Div(P('Hello World!'))

@rt("/{fname:path}.{ext:static}")
async def get(fname: str, ext: str): return FileResponse(f"public/{fname}.{ext}")

serve()
