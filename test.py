from fasthtml.common import Client, Database
from tractor import Tractor, DatabaseColumn

def test_connect_tractor(test_client: Client, test_table_names):
    response = test_client.get('/__tractor__')
    assert response.status_code == 200
    for t in test_table_names: assert f'data-table-name="{t}"' in response.text

def test_tractor_sqlite3_client(test_db: Database, test_table_names):
    t = Tractor.from_sqlite3(connection=test_db.conn)

    db_info = t.get_database_info()

    assert db_info.driver == "SQLite"
    assert db_info.name == "main"
    assert "test-database.db" in db_info.location

    tables = t.list_tables()
    assert list(map(lambda tt: tt.name, tables)) == test_table_names
    assert tables[0].number_of_rows == 347

    assert t.count_rows(table_name='albums') == 347

    rows = t.list_rows(table_name='albums', limit=5, offset=0)

    assert rows[0].table_name == 'albums'
    assert rows[0].columns == [DatabaseColumn(name="AlbumId",is_pk=True), DatabaseColumn(name="Title",is_pk=False), DatabaseColumn(name="ArtistId",is_pk=False)]
    assert rows[0].id == 1
    assert rows[0].attributes["Title"] == 'For Those About To Rock We Salute You'
    assert rows[0].attributes["ArtistId"] == 1

    assert len(rows) == 5

    rows = t.list_rows(table_name='albums', limit=5, offset=5)

    assert rows[0].id == 6

    r = t.get_row_by_id(table_name='albums', id=4)

    assert r is not None
    assert r.id == 4

    assert t.get_row_by_id(table_name='albums', id=999) is None
