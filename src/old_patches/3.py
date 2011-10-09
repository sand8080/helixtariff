def apply(curs):
    print 'Creating table service_type'
    curs.execute(
    '''
        CREATE TABLE service_type (
            id serial,
            operator_id integer NOT NULL,
            name varchar NOT NULL,
            PRIMARY KEY(id),
            FOREIGN KEY (operator_id) REFERENCES operator(id)
        )
    ''')
    print 'Creating unique index on service_type (operator_id, name)'
    curs.execute('CREATE UNIQUE INDEX service_type_operator_id_name_idx ON service_type (operator_id, name)')


def revert(curs):
    print 'Dropping unique index on service_type (operator_id, name)'
    curs.execute('DROP INDEX service_type_operator_id_name_idx')
    print 'Dropping table service_type'
    curs.execute('DROP TABLE service_type')

