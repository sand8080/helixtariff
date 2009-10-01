def apply(curs):  #IGNORE:W0622
    print 'Creating table client'
    curs.execute(
    '''
        CREATE TABLE client (
            id serial,
            login varchar NOT NULL,
            password varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(login)
        )
    ''')


def revert(curs):
    print 'Dropping table client'
    curs.execute('DROP TABLE client')

