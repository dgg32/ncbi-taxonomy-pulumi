import os
import zipfile
import pymysql
import sys
import shutil
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import rds_config

endpoint = sys.argv[1]
rds_config_file = "../rds_config.py"

name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

def zip_lambda(endpoint):
    content = ""
    
    for line in open(rds_config_file):
        content += line

    content += f'\ndb_endpoint = "{endpoint}"'


    output  = open("./lambda/rds_config.py", "w")
    output.write(content)
    output.close()

    try:
        os.remove("./lambda.zip") 
    except:
        pass
    shutil.make_archive("lambda", 'zip', root_dir = "./lambda")


def import_data(endpoint, db_username, db_password, db_name):
    

    conn = pymysql.connect(host=endpoint, user=db_username, passwd=db_password, db=db_name, connect_timeout=5, autocommit=True, local_infile=True)
    cursor = conn.cursor()

    commands = ["use pyphydb;", "CREATE TABLE IF NOT EXISTS tree (taxid integer, name varchar(250), parent integer, rank varchar(20));",
    "CREATE TABLE IF NOT EXISTS synonym (id integer, taxid integer, name varchar(250));",
    'load data local infile "tree.tsv" into table tree fields terminated by "\\t" lines terminated by "\\n" (taxid, name, parent, rank);',
    'load data local infile "synonym.tsv" into table synonym fields terminated by "\\t" lines terminated by "\\n" (id, taxid, name);',
    'CREATE UNIQUE INDEX taxid_on_tree ON tree(taxid);',
    'CREATE INDEX name_on_tree ON tree(name);',
    'CREATE INDEX name_on_synonym ON synonym(name);',
    'CREATE INDEX taxid_on_synonym ON synonym(taxid);']


    for command in commands:
        print (command)
        cursor.execute(command)


if __name__ == "__main__":
    zip_lambda(endpoint)

    import_data(endpoint, name, password, db_name)