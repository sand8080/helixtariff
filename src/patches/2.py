def apply(curs):
    print 'Creating table tariffication_object'
    curs.execute(
    '''
        CREATE TABLE tariffication_object (
            id serial,
            environment_id integer NOT NULL,
            name varchar NOT NULL,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index tariffication_object_environment_id_idx on tariffication_object (environment_id)'
    curs.execute(
    '''
        CREATE INDEX tariffication_object_environment_id_idx ON tariffication_object (environment_id)
    '''
    )

    print 'Creating unique index tariffication_object_environment_id_name_idx on tariffication_object'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tariffication_object_environment_id_name_idx ON
            tariffication_object(environment_id, name)
    ''')


def revert(curs):
    print 'Creating unique index tariffication_object_environment_id_name_idx on tariffication_object'
    curs.execute('DROP INDEX IF EXISTS tariffication_object_environment_id_name_idx')

    print 'Dropping index tariffication_object_environment_id_idx on tariff'
    curs.execute('DROP INDEX IF EXISTS tariffication_object_environment_id_idx')

    print 'Dropping table tariffication_object'
    curs.execute('DROP TABLE IF EXISTS tariffication_object')

