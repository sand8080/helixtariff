def apply(curs):  #IGNORE:W0622
    print 'Creating table service_set_name'
    curs.execute(
    '''
        CREATE TABLE service_set_name (
            id serial,
            client_id integer NOT NULL,
            name varchar NOT NULL,
            PRIMARY KEY(id),
            FOREIGN KEY (client_id) REFERENCES client(id)
        )
    ''')
    print 'Creating unique index on service_set_name name'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_set_name_name_idx ON service_set_name (name)
    '''
    )

def revert(curs):
    print 'Dropping unique index on service_set_name name'
    curs.execute('DROP INDEX service_set_name_name_idx')
    print 'Dropping table service_set_name'
    curs.execute('DROP TABLE service_set_name')

