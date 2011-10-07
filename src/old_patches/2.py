def apply(curs):
    print 'Creating table operator'
    curs.execute(
    '''
        CREATE TABLE operator (
            id serial,
            login varchar NOT NULL,
            password varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(login)
        )
    ''')


def revert(curs):
    print 'Dropping table operator'
    curs.execute('DROP TABLE operator')

