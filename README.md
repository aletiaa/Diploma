This Telegram bot is designed for the automated registration of university alumni, department administrators, and interaction between them. It conveniently records alumni information, allows searching, sends news, and manages data.

---

## 📦 Main Features

- ✅ User and administrator registration
- 📲 Phone number verification (manually or via `request_contact`)
- 🏫 Department and specialty selection from the database
- 🎂 Entering date of birth and graduation year
- 🔑 Administrator authorization via password
- 🧑‍💻 Role division: administrator/limited administrator
- 🧾 Searching for users by surname and phone number
- 🧠 Data storage using SQLite
- 🎉 Automatic birthday greetings
- 🔐 Detection of suspicious messages (*-*)


---

## 🛠️ Technologies

- Python 3.11+
- [Aiogram 3.x](https://docs.aiogram.dev/)
- SQLite3
- JSON (for storing administrators)
- Telegram Bot API

## 🚀 Launch

```bash
python -m BOT.bot
```

> Before launching, make sure to set the `BOT_TOKEN` in `config.py`

---

## 🧪 Testing

1. Start the bot with /start
2. Select **Registration** or **Login**
3. In case of registration, provide:
   - Full name
   - Phone number (or send a contact)
   - Whether it was your number during your studies
   - Date of birth
   - Graduation year
   - Department
   - Specialty

---

## 🔐 Administrator

- Requires a password (`ADMIN_PASSWORD`)
- Can have the role of `admin` or `limited admin`
- Full rights — for department heads

---

## 📌 Note

- If the bot receives a message `*-*`, it notifies all administrators about suspicious activity.
- Phone numbers are verified using `phone_rules.csv`, which contains country-specific rules.

---

🔗 **Project created for the diploma thesis**  
Author: **Alina Seikauskaite**  
University: *Kyiv Polytechnic University of Ukraine*
