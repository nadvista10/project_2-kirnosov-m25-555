import prompt
import shlex

from primitive_db.utils import load_metadata, load_table_data, save_metadata
from primitive_db.core import create_table, drop_table, insert, select


def run():
    commands_no_args = {
        "help": print_help_command,}
    commands_with_args = {
        "create_table": create_table_command,
        "drop_table": drop_table_command,
        "list_tables": list_tables_command,
        "insert": insert_command,
        "select": select_command,
    }

    metadata = load_metadata()

    print_help_command()

    while(True):
        user_input = prompt.string("Введите команду:")

        args = shlex.split(user_input)
        command = args[0] if args else ""

        if command == "exit":
            break

        if command in commands_with_args:
            commands_with_args[command](metadata, args[1:])
        elif command in commands_no_args:
            commands_no_args[command]()
        else:
            show_error_command()


def create_table_command(metadata, args):
    if len(args) < 1:
        print("Для создания таблицы необходимо указать имя")
        return
    
    try:
        create_table(metadata, args[0], args[1:])
        save_metadata(metadata)
    except ValueError as e:
        print(e)


def drop_table_command(metadata, args):
    if len(args) < 1:
        print("Для удаления таблицы необходимо указать имя")
        return
    try:
        drop_table(metadata, args[0])
        save_metadata(metadata)
    except ValueError as e:
        print(e)


def list_tables_command(metadata, args):
    for table_name in metadata.keys():
        print(f"- {table_name}")


def insert_command(metadata, args):
    try:
        insert(metadata, args[0], args[1:])
    except ValueError as e:
        print(e)


def select_command(metadata, args):
    if len(args) < 1:
        print("Для выбора данных необходимо указать имя таблицы")
        return
    table_name = args[0]
    args.remove(table_name)

    if len(args) % 2 != 0:
        print("Некорректный формат условий")
        return
    where_clause = {}
    for i in range(0, len(args), 2):
        where_clause[args[i]] = args[i+1]

    try:
        table_data = load_table_data(table_name)
        results = select(table_data, where_clause if where_clause else None)
        for row in results:
            print(row)
    except ValueError as e:
        print(e)


def show_error_command():
    print("Неизвестная команда. Введите 'help' для справки.")


def print_help_command():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 