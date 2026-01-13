import re
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.utils import load_metadata


def _print_rows(rows):
    if not rows:
        print("Нет записей.")
        return
    table = PrettyTable()
    table.field_names = list(rows[0].keys())
    for row in rows:
        table.add_row([row[col] for col in table.field_names])
    print(table)


def _match(pattern, user_input, usage):
    match = re.match(pattern, user_input, re.IGNORECASE)
    if not match:
        raise ValueError(usage)
    return match


def run():
    commands_no_args = {
        "help": print_help_command,
    }
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
            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"Некорректный ввод: {e}")
                continue
            command = args[0] if args else ""

            if command == "exit":
                break

            handler = commands_with_args.get(command)
            if handler is not None:
                handler(metadata, user_input, args[1:])
                continue

            handler = commands_no_args.get(command)
            if handler is not None:
                handler()
                continue

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
    create_table(metadata, args[0], args[1:])


def drop_table_command(metadata, user_input, args):
    if len(args) < 1:
        print("Для удаления таблицы необходимо указать имя")
        return
    drop_table(metadata, args[0])


def list_tables_command(metadata, user_input, args):
    for table_name in metadata.keys():
        print(f"- {table_name}")


def insert_command(metadata, user_input, args):
    usage = "Синтаксис: insert into <имя_таблицы> values (<значение1>, ...)"
    try:
        match = _match(
            r'^\s*insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$',
            user_input,
            usage,
        )
        table_name = match.group(1)
        values_str = match.group(2)

        lexer = shlex.shlex(values_str, posix=True)
        lexer.whitespace = ','
        lexer.whitespace_split = True
        lexer.quotes = '"\''
        values = [v.strip() for v in lexer if v.strip()]
    except ValueError as e:
        print(e)
        return

    insert(metadata, table_name, values)
    

def select_command(metadata, user_input, args):
    usage = "Синтаксис: select from <имя_таблицы> [where ...]"
    try:
        match = _match(r'^\s*select\s+from\s+(\w+)(.*)$', user_input, usage)
        table_name = match.group(1)

        rest = match.group(2).strip()
        where_dict = _parse_where(rest) if rest else {}
    except ValueError as e:
        print(e)
        return

    rows = select(metadata, table_name, where_dict if where_dict else None)
    if rows is None:
        return
    _print_rows(rows)


def delete_command(metadata, user_input, args):
    usage = "Синтаксис: delete from <имя_таблицы> [where ...]"
    try:
        match = _match(r'^\s*delete\s+from\s+(\w+)(.*)$', user_input, usage)
        table_name = match.group(1)
        rest = match.group(2).strip()
        where_dict = _parse_where(rest) if rest else {}
    except ValueError as e:
        print(e)
        return

    deleted = delete(metadata, table_name, where_dict if where_dict else None)
    if deleted is None:
        return
    print(f"Удалено записей: {deleted}")


def update_command(metadata, user_input, args):
    usage = (
        "Синтаксис: update <имя_таблицы> set <столбец>=<значение> [set ...] "
        "where <столбец>=<значение> [where ...]"
    )
    try:
        match = _match(r'^\s*update\s+(\w+)(.*)$', user_input, usage)
        table_name = match.group(1)
        rest = match.group(2).strip()
        if not rest:
            raise ValueError(usage)

        set_dict = _parse_set(rest)
        where_dict = _parse_where(rest)

        if not set_dict:
            raise ValueError("Не указаны изменения. Добавьте хотя бы один 'set'.")
        if not where_dict:
            raise ValueError("Не указаны условия. Добавьте хотя бы один 'where'.")

    except ValueError as e:
        print(e)
        return

    updated = update(metadata, table_name, set_dict, where_dict)
    if updated is None:
        return
    print(f"Обновлено записей: {updated}")


def show_error_command():
    print("Неизвестная команда. Введите 'help' для справки.")


def print_help_command():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) - "
        "добавить запись"
    )
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