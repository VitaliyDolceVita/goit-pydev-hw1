from collections import UserDict   # Імпортуєм необхідну функцію модуля
from datetime import datetime, timedelta
import pickle
from flask import Flask

app = Flask(__name__)



def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


def get_upcoming_birthdays(users):
    # Поточна дата
    today = datetime.today().date()
    # Список для зберігання дат привітань
    upcoming_birthdays = []
    for user in users:
        # Конвертуємо дату народження з рядка у об'єкт datetime
        birthday = datetime.strptime(user["birthday"], "%Y.%m.%d").date()
        # Визначаємо дату народження в цьому році
        birthday_this_year = birthday.replace(year=today.year)
        # Якщо день народження вже пройшов у цьому році, розглядаємо дату на наступний рік
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=today.year + 1)
        # Різниця між днем народження та поточною датою
        diff = (birthday_this_year - today).days
        # Перевіряємо, чи день народження випадає протягом наступного тижня
        if 0 <= diff <= 7:
            # Якщо день народження припадає на вихідний, переносимо його на наступний понеділок
            if birthday_this_year.weekday() in [5, 6]:
                days_to_monday = (7 - birthday_this_year.weekday()) % 7
                birthday_this_year += timedelta(days=days_to_monday)
            # Додаємо ім'я та дату привітання до списку
            upcoming_birthdays.append(
                {"name": user["name"], "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")})
    return upcoming_birthdays


class Field:  # Створюємо клас Field
    def __init__(self, value):  # Ініціація класу
        self.value = value  # Присвоєння значення атрибуту value

    def __str__(self):  # Оголошення методу для конвертації об'єкта в рядок
        return str(self.value)


class Name:
    def __init__(self, value):
        self.value = value


class Phone(Field):  # Створюєм клас Name який наслідує клас  Field
    def __init__(self, value):  # Оголошення конструктора класу з аргументом value
        super().__init__(value)  # Виклик конструктора батьківського класу Field з передачею значення value
        if not self.is_valid():
            raise ValueError("Invalid phone number format. Please provide a 10-digit phone number.")  # виклик винятку, якщо номер телефону некоректний

    def is_valid(self):  # Оголошення методу для перевірки валідності номера телефону
        return len(self.value) == 10 and self.value.isdigit()  # Повертає True, якщо довжина номера телефону дорівнює 10 і всі символи є цифрами, інакше повертає False


class Birthday:
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:  # Оголошення класу Record
    def __init__(self, name):  # Оголошення конструктора класу з аргументом name
        self.name = Name(name)  # Створення об'єкту класу Name з переданим ім'ям
        self.phones = []  # Ініціалізація порожнього списку для зберігання телефонів
        self.birthday = None

    # @input_error
    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def show_birthday(self):
        if self.birthday:
            return f"{self.name.value}'s birthday is on {self.birthday.date.strftime('%d.%m.%Y')}"
        else:
            return f"{self.name.value} has no birthday set"


    def add_phone(self, phone):  # Оголошення методу для додавання телефону до запису
        self.phones.append(Phone(phone))  # Додавання нового телефону до списку телефонів запису


    def remove_phone(self, phone):  # Оголошення методу для видалення телефону з запису
        self.phones = [p for p in self.phones if p.value != phone]  # Видалення телефону зі списку телефонів запису, якщо він співпадає з переданим


    def edit_phone(self, old_phone, new_phone):  # Оголошення методу для редагування телефону
        for p in self.phones:  # Ітерація по всіх телефонах запису
            if p.value == old_phone:  # Якщо знайдено телефон, який потрібно змінити
                p.value = new_phone  # Заміна старого значення телефону на нове
                break  # Виходимо з циклу після зміни


    def find_phone(self, phone):  # Оголошення методу для пошуку телефону в записі
        for p in self.phones:  # Ітерація по всіх телефонах запису
            if p.value == phone:  # Якщо знайдено шуканий телефон
                return p  # Повертаємо його
        return None  # Повертаємо None, якщо телефон не знайдено


    def __str__(self):  # Оголошення методу для конвертації об'єкту в рядок
        return f"Contact name: {self.name.value}, phone: {'; '.join(p.value for p in self.phones)}"  # Повертає рядок з ім'ям та списком телефонів запису


class AddressBook(UserDict):  # Оголошення класу AddressBook, що успадковує клас UserDict

    def add_record(self, record):
        # Перевіряємо, чи існує вже запис з таким ім'ям у адресній книзі
        existing_record = self.data.get(record.name.value)
        if existing_record:
            # Якщо запис з таким ім'ям існує, додаємо телефони з нового запису до існуючого запису
            existing_record.phones.extend(record.phones)
            # Оновлюємо дату народження існуючого запису на нову, якщо вона була вказана
            existing_record.birthday = record.birthday
        else:
            # Якщо запису з таким ім'ям не існує, додаємо новий запис до адресної книги
            self.data[record.name.value] = record

    def change_record(self, record):  # Оголошення методу для додавання запису до адресної книги
        self.data[record.name.value] = record  # Додавання запису до словника адресної книги, використовуючи ім'я як ключ


    def find(self, name):  # Оголошення методу для пошуку запису за ім'ям у адресній книзі
        return self.data.get(name)  # Повернення запису за вказаним ім'ям, якщо він існує у книзі


    def delete(self, name):  # Оголошення методу для видалення запису за ім'ям з адресної книги
        if name in self.data:  # Перевірка, чи ім'я присутнє у книзі
            del self.data[name]  # Видалення запису з книги, якщо воно присутнє


    def __str__(self):  # Оголошення методу для конвертації об'єкту в рядок
        return "\n".join(str(record) for record in self.data.values())  # Повертає рядок, складений з рядків, які представляють кожен запис у словнику адресної книги


# Декоратор для обробки помилок введення користувача
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command."
    return inner


@input_error
def parse_input(user_input):
    parts = user_input.split()
    return parts

@app.route('/')
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if user_input:
            command, *args = parse_input(user_input)
        else:
            print("Invalid command.")
            continue
        if command in ["close", "exit"]:
            print("Saving data...")
            save_data(book)  # Збереження даних перед виходом з програми
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            if len(args) < 2:
                print("Invalid command. Please provide both name and phone number.")
                continue
            name = args[0]
            phone = args[1]
            if len(phone) != 10 or not phone.isdigit():
                print("Invalid phone number format. Please provide a 10-digit phone number.")
                continue
            elif name.isdigit():
                print("Invalid name format. Please provide valid name.")
                continue
            else:
                user_record = Record(name)
                user_record.add_phone(phone)
                book.add_record(user_record)
                print("Record added successfully!")
        elif command == "change":
            name = args[0]
            new_phone = args[1]
            if name in book:
                user_record = Record(name)
                user_record.add_phone(new_phone)
                book.change_record(user_record)
                print(f"Phone number for {name} updated successfully!")
            else:
                print(f"No record found for {name}.")
        elif command == "phone":
            if not args:
                print("please provide name")
                continue
            else:
                name = args[0]
                found_phone = book.find(name)
                print(f"{found_phone}")
        elif command == "all":
            for name, record in book.data.items():
                print(record)
        elif command == "add-birthday":
            if not args:
                print("please input name and date format. Use DD.MM.YYYY ")
                continue
            else:
                name = args[0]
                new_birthday = args[1]
                user_record = Record(name)
                user_record.add_birthday(new_birthday)
                book.add_record(user_record)
                print("Birthday added successfully!")
        elif command == "show-birthday":
            name = args[0]
            found_record = book.find(name)
            if found_record:
                print(found_record.show_birthday())
            else:
                print(f"No record found for {name}.")
        elif command == "birthdays":
            users = []
            for record in book.data.values():
                if record.birthday:
                    users.append({"name": record.name.value, "birthday": record.birthday.date.strftime("%Y.%m.%d")})
            upcoming_birthdays = get_upcoming_birthdays(users)
            print("Список привітань на цьому тижні:", upcoming_birthdays)
        else:
            print("Invalid command.")


# Перевіряємо, чи цей скрипт є основним і викликаємо функцію main.
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
