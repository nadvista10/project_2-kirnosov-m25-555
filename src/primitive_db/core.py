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


def select(metadata, table_name, condition_dict=None):
    if table_name not in metadata:
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    table = metadata[table_name]
    columns = table["columns"]

    if any(col not in columns for col in (condition_dict or {}).keys()):
        raise ValueError("One or more columns in the condition do not exist in the table.")

    table_data = load_table_data(table_name)

    if not condition_dict:
        return list(table_data.values())

    results = []
    for id, row in table_data.items():
        all = True
        for col, value in condition_dict.items():
            if columns[col] == "int":
                try:
                    cond_value = int(value)
                except ValueError:
                    raise ValueError(f"Invalid condition value for column '{col}': expected int.")
            elif columns[col] == "bool":
                if value.lower() in ("true", "1"):
                    cond_value = True
                elif value.lower() in ("false", "0"):
                    cond_value = False
                else:
                    raise ValueError(f"Invalid condition value for column '{col}': expected bool.")
            elif columns[col] == "str":
                cond_value = str(value)
            else:
                raise ValueError(f"Unsupported column type: {columns[col]}")
            
            if row[col] != cond_value:
                all = False
                break
        if all:
            results.append(row)
    return results  
    

def update(metadata, table_name, set_clause, condition_dict):
    pass


def delete(metadata, table_name, condition_dict):
    todelete = select(metadata, table_name, condition_dict)
    deleted_count = len(todelete)
    table_data = load_table_data(table_name)

    filtered_table = {id: row for id, row in table_data.items() if row not in todelete}
    save_table_data(table_name, filtered_table)

    return deleted_count