SPECIALTIES = [
    {"code": "121", "name": "Інженерія програмного забезпечення"},
    {"code": "122", "name": "Комп’ютерні науки"},
    {"code": "174", "name": "Автоматизація та комп'ютерно-інтегровані технології та робототехника"},
    {"code": "144", "name": "Теплоенергетика"},
    {"code": "143", "name": "Атомна енергетика"},
    {"code": "142", "name": "Енергетичне машинобудування"}
]

def search_specialty(user_input):
    input_lower = user_input.lower()
    return [
        s for s in SPECIALTIES
        if input_lower in s['code'] or input_lower in s['name'].lower()
    ]
