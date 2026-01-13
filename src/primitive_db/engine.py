import re
import prompt
import shlex
from prettytable import PrettyTable
from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, drop_table, insert, select, delete


def run():
    commands_no_args = {
        "help": print_help_command,}
    commands_with_args = {
        "create_table": create_table_command,
        "drop_table": drop_table_command,
        "list_tables": list_tables_command,
        "insert": insert_command,
        "select": select_command,
        "delete": delete_command,
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
    pattern = r'^\s*insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$'
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        print("Синтаксис: insert into <имя_таблицы> values (<значение1>, ...)")
        return
    table_name = match.group(1)
    values_str = match.group(2)

    if table_name not in metadata:
        print(f"Таблица '{table_name}' не существует.")
        return

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
    # Ожидается: select from <table> [where ...]
    pattern = r'^\s*select\s+from\s+(\w+)(.*)$'
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        print("Синтаксис: select from <имя_таблицы> [where ...]")
        return
    
    table_name = match.group(1)

    if table_name not in metadata:
        print(f"Таблица '{table_name}' не существует.")
        return

    rest = match.group(2).strip()

    try:
        where_dict = _parse_where(rest) if rest else {}
        results = select(metadata, table_name, where_dict if where_dict else None)
        if not results:
            print("Нет записей.")
            return

        pt = PrettyTable()
        pt.field_names = list(results[0].keys())
        for row in results:
            pt.add_row([row[col] for col in pt.field_names])
        print(pt)
    except Exception as e:
        print(f"Ошибка выборки: {e}")


def delete_command(metadata, user_input, args):
    pattern = r'^\s*delete\s+from\s+(\w+)(.*)$'
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        print("Синтаксис: select from <имя_таблицы> [where ...]")
        return
    
    table_name = match.group(1)

    if table_name not in metadata:
        print(f"Таблица '{table_name}' не существует.")
        return

    rest = match.group(2).strip()

    try:
        where_dict = _parse_where(rest) if rest else {}
        result = delete(metadata, table_name, where_dict if where_dict else None)
        print(f"Удалено записей: {result}")
        
    except Exception as e:
        print(f"Ошибка выборки: {e}")


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


def _parse_where(where_part):
    tokens = list(shlex.shlex(where_part, posix=True))
    where_dict = {}
    i = 0
    while i < len(tokens):
        if tokens[i].lower() == 'where' and i + 2 < len(tokens): #+2 из-за формата where col=val
            keyval = tokens[i+1]
            if '=' in keyval:
                key, value = keyval.split('=', 1)
            else:
                key = keyval
                if i+2 < len(tokens) and tokens[i+2] == '=':
                    value = tokens[i+3] if i+3 < len(tokens) else ''
                    i += 1
                else:
                    value = tokens[i+2]
                    i += 1
            key = key.strip()
            value = value.strip('"\'')
            
            where_dict[key] = value
            i += 3
        else:
            i += 1
    return where_dict