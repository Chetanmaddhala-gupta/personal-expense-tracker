from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


app = FastAPI(title="Personal Expense Tracker")

# In-memory storage keeps this assignment simple; expenses reset when the server stops.
expenses: dict[int, dict] = {}
next_expense_id = 1


class ExpenseInput(BaseModel):
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)


@app.get("/")
async def home():
    return FileResponse(Path(__file__).with_name("index.html"))


@app.get("/api/expenses")
async def get_expenses():
    return list(expenses.values())


@app.post("/api/expenses", status_code=201)
async def add_expense(expense: ExpenseInput):
    global next_expense_id
    description = expense.description.strip()
    category = expense.category.strip()
    if not description or not category:
        raise HTTPException(status_code=422, detail="Description and category cannot be empty.")

    new_expense = {
        "id": next_expense_id,
        "description": description,
        "amount": expense.amount,
        "category": category,
    }
    expenses[next_expense_id] = new_expense
    next_expense_id += 1
    return {"message": "Expense added successfully.", "expense": new_expense}


@app.put("/api/expenses/{expense_id}")
async def update_expense(expense_id: int, expense: ExpenseInput):
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    description = expense.description.strip()
    category = expense.category.strip()
    if not description or not category:
        raise HTTPException(status_code=422, detail="Description and category cannot be empty.")

    updated_expense = {
        "id": expense_id,
        "description": description,
        "amount": expense.amount,
        "category": category,
    }
    expenses[expense_id] = updated_expense
    return {"message": "Expense updated successfully.", "expense": updated_expense}


@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: int):
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    del expenses[expense_id]
    return {"message": "Expense deleted successfully."}
