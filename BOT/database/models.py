from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]  # None для нових користувачів
    telegram_id: str
    full_name: str
    phone_number: str
    old_phone_number: str
    graduation_year: int
    department_id: int
    specialty_id: int
    group_name: Optional[str]
    role: str
    birth_date: str
    admin_level: Optional[str] = None  # 'super' або 'limited' для адмінів

@dataclass
class Department:
    id: int
    name: str

@dataclass
class Specialty:
    id: int
    code: str
    name: str