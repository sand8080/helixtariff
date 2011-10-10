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

    print 'Creating unique index tariffication_object_environment_id_name_idx on tariffication_object'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tariffication_object_environment_id_name_idx ON
            tariffication_object(environment_id, name)
    ''')


def revert(curs):
    print 'Creating unique index tariffication_object_environment_id_name_idx on tariffication_object'
    curs.execute('DROP INDEX tariffication_object_environment_id_name_idx')

    print 'Dropping table tariffication_object'
    curs.execute('DROP TABLE tariffication_object')

