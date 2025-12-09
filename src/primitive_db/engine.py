import prompt
import shlex

from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, drop_table

def run():
    commands_no_args = {
        "help": print_help_command,}
    commands_with_args = {
        "create_table": create_table_command,
        "drop_table": drop_table_command,
        "list_tables": list_tables_command,
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