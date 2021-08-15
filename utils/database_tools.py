from functools import wraps
from typing import List

from sqlalchemy import Column, String, Integer, Boolean, BigInteger, null, Table, ForeignKey, ForeignKeyConstraint, and_, or_
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship

from utils.tools import convert_to_bool

Base = declarative_base()


def none_as_null(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Replace None as null()
        """
        func(self, *args, **kwargs)
        for k, v in self.__dict__.items():
            if v is None:
                setattr(self, k, null())

    return wrapper


def get_table_schema_name(table: DeclarativeMeta) -> str:
    return getattr(table, "__name__", None)


def get_table_columns(table: Table) -> List[Column]:
    return table.columns._all_columns


def get_table_column_names(table: Table) -> List[str]:
    columns = get_table_columns(table=table)
    return [column.name for column in columns]


def table_schema_to_name_type_pairs(table: Table):
    columns = get_table_columns(table=table)
    pairs = {}
    ignore_columns = getattr(table, "_ignore", [])
    for column in columns:
        if column not in ignore_columns:
            pairs[column.name] = sql_type_to_human_type_string(column.type)
    return pairs


def sql_type_to_human_type_string(sql_type) -> str:
    if not hasattr(sql_type, "python_type"):
        return ""

    python_type = sql_type.python_type
    if python_type == str:
        return "String"
    elif python_type in [int, float]:
        return "Number"
    elif python_type == bool:
        return "True/False"
    return ""


def human_type_to_python_type(human_type: str):
    try:
        return float(human_type)  # is it a float?
    except:
        try:
            return int(human_type)  # is it an int?
        except:
            bool_value = convert_to_bool(bool_string=human_type)
            if bool_value is not None:  # is is a boolean?
                return bool_value
            else:
                return human_type  # it's a string
