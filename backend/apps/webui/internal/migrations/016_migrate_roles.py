"""Peewee migrations -- 016_migrate_roles.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator

with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""

    Role = migrator.orm["role"]

    Role.create(name="pending")
    Role.create(name="admin")
    Role.create(name="user")

    migrate_roles_to_table(migrator, database)

def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.add_fields("user", role=pw.CharField(max_length=255))

    migrator.sql('UPDATE "user" SET role = subquery.rolename '
                 'FROM (SELECT "user".id AS userid, "role".name AS rolename FROM "user" JOIN "role" ON "user".role_id = "role".id) '
                 'AS subquery WHERE "user".id = subquery.userid;')

    migrator.remove_fields("user", "role_id")

def migrate_roles_to_table(migrator: Migrator, database: pw.Database):
    Role = migrator.orm["role"]
    
    migrator.add_fields("user", role_id=pw.ForeignKeyField(Role, backref="users", default=1))

    migrator.sql('UPDATE "user" SET role_id = subquery.roleid '
                 'FROM (SELECT "user".id AS userid, "role".id AS roleid FROM "user" JOIN "role" ON "user".role = "role".name) '
                 'AS subquery WHERE "user".id = subquery.userid;')
    
    migrator.remove_fields("user", "role")
