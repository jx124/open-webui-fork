"""Peewee migrations -- 022_add_evaluation_and_class.py.

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
    
    User = migrator.orm["user"]
    Prompt = migrator.orm["prompt"]

    @migrator.create_model
    class Evaluation(pw.Model):
        title = pw.CharField(null=False, unique=True)
        content = pw.TextField(default="")

        class Meta:
            table_name = "evaluation"

    @migrator.create_model
    class Class(pw.Model):
        name = pw.CharField(null=False, unique=True)
        instructor_id = pw.ForeignKeyField(User, field=User.id)

        class Meta:
            table_name = "class"

    @migrator.create_model
    class StudentClass(pw.Model):
        student_id = pw.ForeignKeyField(User, field=User.id)
        class_id = pw.ForeignKeyField(Class)

        class Meta:
            table_name = "studentclass"

    @migrator.create_model
    class ClassPrompt(pw.Model):
        class_id = pw.ForeignKeyField(Class)
        prompt_id = pw.ForeignKeyField(Prompt)

        class Meta:
            table_name = "classprompt"

def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""

    migrator.remove_model("evaluation")
    migrator.remove_model("class")
    migrator.remove_model("studentclass")
    migrator.remove_model("classprompt")

