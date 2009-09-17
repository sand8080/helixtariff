def apply(curs):  #IGNORE:W0622
    print 'Creating table service_type'
    curs.execute(
    '''
        CREATE TABLE service_type (
            id serial,
            name varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(name)
        )
    ''')

def revert(curs):
    print 'Dropping table service_type'
    curs.execute('DROP TABLE service_type')

