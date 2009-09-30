def apply(curs): #IGNORE:W0622
    print 'Creating table rule'
    curs.execute(
    '''
        CREATE TABLE rule (
            id serial,
            PRIMARY KEY(id),
            tariff_id integer NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariff(id),
            service_type_id integer NOT NULL,
            FOREIGN KEY (service_type_id) REFERENCES service_type(id),
            rule VARCHAR NOT NULL
        )
    ''')
    print 'Creating unique index on rule (tariff_id, service_type_id)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tariff_id_service_type_id_idx ON rule (tariff_id, service_type_id)
    '''
    )

def revert(curs):
    print 'Dropping unique index on rule (tariff_id, service_type_id)'
    curs.execute('DROP INDEX tariff_id_service_type_id_idx')
    print 'Dropping table rule'
    curs.execute('DROP TABLE rule')

