from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    Boolean,
    ForeignKey,
)
from sqlalchemy.sql.sqltypes import UnicodeText


def get_field_table(meta):
    fg = Table("field_group", meta, autoload=True)
    ft = Table("field_type", meta, autoload=True)

    return Table(
        "field",
        meta,
        Column("id", Integer, primary_key=True),
        Column("field_group_id", Integer, ForeignKey(fg.c.id), index=True, nullable=False),
        Column("order", Integer),
        Column("field_type_id", Integer, ForeignKey(ft.c.id), index=True, nullable=False),
        Column("field_name", NVARCHAR(200)),
        Column("label", NVARCHAR(200)),
        Column("required", Boolean),
        Column("max_length", Integer),
        Column("default", NVARCHAR(200)),
        Column("choices", NVARCHAR(500)),
        Column("allowed_file_extensions", NVARCHAR(200)),
        Column("download_filename_format", NVARCHAR(200)),
        Column("validation_regex", NVARCHAR(500)),
        Column("description", UnicodeText),
    )


def get_field_group_table(meta):
    return Table(
        "field_group",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(200)),
    )


def get_field_type_table(meta):
    return Table(
        "field_type",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(200)),
        Column("is_file", Boolean),
    )


def create_dynamic_form_tables(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    get_field_type_table(meta).create()
    get_field_group_table(meta).create()
    get_field_table(meta).create()


def drop_security_tables(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    Table("field", meta, autoload=True).drop()
    Table("field_group", meta, autoload=True).drop()
    Table("field_type", meta, autoload=True).drop()
