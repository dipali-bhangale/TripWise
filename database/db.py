import sqlite3,json
from pathlib import Path
DB=Path(__file__).resolve().parent.parent/'tripwise.db'
def connect():
 c=sqlite3.connect(DB); c.execute('CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY AUTOINCREMENT,destination TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,data TEXT NOT NULL)'); c.execute('CREATE TABLE IF NOT EXISTS itineraries(id INTEGER PRIMARY KEY AUTOINCREMENT,trip_id INTEGER, itinerary_json TEXT)'); c.execute('CREATE TABLE IF NOT EXISTS user_preferences(id INTEGER PRIMARY KEY AUTOINCREMENT,preferences_json TEXT)'); c.commit(); return c
def save_trip(t):
 with connect() as c:
  cur=c.execute('INSERT INTO trips(destination,data) VALUES (?,?)',(t['destination'],json.dumps(t))); tid=cur.lastrowid
  c.execute('INSERT INTO itineraries(trip_id,itinerary_json) VALUES (?,?)',(tid,json.dumps(t['itinerary']))); return tid
def list_trips():
 with connect() as c: return c.execute('SELECT id,destination,created_at FROM trips ORDER BY id DESC').fetchall()
def load_trip(i):
 with connect() as c: r=c.execute('SELECT data FROM trips WHERE id=?',(i,)).fetchone(); return json.loads(r[0]) if r else None
def delete_trip(i):
 with connect() as c: c.execute('DELETE FROM itineraries WHERE trip_id=?',(i,));c.execute('DELETE FROM trips WHERE id=?',(i,))
