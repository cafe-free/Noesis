import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class MockResponse:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data


class MockTableQuery:
    def __init__(self, table_name: str, db_store: Dict[str, List[Dict[str, Any]]]):
        self.table_name = table_name
        self.db_store = db_store
        self._filters: List[tuple[str, Any]] = []
        self._order_by: Optional[str] = None
        self._action: str = "select"
        self._insert_data: Optional[Any] = None
        self._update_data: Optional[Dict[str, Any]] = None

    def select(self, columns: str = "*") -> "MockTableQuery":
        self._action = "select"
        return self

    def insert(self, data: Any) -> "MockTableQuery":
        self._action = "insert"
        self._insert_data = data
        return self

    def update(self, data: Dict[str, Any]) -> "MockTableQuery":
        self._action = "update"
        self._update_data = data
        return self

    def delete(self) -> "MockTableQuery":
        self._action = "delete"
        return self

    def eq(self, column: str, value: Any) -> "MockTableQuery":
        self._filters.append((column, str(value)))
        return self

    def order(self, column: str, desc: bool = False) -> "MockTableQuery":
        self._order_by = column
        return self

    def execute(self) -> MockResponse:
        records = self.db_store.setdefault(self.table_name, [])

        if self._action == "select":
            res = [r.copy() for r in records]
            for col, val in self._filters:
                res = [r for r in res if str(r.get(col)) == val]
            if self._order_by:
                res.sort(key=lambda r: r.get(self._order_by, 0))
            return MockResponse(res)

        elif self._action == "insert":
            now_str = datetime.now(timezone.utc).isoformat()
            items = self._insert_data if isinstance(self._insert_data, list) else [self._insert_data]
            created = []
            for item in items:
                record = dict(item)
                if "id" not in record or not record["id"]:
                    record["id"] = str(uuid.uuid4())
                if "created_at" not in record or not record["created_at"]:
                    record["created_at"] = now_str
                if self.table_name in ("users", "lessons") and ("updated_at" not in record or not record["updated_at"]):
                    record["updated_at"] = now_str
                if self.table_name == "generation_jobs" and "status" not in record:
                    record["status"] = "pending"
                if self.table_name == "quiz_attempts" and "started_at" not in record:
                    record["started_at"] = now_str
                records.append(record)
                created.append(record.copy())
            return MockResponse(created)

        elif self._action == "update":
            now_str = datetime.now(timezone.utc).isoformat()
            updated = []
            for r in records:
                matches = all(str(r.get(col)) == val for col, val in self._filters)
                if matches:
                    r.update(self._update_data or {})
                    if self.table_name in ("users", "lessons"):
                        r["updated_at"] = now_str
                    updated.append(r.copy())
            return MockResponse(updated)

        elif self._action == "delete":
            to_delete = []
            remaining = []
            for r in records:
                matches = all(str(r.get(col)) == val for col, val in self._filters)
                if matches:
                    to_delete.append(r.copy())
                else:
                    remaining.append(r)
            self.db_store[self.table_name] = remaining
            return MockResponse(to_delete)

        return MockResponse([])


class MockSupabaseClient:
    def __init__(self):
        self.store: Dict[str, List[Dict[str, Any]]] = {}

    def table(self, table_name: str) -> MockTableQuery:
        return MockTableQuery(table_name, self.store)
