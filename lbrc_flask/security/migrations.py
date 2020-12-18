from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    DateTime,
    NVARCHAR,
    Boolean,
    ForeignKey,
)


def get_user_table(meta):
    return Table(
        "user",
        meta,
        Column("id", Integer, primary_key=True),
        Column("email", NVARCHAR(255), unique=True),
        Column("password", NVARCHAR(255)),
        Column("first_name", NVARCHAR(255)),
        Column("last_name", NVARCHAR(255)),
        Column("active", Boolean()),
        Column("confirmed_at", DateTime()),
        Column("last_login_at", DateTime()),
        Column("current_login_at", DateTime()),
        Column("last_login_ip", NVARCHAR(50)),
        Column("current_login_ip", NVARCHAR(50)),
        Column("login_count", Integer),
        Column("date_created", DateTime),
    )


def get_role_table(meta):
    return Table(
        "role",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100)),
        Column("description", NVARCHAR(250)),
        Column("date_created", DateTime),
    )


def get_roles_users_table(meta):
    r = Table("role", meta, autoload=True)
    u = Table("user", meta, autoload=True)
    
    return Table(
        "roles_users",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        Column("role_id", Integer, ForeignKey(r.c.id), index=True, nullable=False),
    )


def create_security_tables(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    get_user_table(meta).create()
    get_role_table(meta).create()
    get_roles_users_table(meta).create()


def drop_security_tables(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    Table("roles_users", meta, autoload=True).drop()
    Table("role", meta, autoload=True).drop()
    Table("user", meta, autoload=True).drop()


def get_audit_mixin_columns():
    return [
        Column("last_update_date", DateTime, nullable=False),
        Column("last_update_by", NVARCHAR(500), nullable=False),
        Column("created_date", DateTime, nullable=False),
        Column("created_by", NVARCHAR(500), nullable=False),
    ]
