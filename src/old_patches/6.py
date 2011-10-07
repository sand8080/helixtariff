def apply(curs): #IGNORE:W0622
    print 'Creating table tariff'
    curs.execute(
    '''
        CREATE TABLE tariff (
            id serial,
            PRIMARY KEY(id),
            parent_id integer,
            FOREIGN KEY (parent_id) REFERENCES tariff(id),
            service_set_id integer NOT NULL,
            FOREIGN KEY (service_set_id) REFERENCES service_set(id),
            operator_id integer NOT NULL,
            FOREIGN KEY (operator_id) REFERENCES operator(id),
            name varchar NOT NULL,
            in_archive boolean DEFAULT FALSE
        )
    ''')
    print 'Creating unique index on tariff (operator_id, name)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tariff_operator_id_name_idx ON tariff (operator_id, name)
    '''
    )
    print 'Creating index on tariff (parent_id)'
    curs.execute(
    '''
        CREATE INDEX tariff_parent_id_idx ON tariff (parent_id)
    '''
    )

def revert(curs):
    print 'Dropping index on tariff (parent_id)'
    curs.execute('DROP INDEX tariff_parent_id_idx')
    print 'Dropping unique index on tariff (operator_id, name)'
    curs.execute('DROP INDEX tariff_operator_id_name_idx')
    print 'Dropping table tariff'
    curs.execute('DROP TABLE tariff')

