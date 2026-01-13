import re
import prompt
import shlex
from prettytable import PrettyTable
from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, drop_table, insert, select, delete, update


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
        "update": update_command,
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


def update_command(metadata, user_input, args):
    pattern = r'^\s*update\s+(\w+)(.*)$'
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        print("Синтаксис: update <имя_таблицы> set <столбец>=<значение> where <столбец>=<значение>")
        return

    table_name = match.group(1)
    rest = match.group(2).strip()

    if table_name not in metadata:
        print(f"Таблица '{table_name}' не существует.")
        return

    if not rest:
        print("Синтаксис: update <имя_таблицы> set <столбец>=<значение> where <столбец>=<значение>")
        return

    try:
        set_dict = _parse_set(rest)
        where_dict = _parse_where(rest)

        if not set_dict:
            print("Не указаны изменения. Добавьте хотя бы один 'set'.")
            return
        if not where_dict:
            print("Не указаны условия. Добавьте хотя бы один 'where'.")
            return

        updated = update(metadata, table_name, set_dict, where_dict)
        print(f"Обновлено записей: {updated}")
    except Exception as e:
        print(f"Ошибка обновления: {e}")


def show_error_command():
    print("Неизвестная команда. Введите 'help' для справки.")


def print_help_command():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - добавить запись")
    print("<command> select from <имя_таблицы> [where ...] - выбрать записи")
    print("<command> delete from <имя_таблицы> [where ...] - удалить записи")
    print("<command> update <имя_таблицы> set ... where ... - обновить записи")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 


def _parse_keyword_clauses(text_part, keyword):
    lexer = shlex.shlex(text_part, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = list(lexer)

    clauses = {}
    i = 0
    keyword_lower = keyword.lower()
    while i < len(tokens):
        if tokens[i].lower() != keyword_lower:
            i += 1
            continue

        if i + 1 >= len(tokens):
            break

        keyval = tokens[i + 1]
        key = None
        value = None

        if "=" in keyval:
            key, value = keyval.split("=", 1)
            i += 2
        elif i + 3 < len(tokens) and tokens[i + 2] == "=":
            key = keyval
            value = tokens[i + 3]
            i += 4
        elif i + 2 < len(tokens):
            key = keyval
            value = tokens[i + 2]
            i += 3
        else:
            break

        key = (key or "").strip()
        value = (value or "").strip().strip('"\'')
        if key:
            clauses[key] = value

    return clauses


def _parse_where(where_part):
    return _parse_keyword_clauses(where_part, "where")


def _parse_set(set_part):
    return _parse_keyword_clauses(set_part, "set")