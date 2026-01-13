from decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import (
    delete_table_data,
    load_table_data,
    save_metadata,
    save_table_data,
)

reserved_id_column = "__ID"


def _coerce_value(columns, column_name, raw_value, *, mode):
    column_type = columns[column_name]

    if mode == "condition":
        value_label = "condition value"
    else:
        value_label = "value"

    if column_type == "int":
        try:
            return int(raw_value)
        except ValueError:
            raise ValueError(
                f"Invalid {value_label} for column '{column_name}': expected int."
            )

    if column_type == "bool":
        value_str = str(raw_value).lower()
        if value_str in ("true", "1"):
            return True
        if value_str in ("false", "0"):
            return False
        raise ValueError(
            f"Invalid {value_label} for column '{column_name}': expected bool."
        )

    if column_type == "str":
        return str(raw_value)

    raise ValueError(f"Unsupported column type: {column_type}")


@handle_db_errors
@log_time
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise FileExistsError(f"Table '{table_name}' already exists.")

    table = {"columns": {reserved_id_column: "int"}}

    table_columns = table["columns"]

    for column in columns:
        result = column.split(":")
        if len(result) != 2:
            raise ValueError(
                f"Invalid column definition: {column}. Expected format 'name:type'."
            )
        
        c_name, c_type = result

        if c_name == reserved_id_column:
            raise ValueError(f"Column name '{reserved_id_column}' is reserved.")
        
        if c_name in table_columns:
            raise ValueError(
                f"Column '{c_name}' already exists in table '{table_name}'."
            )

        if c_type == "int" or c_type == "str" or c_type == "bool":
            table_columns[c_name] = c_type
        else:
            raise ValueError(f"Unsupported column type: {c_type}")

    metadata[table_name] = table
    save_metadata(metadata)


@handle_db_errors
@confirm_action("удаление таблицы")
@log_time
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(f"Table '{table_name}' does not exist.")

    del metadata[table_name]
    delete_table_data(table_name)
    save_metadata(metadata)


@handle_db_errors
@log_time
def insert(metadata, table_name, row_data):
    if table_name not in metadata:
        raise KeyError(f"Table '{table_name}' does not exist.")

    table = metadata[table_name]
    columns = table["columns"]
    
    if len(row_data) != len(columns) - 1:  # -1 because of reserved ID column
        raise ValueError("Row data does not match table columns.")

    row = {}
    for idx, (column_name, _) in enumerate(columns.items()):
        if column_name == reserved_id_column:
            continue
        value = row_data[idx - 1]  # -1 because of reserved ID column
        row[column_name] = _coerce_value(columns, column_name, value, mode="insert")

    table_data = load_table_data(table_name)

    new_id = len(table_data) + 1
    row[reserved_id_column] = new_id
    table_data[new_id] = row

    save_table_data(table_name, table_data)


@handle_db_errors
@log_time
def select(metadata, table_name, condition_dict=None):
    if table_name not in metadata:
        raise KeyError(f"Table '{table_name}' does not exist.")

    table = metadata[table_name]
    columns = table["columns"]

    if any(col not in columns for col in (condition_dict or {}).keys()):
        missing = [col for col in (condition_dict or {}).keys() if col not in columns]
        raise KeyError(f"Unknown column(s) in condition: {', '.join(missing)}")

    table_data = load_table_data(table_name)

    if not condition_dict:
        return list(table_data.values())

    results = []
    for _, row in table_data.items():
        matches = True
        for col, value in condition_dict.items():
            cond_value = _coerce_value(columns, col, value, mode="condition")
            if row[col] != cond_value:
                matches = False
                break
        if matches:
            results.append(row)
    return results
    


@handle_db_errors
@log_time
def update(metadata, table_name, set_clause, condition_dict):
    if table_name not in metadata:
        raise KeyError(f"Table '{table_name}' does not exist.")

    table = metadata[table_name]
    columns = table["columns"]

    if reserved_id_column in set_clause:
        raise PermissionError(f"Column '{reserved_id_column}' cannot be updated.")

    if any(col not in columns for col in set_clause.keys()):
        missing = [col for col in set_clause.keys() if col not in columns]
        raise KeyError(f"Unknown column(s) in SET: {', '.join(missing)}")

    if condition_dict is not None:
        if any(col not in columns for col in condition_dict.keys()):
            missing = [col for col in condition_dict.keys() if col not in columns]
            raise KeyError(f"Unknown column(s) in WHERE: {', '.join(missing)}")

    table_data = load_table_data(table_name)

    coerced_set = {
        col: _coerce_value(columns, col, val, mode="set")
        for col, val in set_clause.items()
    }
    coerced_where = None
    if condition_dict:
        coerced_where = {
            col: _coerce_value(columns, col, val, mode="condition")
            for col, val in condition_dict.items()
        }

    updated_count = 0
    for _, row in table_data.items():
        match = True
        if coerced_where:
            for col, expected in coerced_where.items():
                if row.get(col) != expected:
                    match = False
                    break
        if not match:
            continue

        for col, new_val in coerced_set.items():
            row[col] = new_val
        updated_count += 1

    save_table_data(table_name, table_data)
    return updated_count


@handle_db_errors
@confirm_action("удаление записей")
@log_time
def delete(metadata, table_name, condition_dict):
    todelete = select(metadata, table_name, condition_dict)
    if todelete is None:
        return None
    deleted_count = len(todelete)
    table_data = load_table_data(table_name)

    filtered_table = {
        row_id: row for row_id, row in table_data.items() if row not in todelete
    }
    save_table_data(table_name, filtered_table)

    return deleted_count