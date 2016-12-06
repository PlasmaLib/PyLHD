import psycopg2 as pgdb

PGDB_HOST = 'egdb.lhd.nifs.ac.jp'
PGDB_DB = 'db1'
PGDB_USER = 'guest'
PGDB_PASSWORD = ''

def load(shotnumber, keys):
    """
    A simple method to handle the data base.
    :args
    - shotnumber: shotnumber to search
    - keys: a list of strings.

    :returns
    - dict with key and its value pair.

    For valid keys, see
    http://kaiseki-dev.lhd.nifs.ac.jp/software/shotsummary/Main_new.htm
    or
    http://kaiseki-dev.lhd.nifs.ac.jp/software/shotsummary/ExpLog2_2013.html
    """
    db = pgdb.connect(host=PGDB_HOST, database=PGDB_DB, user=PGDB_USER,
                        password=PGDB_PASSWORD)
    cursor = db.cursor()

    key_string = ''
    for key in keys:
        key_string = key_string + key + ','
    cursor.execute("select " + key_string[:-1] +\
                        ' from explog2 where nshotnumber=' + str(shotnumber))
    val = {}
    row = cursor.fetchone()
    if not row:
        raise ValueError
    for i in range(len(row)):
        val[keys[i]] = row[i]
    db.close()
    return val
