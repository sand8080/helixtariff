def apply(curs):
    print 'Creating table tarification_object'
    curs.execute(
    '''
        CREATE TABLE tarification_object (
            id serial,
            environment_id integer NOT NULL,
            name varchar NOT NULL,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating unique index tarification_object_environment_id_name_idx on tarification_object'
    curs.execute(
    '''
        CREATE UNIQUE INDEX tarification_object_environment_id_name_idx ON
            tarification_object(environment_id, name)
    ''')


def revert(curs):
    print 'Creating unique index tarification_object_environment_id_name_idx on tarification_object'
    curs.execute('DROP INDEX tarification_object_environment_id_name_idx')

    print 'Dropping table tarification_object'
    curs.execute('DROP TABLE tarification_object')

