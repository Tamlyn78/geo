#!/usr/bin/env python

"""PostgreSQL wrapper methods.

This modules provides methods for PostgreSQL databse operations.

"""

import os
import sys
import psycopg2
import subprocess
from datetime import datetime
import tempfile
import shutil
from getpass import getpass

def connect(host='localhost', port=5432, dbname='postgres', user='postgres', password=None):
    """"""
    try:
        con = None
        if not password:
            password = getpass('Enter postgresql password: ')
        con = psycopg2.connect(host = host, database = dbname, user = user, password = password, port = port)
        con.autocommit = True
        return(con)
    except psycopg2.Error as e:
        print(e)
        sys.exit()

def check_database(con, dbname):
    """Check a database exists in a given connection"""
    cur = con.cursor()
    sql = """SELECT 0 FROM pg_database WHERE datname = '%s'"""
    cur.execute(sql % dbname)
    result = cur.fetchall()
    if result:
        return(True)
    else:
        return(False)
        
def create_database(con, dbname):
    """Create a database"""
    try:
        cur = con.cursor()
        cur.execute('CREATE DATABASE ' + dbname)
        cur.close()
    except psycopg2.Error as e:
        print(e)
        
def csv2pg(cur, file_object, table, schema = "public"):
    """Copy csv data to a postgreSQL table"""
    sql = """COPY %s FROM STDIN WITH CSV HEADER DELIMITER AS ','"""
    try:
        cur.copy_expert("COPY %s FROM STDIN WITH CSV HEADER" % (schema + '.' + table), file_object, size = 8192)
    except psycopg2.Error as e:
        print(e.pgerror)
        sys.exit(1)
    finally:
        cur.close()
        
def pg2csv(cur, file_object, table, schema = "public", sql = None):
    """Copy PostgreSQL table to csv; direct copy fails because of permissions in Linux so copy first to a temporary file"""
    try:
        if not sql:
            sql = """SELECT * FROM """ + schema + """.""" + table
        cur.copy_expert("""COPY (""" + sql + """) TO STDOUT CSV HEADER""", file_object, size = 8192)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        
def pg2dic(cur, sql):
    """Return a dictionary of the results of an sql query"""
    try:
        cur.execute(sql)
        h = [i[0] for i in cur.description]
        d = cur.fetchall()
        dic = {}
        for key in h:
            idx = [n for n, i in enumerate(h) if i == key][0] 
            lst = []
            for row in d:
                value = row[idx]
                lst += [value]

            dic[key] = lst
        return(dic)
    except psycopg2.Error as e:
        print(e.pgerror)
        sys.exit(1)
    
def pg_dump(dbname='postgres', host='localhost', port = 5432, dbuser='postgres', outpath=None, format='c'):
    """"""
    try:
        print('wee')
        subprocess.call(['pg_dump', "--host", host, "--port", str(port), "--file", outpath, "--format", format, "--no-owner", "--username", dbuser, dbname], shell = False)
        print('poo')
    except Exception as e:
        print(e)
    
def pg_restore(host, dbuser, dbname, format, inpath, port = 5432):
    """"""
    try:
        subprocess.call(["pg_restore", "--host", host, "--port", str(port), "--username", dbuser, "--dbname", dbname, "--format", format, inpath], shell = False)
    except Exception as e:
        print(e)
    
 
def pg_dumpnew():
    from optparse import OptionParser
    from datetime import datetime
    
    parser = OptionParser()
    parser.add_option('-t', '--type', dest='backup_type',
                      help="Specify either 'hourly' or 'daily'.")

    now = datetime.now()

    filename = None
    (options, args) = parser.parse_args()
    if options.backup_type == 'hourly':
        hour = str(now.hour).zfill(2)
        filename = '%s.h%s' % (FILENAME_PREFIX, hour)
    elif options.backup_type == 'daily':
        day_of_year = str(now.timetuple().tm_yday).zfill(3)
        filename = '%s.d%s' % (FILENAME_PREFIX, day_of_year)
    else:
        parser.error('Invalid argument.')
        sys.exit(1)

    destination = r'%s/%s' % (BACKUP_PATH, filename)
        

