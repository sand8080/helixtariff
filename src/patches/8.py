def apply(curs):
    print 'Creating table tariff_viewing_context'
    curs.execute(
    '''
        CREATE TABLE tariff_viewing_context (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            tariff_id integer NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariff(id),
            view_order integer DEFAULT 0,
            serialized_context varchar NOT NULL
        )
    ''')

    print 'Creating index tariff_viewing_context_environment_id_idx on tariff_viewing_context (environment_id)'
    curs.execute(
    '''
        CREATE INDEX tariff_viewing_context_environment_id_idx ON tariff_viewing_context (environment_id)
    '''
    )

    print 'Creating index tariff_viewing_context_environment_id_tariff_id_idx on tariff_viewing_context (environment_id, tariff_id)'
    curs.execute(
    '''
        CREATE INDEX tariff_viewing_context_environment_id_tariff_id_idx ON tariff_viewing_context (environment_id, tariff_id)
    '''
    )


def revert(curs):
    print 'Dropping unique index tariff_viewing_context_environment_id_idx on tariff_viewing_context'
    curs.execute('DROP INDEX IF EXISTS tariff_viewing_context_environment_id_idx')


    print 'Dropping index tariff_viewing_context_environment_id_tariff_id_idx on tariff_viewing_context'
    curs.execute('DROP INDEX IF EXISTS tariff_viewing_context_environment_id_tariff_id_idx')

    print 'Dropping table tariff_viewing_context'
    curs.execute('DROP TABLE IF EXISTS tariff_viewing_context')
