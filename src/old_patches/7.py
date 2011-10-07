def apply(curs): #IGNORE:W0622
    print 'Creating table rule'
    curs.execute(
    '''
        CREATE TABLE rule (
            id serial,
            PRIMARY KEY(id),
            operator_id integer NOT NULL,
            FOREIGN KEY (operator_id) REFERENCES operator(id),
            tariff_id integer NOT NULL,
            FOREIGN KEY (tariff_id) REFERENCES tariff(id),
            service_type_id integer NOT NULL,
            FOREIGN KEY (service_type_id) REFERENCES service_type(id),
            rule varchar NOT NULL,
            type varchar NOT NULL CHECK (type in ('actual', 'draft')),
            enabled bool
        )
    ''')
    print 'Creating index on rule (service_type_id)'
    curs.execute('CREATE INDEX rule_service_type_id_idx ON rule (service_type_id)')

    print 'Creating index on rule (tariff_id)'
    curs.execute('CREATE INDEX rule_tariff_id_idx ON rule (tariff_id)')

    print 'Creating index on rule (tariff_id, service_type_id)'
    curs.execute('CREATE INDEX rule_tariff_id_service_type_id_idx ON rule (tariff_id, service_type_id)')

    print 'Creating unique index on rule (tariff_id, service_type_id, type)'
    curs.execute('CREATE UNIQUE INDEX rule_tariff_id_service_type_id_type_idx ON rule (tariff_id, service_type_id, type)')

def revert(curs):
    print 'Dropping unique index on rule (tariff_id, service_type_id, type)'
    curs.execute('DROP INDEX rule_tariff_id_service_type_id_type_idx')

    print 'Dropping index on rule (tariff_id, service_type_id)'
    curs.execute('DROP INDEX rule_tariff_id_service_type_id_idx')

    print 'Dropping index on rule (tariff_id)'
    curs.execute('DROP INDEX rule_tariff_id_idx')

    print 'Dropping index on rule (service_type_id)'
    curs.execute('DROP INDEX rule_service_type_id_idx')

    print 'Dropping table rule'
    curs.execute('DROP TABLE rule')

