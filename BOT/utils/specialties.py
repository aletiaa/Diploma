SPECIALTIES = [
    {"id": 1, "code": "121", "name": "Інженерія програмного забезпечення"},
    {"id": 2, "code": "122", "name": "Комп’ютерні науки"},
    {"id": 3, "code": "174", "name": "Автоматизація та комп'ютерно-інтегровані технології"},
    {"id": 4, "code": "144", "name": "Теплоенергетика"},
    {"id": 5, "code": "143", "name": "Атомна енергетика"},
    {"id": 6, "code": "142", "name": "Енергетичне машинобудування"}
]


def search_specialty(user_input):
    input_lower = user_input.lower()
    return [
        s for s in SPECIALTIES
        if input_lower in s['code'] or input_lower in s['name'].lower()
    ]
