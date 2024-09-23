import re
from re import Match
import json

output = []

insert_pattern = r"(INSERT)\sINTO\s([A-Z._]*)(?:[\s\S]*?);"
update_pattern = r"(UPDATE)\s([A-Z._]*)(?:[\s\S]*?);"
create_pattern = r"(CREATE)\sOR\sREPLACE\sTEMPORARY\sTABLE\s([A-Z._]*)(?:[\s\S]*?);"
select_pattern = r"(SELECT)[\S\s]*?(FROM)\s([A-Z_.]*)"
join_pattern = r"(JOIN)\s([A-Z_.]*)"

with open("./sample_stored_procedure.sql") as file:
    sql_data = file.read()

insert_compiled = re.compile(insert_pattern)
update_compiled = re.compile(update_pattern)
create_compiled = re.compile(create_pattern)

def extract_table_info(statement_id: int, statement_type: str, statement: Match) -> dict:
    data = {"statement_id": statement_id}
    data["table_name"] = []

    data["statement_type"] = statement_type
    data["table_name"].append({"target_table_name": statement.group(2)})
    
    select_compiled = re.compile(select_pattern)
    join_compiled = re.compile(join_pattern)

    for select_stmt in select_compiled.finditer(statement.group(0)):
        if not select_stmt.group(3):
            continue
        data["table_name"].append({
            "type": select_stmt.group(2),
            "source_table_name": select_stmt.group(3)
        })

    for join_stmt in join_compiled.finditer(statement.group(0)):
        if not join_stmt.group(2):
            continue
        data["table_name"].append({
            "type": join_stmt.group(1),
            "source_table_name": join_stmt.group(2)
        })

    return data

statement_id = 1

for insert_stmt in insert_compiled.finditer(sql_data):
    output.append(extract_table_info(statement_id, insert_stmt.group(1), insert_stmt))
    statement_id += 1

for update_stmt in update_compiled.finditer(sql_data):
    output.append(extract_table_info(statement_id, update_stmt.group(1), update_stmt))
    statement_id += 1

for create_stmt in create_compiled.finditer(sql_data):
    output.append(extract_table_info(statement_id, create_stmt.group(1), create_stmt))
    statement_id += 1

with open("./output.json", "w") as output_file:
    json.dump(output, output_file)
