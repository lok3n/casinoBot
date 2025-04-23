from peewee import SqliteDatabase, TextField, IntegerField, DateTimeField, Model, ForeignKeyField

db = SqliteDatabase('database.db')


class Users(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    free_balance = IntegerField(default=5)
    balance = IntegerField(default=0)

    class Meta:
        database = db


class Payments(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    amount = IntegerField()
    date_time = DateTimeField()
    finished = IntegerField(default=0)

    class Meta:
        database = db


class Withdraws(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    amount = IntegerField()
    way = TextField()
    wallet = TextField()
    finished = IntegerField(default=0)

    class Meta:
        database = db
