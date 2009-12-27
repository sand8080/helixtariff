def apply(curs): #IGNORE:W0622
    print 'Creating table service_set_row'
    curs.execute(
    '''
        CREATE TABLE service_set_row (
            id serial,
            PRIMARY KEY(id),
            service_type_id integer NOT NULL,
            FOREIGN KEY (service_type_id) REFERENCES service_type(id),
            service_set_id integer NOT NULL,
            FOREIGN KEY (service_set_id) REFERENCES service_set(id)
        )
    ''')
    print 'Creating unique index on service_set_row (service_type_id, service_set_id)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_set_row_service_type_id_service_set_id_idx ON
            service_set_row (service_type_id, service_set_id)
    '''
    )

def revert(curs):
    print 'Dropping unique index on service_set_row (service_type_id, service_set_id)'
    curs.execute('DROP INDEX service_set_row_service_type_id_service_set_id_idx')
    print 'Dropping table service_set_row'
    curs.execute('DROP TABLE service_set_row')

