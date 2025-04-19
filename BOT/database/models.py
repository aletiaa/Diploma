from dataclasses import dataclass

@dataclass
class User:
    id: int
    telegram_id: str
    full_name: str
    phone_number: str
    graduation_year: int
    department_id: int
    specialty_id: int
    group_name: str
    role: str

@dataclass
class Department:
    id: int
    name: str

@dataclass
class Specialty:
    id: int
    code: str
    name: str