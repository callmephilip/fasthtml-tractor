import pytest
import os
from typing import List
from fasthtml.common import Client, FastHTML, database
from tractor import connect_tractor

TEST_DATABASE = 'data/test-database.db'
SOURCE_DATABASE = 'data/tractor.db'

@pytest.fixture
def test_client() -> Client:
    if os.path.exists(TEST_DATABASE): os.remove(TEST_DATABASE)
    with open(SOURCE_DATABASE, 'rb') as source:
        with open(TEST_DATABASE, 'wb') as target: target.write(source.read())
    return Client(app=connect_tractor(app=FastHTML(), connection=database(TEST_DATABASE).conn))

@pytest.fixture
def test_db() -> Client:
    if os.path.exists(TEST_DATABASE): os.remove(TEST_DATABASE)
    with open(SOURCE_DATABASE, 'rb') as source:
        with open(TEST_DATABASE, 'wb') as target: target.write(source.read())
    return database(TEST_DATABASE)

@pytest.fixture
def test_table_names() -> List[str]:
    # XX: skipping 'sqlite_stat1'
    ts = ['albums', 'sqlite_sequence', 'artists', 'customers', 'employees', 'genres', 'invoices', 'invoice_items', 'media_types', 'playlists', 'playlist_track', 'tracks']
    ts.sort()
    return ts
