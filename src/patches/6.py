def apply(curs): #IGNORE:W0622
    print 'Creating table tariff'
    curs.execute(
    '''
        CREATE TABLE tariff (
            id serial,
            PRIMARY KEY(id),
            service_set_descr_id integer NOT NULL,
            FOREIGN KEY (service_set_descr_id) REFERENCES service_set_descr(id),
            client_id integer NOT NULL,
            name varchar NOT NULL,
            in_archive boolean DEFAULT FALSE,
            FOREIGN KEY (client_id) REFERENCES client(id)
        )
    ''')
    print 'Creating unique index on tariff (client_id, name)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tariff_client_id_name_idx ON tariff (client_id, name)
    '''
    )

def revert(curs):
    print 'Dropping unique index on tariff (client_id, name)'
    curs.execute('DROP INDEX tariff_client_id_name_idx')
    print 'Dropping table tariff'
    curs.execute('DROP TABLE tariff')

