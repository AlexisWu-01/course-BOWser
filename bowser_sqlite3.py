

import sqlite3
import configparser
import os

# got this code from pymsql/optionfile.py


def connect(file):
    '''Returns a new database connection given the dsn (a dictionary). The
default is to use cache_cnf('~/.my.cnf')

    The database connection is not set to automatically commit.

    '''
    try:
        conn = sqlite3.connect(file)
    except sqlite3.Error as e:
        print("Couldn't connect to database")
    return conn


def select_db(conn,db):
    '''This function isn't necessary; just use the select_db() method
on the connection.'''
    raise Exception('cannot select a different database in SQLite3')

def cursor(conn):
    '''Returns a cursor where rows are represented as tuples.'''
    return conn.cursor()

# Follows this
# https://docs.python.org/3/library/sqlite3.html#accessing-columns-by-name-instead-of-by-index

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def dict_cursor(conn):
    '''Returns a cursor where rows are represented as dictionaries.'''
    conn.row_factory = dict_factory
    return conn.cursor()
