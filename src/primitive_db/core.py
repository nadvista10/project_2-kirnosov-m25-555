def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f"Table '{table_name}' already exists.")
    
    table = {"columns": {"ID":"int"}, "rows": []}

    table_columns = table["columns"]

    for column in columns:
        c_name, c_type = column.split(":")

        if c_name == "ID":
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