from primitive_db.utils import delete_table_data, load_table_data, save_table_data

reserved_id_column = "__ID"

def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f"Table '{table_name}' already exists.")
    
    table = {"columns": {reserved_id_column:"int"}}

    table_columns = table["columns"]

    for column in columns:
        result = column.split(":")
        if len(result) != 2:
            raise ValueError(f"Invalid column definition: {column}. Expected format 'name:type'.")
        
        c_name, c_type = result

        if c_name == reserved_id_column:
            raise ValueError("Column name 'ID' is reserved.")
        
        if c_name in table_columns:
            raise ValueError(f"Column '{c_name}' already exists in table '{table_name}'.")

        if c_type == "int" or c_type == "str" or c_type == "bool":
            table_columns[c_name] = c_type
        else:
            raise ValueError(f"Unsupported column type: {c_type}")

    metadata[table_name] = table


def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    del metadata[table_name]
    delete_table_data(table_name)


def insert(metadata, table_name, row_data):
    if table_name not in metadata:
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    table = metadata[table_name]
    columns = table["columns"]
    
    if len(row_data) != len(columns) - 1: # -1 because of reserved ID column
        raise ValueError("Row data does not match table columns.")

    row = {}
    for idx, (column_name, column_type) in enumerate(columns.items()):
        if column_name == reserved_id_column:
            continue

        value = row_data[idx-1]  # -1 because of reserved ID column

        if column_type == "int":
            try:
                row[column_name] = int(value)
            except ValueError:
                raise ValueError(f"Invalid value for column '{column_name}': expected int.")
        elif column_type == "str":
            row[column_name] = str(value)
        elif column_type == "bool":
            if value.lower() in ("true", "1"):
                row[column_name] = True
            elif value.lower() in ("false", "0"):
                row[column_name] = False
            else:
                raise ValueError(f"Invalid value for column '{column_name}': expected bool.")
        else:
            raise ValueError(f"Unsupported column type: {column_type}")

    table_data = load_table_data(table_name)

    new_id = len(table_data) + 1
    row[reserved_id_column] = new_id
    table_data[new_id] = row

    save_table_data(table_name, table_data)


def select(table_data, where_clause=None):
    pass


def update(table_data, set_clause, where_clause):
    pass


def delete(table_data, where_clause):
    pass