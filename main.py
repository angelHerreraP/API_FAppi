from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str
    price: float

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL)''')
    conn.commit()
    conn.close()

# New function to retrieve all items
@app.get("/items")
def get_all_items():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()  # Fetch all rows as a list of dictionaries
    conn.close()
    return items

# Existing functions for adding, deleting, and updating items

@app.post("/add_item/")
def add_item(item: Item):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
              (item.name, item.description, item.price))
    conn.commit()
    conn.close()
    return {"message": "Item added successfully"}

@app.delete("/delete_item/{item_id}")
def delete_item(item_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    conn.commit()
    conn.close()
    return {"message": "Item deleted successfully"}

@app.put("/update_item/{item_id}")
def update_item(item_id: int, new_item: Item):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE items SET name=?, description=?, price=? WHERE id=?",
              (new_item.name, new_item.description, new_item.price, item_id))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    conn.commit()
    conn.close()
    return {"message": "Item updated successfully"}
