import sys
import requests
from datetime import datetime

base_url = "https://api.trello.com/1/{}"

# это данные тестовой доски, с ней можно делать все что угодно, для удобства проверяющего ;)
# можете ввести данные своей доски и работать с ней
auth_params = {
    "key": "279e90f7d23ca4c459ec54666e9397e8",
    "token": "1d3a4e99f3f624ff2727a6c1b05a6ded3c9a13d97b5b4c4fd683ff0c9bb10bee"
}
board_id = "Mo1GyeL9"


def read_tasks():
    """
    Чтение колонок и вывод на экран
    """   
    print("\nСписок задач:\n")
    columns = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
    for column in columns:
        print("{:21} {}".format("КОЛОНКА: ", column["name"]))
        print("{:21} {}".format("ID колонки: ", column["id"]))
        tasks = requests.get(base_url.format("lists") + "/" + column["id"] + "/cards", params=auth_params).json()
        print("{:21} {:<}\n".format("Количество задач: ", len(tasks)))
        if tasks:
            task_number = 1
            for task in tasks:
                print(" {}) {:17} {}".format(task_number, "ЗАДАЧА: ", task["name"]))
                print("    {:17} {}".format("ID задачи: ", task["id"]))
                d = datetime.strptime(task["dateLastActivity"],"%Y-%m-%dT%H:%M:%S.%fZ")
                new_format = "%H:%M %d.%m.%Y"
                print("    {:17} {}".format("Задача изменена: ", d.strftime(new_format)))
                print("    {:17} {}".format("Описание: ", task["desc"] if task["desc"] else "Нет"))
                print("    {:17} {}\n".format("Активная: ", "Нет" if task["closed"] else "Да"))
                task_number += 1


def append_task(task_name, target_column = None):
    """
    Добавление задачи в определенную колонку
    """
    if task_name.strip():
        columns = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()

        found_columns = {} # словарь найденых колонок
        all_columns = {} # все колонки
        column_id = ""
        for column in columns:
            all_columns[column["id"]] = column["name"] # заодно сохраним данные всех колонок, все равно всех перебираем
            if column["name"] == target_column or column["id"] == target_column: # ищем целевую колонку или колонки
                found_columns[column["id"]] = column["name"]

        if target_column: # если задана колонка
            if found_columns: # и найдена заданная колонка
                if len(found_columns) > 1:
                    # если колонок несколько, то запрашиваем пользователя
                    print("\nНайдено несколько колонок с одинаковым именем:\n")
                    column_id = userChoice(found_columns, False)
                else:
                    # если одна то берем ее id
                    column_id = list(found_columns.keys())[0]
            else:
                # если колонка не найдена то создаем ее и заново добавляем задачу
                append_column(target_column)
                append_task(task_name, target_column)
        else:
            # если колонка не задана то запрашиваем у пользователя выбор из всех колонок
            print("\nВыберите целевую колонку для добавления задачи:\n")
            column_id = userChoice(all_columns, False)

        if column_id: # если не было ошибки при запросе пользователя
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column_id, **auth_params})
            print("Задача '{}' добавлена.\n".format(task_name))
    else:
        print("Не задано имя задачи.")


def delete_task(target_task):
    """
    Удаление задачи
    """
    columns = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
    found_tasks = {} # словарь найденых задач если их несколько
    for column in columns: # перебираем все задачи во всех колонках
        tasks = requests.get(base_url.format("lists") + "/" + column["id"] + "/cards", params=auth_params).json()
        for task in tasks:
            if task["name"] == target_task or task["id"] == target_task:
                # добавляем данные задачи в словарь если имя или id задачи совпадает
                # ключ словаря id задачи, значение - артибуты задачи и колонки, где она обнаружена
                found_tasks[task["id"]] = [column["name"], column["id"], task["name"], task["dateLastActivity"], task["desc"], task["closed"]]

    if found_tasks: # если найдена хоть одна задача
        if len(found_tasks) > 1: 
            # если найдено больше 1 задачи то запрашиваем пользователя 
            print("\nНайдено несколько задач с одинаковым именем:\n")
            task_id = userChoice(found_tasks)
        else:
            # если всего одна задача
            task_id = list(found_tasks.keys())[0]

        if task_id: # если не было ошибки при запросе пользователя то удаляем задачу
            requests.delete(base_url.format('cards') + '/' + task_id, data={**auth_params})
            print("Задача '{}' удалена.\n".format(target_task))
    else:
        print("Задача '{}' не найдена.\n".format(target_task))


def append_column(target_column):
    """
    Добавляет новую колонку
    """
    if target_column.strip():
        requests.post(base_url.format('boards') + '/' + board_id + '/lists', data={'name': target_column.strip(), **auth_params})
        print("Колонка '{}' добавлена.\n".format(target_column))
    else:
        print("Не корректное имя колонки.")


def delete_column(target_column):
    """
    Удаляет колонку 
    """
    columns = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
    found_columns = {} # словарь найденых колонок
    column_id = ""
    for column in columns:
        if column["name"] == target_column or column["id"] == target_column: # ищем целевую колонку или колонки
            found_columns[column["id"]] = column["name"]

    if found_columns:
        if len(found_columns) > 1:
            # если колонок несколько, то запрашиваем пользователя
            print("\nНайдено несколько колонок с одинаковым именем:\n")
            column_id = userChoice(found_columns, False)
        else:
            # если одна то берем ее id
            column_id = list(found_columns.keys())[0]

        if column_id: # если не было ошибки при запросе пользователя
            requests.put(base_url.format('lists') + '/' + column_id + '/closed', data={'value': 'true', **auth_params})
            print("Колонка '{}' удалена.\n".format(target_column))
    else:
        print("Колонка '{}' не найдена.\n".format(target_column))


def move(target_task, target_column):
    """
    Обработка перемещения существующей задачи межну колонками
    """
    columns = requests.get(base_url.format("boards") + "/" + board_id + "/lists", params=auth_params).json()
    found_tasks = {} # словарь найденых задач если их несколько
    column_id = "" # id колонки в которую будем перемещать задачу
    found_columns = {} # словарь найденых целевых колонок если их несколько
    for column in columns:
        if column["name"] == target_column or column["id"] == target_column: # ищем целевую колонку или колонки
            found_columns[column["id"]] = column["name"]
        tasks = requests.get(base_url.format("lists") + "/" + column["id"] + "/cards", params=auth_params).json()
        for task in tasks:
            if task["name"] == target_task or task["id"] == target_task: # ищем задачи с заданным именем или id
                found_tasks[task["id"]] = [column["name"], column["id"], task["name"], task["dateLastActivity"], task["desc"], task["closed"]]

    if found_columns: # если колонка существует
        if len(found_columns) > 1:
            # если колонок несколько, то запрашиваем пользователя
            print("\nНайдено несколько колонок с одинаковым именем:\n")
            column_id = userChoice(found_columns, False)
        else:
            # если одна то берем ее id
            column_id = list(found_columns.keys())[0]

        if column_id: # если не было ошибки при запросе пользователя
            if found_tasks: # если задача с таким именем существует 
                if len(found_tasks) > 1:
                    # если задач несколько, то запрашиваем пользователя
                    print("\nНайдено несколько задач с одинаковым именем:\n")
                    task_id = userChoice(found_tasks)
                else:
                    # если всего одна 
                    task_id = list(found_tasks.keys())[0]
                if task_id: # если не было ошибки при запросе пользователя то переносим задачу
                    requests.put(base_url.format("cards") + "/" + task_id + "/idList", data={"value": column_id, **auth_params})
                    print("Задача '{}' перенесена в колонку '{}'.\n".format(target_task, target_column))
            else:
                print("Задача '{}' не найдена.\n".format(target_task))
    else:
        print("Колонка '{}' не найдена.\n".format(target_column))


def userChoice(dictionary, is_tasks = True):
    """
    Взаимодействие с пользователем при нахождении нескольких задач или колонок
    Возвращает ID
    """
    if is_tasks:
        tasks_id = [] # список id
        for key, value in dictionary.items():
            tasks_id.append(key)
            print("{}) {:17} {}".format(len(tasks_id), "ЗАДАЧА: ", value[2]))
            print("   {:17} {}".format("ID задачи: ", key))
            print("   {:17} {}".format("В колонке: ", value[0]))
            print("   {:17} {}".format("ID колонки: ", value[1]))
            d = datetime.strptime(value[3],"%Y-%m-%dT%H:%M:%S.%fZ")
            new_format = "%H:%M %d.%m.%Y"
            print("   {:17} {}".format("Задача изменена: ", d.strftime(new_format)))
            print("   {:17} {}".format("Описание: ", value[4] if value[4] else "Нет"))
            print("   {:17} {}\n".format("Активная: ", "Нет" if value[5] else "Да"))
        choice = input("Выберите по номеру в списке или по ID задачи: ")
        if choice: # если что то было введено пользователем
            if choice.isdigit(): # если это цифра
                if int(choice) in range(1, len(tasks_id) + 1): # если эта цифра в пределах номеров списка задач
                    return tasks_id[int(choice) - 1] # возвращаем id задачи
            else:
                if choice in tasks_id: # если это набор символов, то проверяем его на совпадение со списком id задач
                    return choice # возвращаем id задачи
    else:
        columns_id = []
        for key, value in dictionary.items():
            columns_id.append(key)
            print("{}) {:17} {}".format(len(columns_id), "КОЛОНКА: ", value))
            print("   {:17} {}\n".format("ID колонки: ", key))
        choice = input("Выберите по номеру в списке или по ID колонки: ")
        if choice: # если что то было введено пользователем
            if choice.isdigit(): # если это цифра
                if int(choice) in range(1, len(columns_id) + 1): # если эта цифра в пределах номеров списка
                    return columns_id[int(choice) - 1] # возвращаем id колонки
            else:
                if choice in columns_id: # если это набор символов, то проверяем его на совпадение со списком id колонок
                    return choice # возвращаем id колонки
    print("Некорректное значение")


help_text = """Запуск приложения с параметрами:
python {prg} [ключ] [параметр] [параметр]

Запуск без ключей и параметров выведет все задачи на доске.

Ключи: create_task, create_column, delete_task, delete_column, move_task

create_task - добавить задачу
python {prg} create_task "Имя задачи" "Имя колонки"
python {prg} create_task "Имя задачи"

create_column - добавить колонку
python {prg} create_column "Имя колонки"

delete_task - удалить задачу
python {prg} delete_task "Имя задачи/ID задачи"

delete_column - удалить колонку
python {prg} delete_column "Имя колонки/ID колонки"

move_task - перенос задачи между колонками
python {prg} move_task "Имя задачи/ID задачи" "Имя целевой колонки/ID колонки"
""".format(prg = sys.argv[0])

if __name__ == "__main__":    
    if len(sys.argv) == 1:    
        read_tasks()    
        print("\nСправка по ключам запуска программы:\n{}".format("python " + sys.argv[0] + " ?\n"))
    elif sys.argv[1] == "create_task":
        if len(sys.argv) == 4:   
            append_task(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            append_task(sys.argv[2])
        else:
            print("\nНекорректные параметры запуска.\n")
            print(help_text)
    elif sys.argv[1] == "move_task":
        if len(sys.argv) == 4:   
            move(sys.argv[2], sys.argv[3])
        else:
            print("\nНекорректные параметры запуска.\n")
            print(help_text)
    elif sys.argv[1] == "create_column":
        if len(sys.argv) == 3:   
            append_column(sys.argv[2])
        else:
            print("\nНекорректные параметры запуска.\n")
            print(help_text)
    elif sys.argv[1] == "delete_task":
        if len(sys.argv) == 3:   
            delete_task(sys.argv[2])
        else:
            print("\nНекорректные параметры запуска.\n")
            print(help_text)
    elif sys.argv[1] == "delete_column":
        if len(sys.argv) == 3:   
            delete_column(sys.argv[2])
        else:
            print("\nНекорректные параметры запуска.\n")
            print(help_text)
    elif sys.argv[1] == "?":
        if len(sys.argv) == 2:
            print(help_text)


# Для теста функций, отключить последний if и использовать прямой вызов функций ниже

# read_tasks()

# append_task("Новая задача 3", "Новая колонка 1")

# append_task("Новая задача 4")

# append_task("Новая задача 3", "Авто новая")

# move("Новая задача 2", "Готово")

# append_column("Недодел")

# delete_task("Научиться использовать Trello API")

# delete_column("Недодел")