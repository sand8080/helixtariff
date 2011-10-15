def apply(curs):
    print 'Creating table rule'
    curs.execute(
    '''
        CREATE TABLE rule (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            tariff_id integer NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariff(id),
            tariffication_object_id integer NOT NULL,
            FOREIGN KEY (tariffication_object_id) REFERENCES tariffication_object(id),
            rule varchar NULL,
            draft_rule varchar NOT NULL,
            status varchar NOT NULL CHECK (status in ('active', 'inactive'))
        )
    ''')

    print 'Creating index rule_environment_id_idx on rule (environment_id)'
    curs.execute(
    '''
        CREATE INDEX rule_environment_id_idx ON rule (environment_id)
    '''
    )

    print 'Creating index rule_environment_id_tariff_id_idx on rule (environment_id, tariff_id)'
    curs.execute(
    '''
        CREATE INDEX rule_environment_id_tariff_id_idx ON rule (environment_id, tariff_id)
    '''
    )

    print 'Creating unique index rule_environment_id_tariff_id_tariffication_object_id_idx on ' \
        'rule (environment_id, tariff_id, tariffication_object_id)'
    curs.execute(
    '''
        CREATE UNIQUE INDEX environment_id_tariff_id_tariffication_object_id_idx ON
        rule (environment_id, tariff_id, tariffication_object_id)
    '''
    )

def revert(curs):
    print 'Dropping unique index rule_environment_id_tariff_id_tariffication_object_id_idx on rule'
    curs.execute('DROP INDEX IF EXISTS rule_environment_id_tariff_id_tariffication_object_id_idx')

    print 'Dropping index rule_environment_id_tariff_id_idx on rule'
    curs.execute('DROP INDEX IF EXISTS rule_environment_id_tariff_id_idx')

    print 'Dropping table rule'
    curs.execute('DROP TABLE IF EXISTS rule')

