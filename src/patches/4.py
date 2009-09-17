def apply(curs):
    print 'Creating table service_set'
    curs.execute(
    '''
        CREATE TABLE service_set (
            id serial,
            PRIMARY KEY(id),
            service_type_id integer NOT NULL,
            FOREIGN KEY (service_type_id) REFERENCES service_type(id),
            service_set_descr_id integer NOT NULL,
            FOREIGN KEY (service_set_descr_id) REFERENCES service_set_descr(id)
        )
    ''')
    print 'Creating unique index on service_set (service_type_id, service_set_descr_id)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_set_service_type_id_service_set_descr_id_idx ON service_set (service_type_id, service_set_descr_id)
    '''
    )

def revert(curs):
    print 'Dropping unique index on service_set (service_type_id, service_set_descr_id)'
    curs.execute('DROP INDEX service_set_service_type_id_service_set_descr_id_idx')
    print 'Dropping table service_set'
    curs.execute('DROP TABLE service_set')

