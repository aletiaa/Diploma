from dataclasses import dataclass
from typing import Optional

# Користувач або адміністратор
@dataclass
class User:
    id: Optional[int]  # None для нових користувачів
    telegram_id: str
    full_name: str
    phone_number: str
    old_phone_number: Optional[str]
    graduation_year: Optional[int]
    department_id: Optional[int]
    specialty_id: Optional[int]
    group_name: Optional[str]
    role: str  # 'user' або 'admin'
    access_level: Optional[str]  # 'user', 'admin_limited', 'admin_super'
    birth_date: Optional[str]

# Кафедра (хоч одна, але залишимо для структури)
@dataclass
class Department:
    id: int
    name: str

# Спеціальність
@dataclass
class Specialty:
    id: int
    code: str
    name: str

# Адміністратор (для окремої логіки, якщо потрібно)
@dataclass
class Admin:
    id: Optional[int]
    telegram_id: str
    full_name: str
    phone_number: str
    role: str  # 'admin'
    access_level: str  # 'admin_limited' або 'admin_super'
    password: str
