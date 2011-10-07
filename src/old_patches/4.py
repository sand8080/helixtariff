def apply(curs):
    print 'Creating table service_set'
    curs.execute(
    '''
        CREATE TABLE service_set (
            id serial,
            operator_id integer NOT NULL,
            name varchar NOT NULL,
            PRIMARY KEY(id),
            FOREIGN KEY (operator_id) REFERENCES operator(id)
        )
    ''')
    print 'Creating unique index on service_set name'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_set_name_idx ON service_set (name)
    '''
    )


def revert(curs):
    print 'Dropping unique index on service_set name'
    curs.execute('DROP INDEX service_set_name_idx')
    print 'Dropping table service_set'
    curs.execute('DROP TABLE service_set')

