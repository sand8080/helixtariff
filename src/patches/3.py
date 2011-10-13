def apply(curs): #IGNORE:W0622
    print 'Creating table tariff'
    curs.execute(
    '''
        CREATE TABLE tariff (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            parent_tariff_id integer,
            FOREIGN KEY (parent_tariff_id) REFERENCES tariff(id),
            name varchar NOT NULL,
            type varchar NOT NULL CHECK(type in ('public', 'personal')),
            status varchar NOT NULL CHECK(status in ('active', 'archive', 'inactive'))
        )
    ''')

    print 'Creating index tariff_environment_id_idx on tariff (environment_id)'
    curs.execute(
    '''
        CREATE INDEX tariff_environment_id_idx ON tariff (environment_id)
    '''
    )

    print 'Creating index tariff_environment_id_name_type_idx on tariff (environment_id, name, type)'
    curs.execute(
    '''
        CREATE INDEX tariff_environment_id_name_type_idx ON tariff (environment_id, name, type)
    '''
    )

    print 'Creating index tariff_parent_tariff_id_idx on tariff (parent_tariff_id)'
    curs.execute(
    '''
        CREATE INDEX tariff_parent_tariff_id_idx ON tariff (parent_tariff_id)
    '''
    )

def revert(curs):
    print 'Dropping index tariff_parent_tariff_id_idx on tariff'
    curs.execute('DROP INDEX IF EXISTS tariff_parent_tariff_id_idx')

    print 'Dropping index tariff_environment_id_name_type_idx on tariff'
    curs.execute('DROP INDEX IF EXISTS tariff_environment_id_name_type_idx')

    print 'Dropping index tariff_environment_id_idx on tariff'
    curs.execute('DROP INDEX IF EXISTS tariff_environment_id_idx')

    print 'Dropping table tariff'
    curs.execute('DROP TABLE IF EXISTS tariff')

