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

    try:
        while True:
            user_input = prompt.string("Введите команду:")

            args = shlex.split(user_input)
            command = args[0] if args else ""

            if command == "exit":
                break

            if command in commands_with_args:
                commands_with_args[command](metadata, user_input, args[1:])
            elif command in commands_no_args:
                commands_no_args[command]()
            else:
                show_error_command()
    except KeyboardInterrupt:
        print("\nЗавершение работы.")


def create_table_command(metadata, user_input, args):
    if len(args) < 1:
        print("Для создания таблицы необходимо указать имя")
        return
    if len(args) < 2:
        print("Для создания таблицы необходимо указать хотя бы один столбец")
        return
    try:
        create_table(metadata, args[0], args[1:])
        save_metadata(metadata)
    except ValueError as e:
        print(e)


def drop_table_command(metadata, user_input, args):
    if len(args) < 1:
        print("Для удаления таблицы необходимо указать имя")
        return
    try:
        drop_table(metadata, args[0])
        save_metadata(metadata)
        
    except ValueError as e:
        print(e)


def list_tables_command(metadata, user_input, args):
    for table_name in metadata.keys():
        print(f"- {table_name}")


def insert_command(metadata, user_input, args):
    import re

    pattern = r'^\s*insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$'
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        print("Синтаксис: insert into <имя_таблицы> values (<значение1>, ...)")
        return
    table_name = match.group(1)
    values_str = match.group(2)

    try:
        lexer = shlex.shlex(values_str, posix=True)
        lexer.whitespace = ','
        lexer.whitespace_split = True
        lexer.quotes = '"\''
        values = [v.strip() for v in lexer if v.strip() != '']
    except Exception as e:
        print(f"Ошибка разбора значений: {e}")
        return

    try:
        insert(metadata, table_name, values)
    except Exception as e:
        print(f"Ошибка вставки: {e}")
    


def select_command(metadata, user_input, args):
    pass


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