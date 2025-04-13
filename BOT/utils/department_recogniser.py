def normalize_department(input_text):
    input_text = input_text.lower().strip().replace("-", " ")

    matches = {
        "теф": "Теплоенергетичний факультет",
        "нніате": "Теплоенергетичний факультет",
        "навчально науковий інститут атомної та теплової енергетики": "Теплоенергетичний факультет",
        "теплоенергетичний факультет": "Теплоенергетичний факультет"
    }

    for key, standard in matches.items():
        if key in input_text:
            return standard
    return None
