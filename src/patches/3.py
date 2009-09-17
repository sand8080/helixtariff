def apply(curs):
    print 'Creating table service_set_descr'
    curs.execute(
    '''
        CREATE TABLE service_set_descr (
            id serial,
            name varchar NOT NULL,
            PRIMARY KEY(id)
        )
    ''')
    print 'Creating unique index on service_set_descr name'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_set_descr_name_idx ON service_set_descr (name)
    '''
    )

def revert(curs):
    print 'Dropping unique index on service_set_descr name'
    curs.execute('DROP INDEX service_set_descr_name_idx')
    print 'Dropping table service_set_descr'
    curs.execute('DROP TABLE service_set_descr')

