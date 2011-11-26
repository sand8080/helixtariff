def apply(curs):
    print 'Creating table user_tariff'
    curs.execute(
    '''
        CREATE TABLE user_tariff (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            tariff_id integer NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariff(id),
            user_id integer NOT NULL
        )
    ''')

    print 'Creating index user_tariff_environment_id_idx on user_tariff (environment_id)'
    curs.execute(
    '''
        CREATE INDEX user_tariff_environment_id_idx ON user_tariff (environment_id)
    '''
    )

    print 'Creating index user_tariff_environment_id_tariff_id_idx on user_tariff (environment_id, tariff_id)'
    curs.execute(
    '''
        CREATE INDEX user_tariff_environment_id_tariff_id_idx ON user_tariff (environment_id, tariff_id)
    '''
    )

    print 'Creating unique index user_tariff_environment_id_tariff_id_user_id_idx on ' \
        'user_tariff (environment_id, tariff_id, user_id)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX user_tariff_environment_id_tariff_id_user_id_idx ON
        user_tariff (environment_id, tariff_id, user_id)
    '''
    )

def revert(curs):
    print 'Dropping unique index user_tariff_environment_id_tariff_id_user_id_idx on user_tariff'
    curs.execute('DROP INDEX IF EXISTS user_tariff_environment_id_tariff_id_user_id_idx')

    print 'Dropping index user_tariff_environment_id_tariff_id_idx on user_tariff'
    curs.execute('DROP INDEX IF EXISTS user_tariff_environment_id_tariff_id_idx')

    print 'Dropping index user_tariff_environment_id_idx on user_tariff'
    curs.execute('DROP INDEX IF EXISTS user_tariff_environment_id_idx')

    print 'Dropping table user_tariff'
    curs.execute('DROP TABLE IF EXISTS user_tariff')
