def apply(curs):
    print 'Creating table currency'
    curs.execute(
    '''
        CREATE TABLE currency (
            id serial,
            code varchar NOT NULL,
            cent_factor int NOT NULL,
            name varchar,
            location varchar,
            PRIMARY KEY(id),
            UNIQUE(code),
            CHECK(cent_factor > 0)
        )
    ''')


def revert(curs):
    print 'Dropping table currency'
    curs.execute('DROP TABLE IF EXISTS currency')

