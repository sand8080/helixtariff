def apply(curs): #IGNORE:W0622
    print 'Creating table action_log'
    curs.execute(
    '''
        CREATE TABLE action_log (
            id serial,
            client_id integer NOT NULL,
            FOREIGN KEY (client_id) REFERENCES client(id),
            source varchar,
            action varchar NOT NULL,
            request_date timestamp with time zone NOT NULL DEFAULT now(),
            request text NOT NULL,
            response text NOT NULL,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index action_log_client_id_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_client_id_idx ON action_log(client_id);
    ''')

    print 'Creating index action_log_action_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_action_idx ON action_log(action);
    ''')

    print 'Creating index action_log_client_id_action_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_client_id_action_idx ON action_log(client_id, action);
    ''')


def revert(curs):
    print 'Dropping index action_log_client_id_action_idx on action_log'
    curs.execute('DROP INDEX action_log_client_id_action_idx')

    print 'Dropping index action_log_action_idx on action_log'
    curs.execute('DROP INDEX action_log_action_idx')

    print 'Dropping index action_log_client_id_idx on action_log'
    curs.execute('DROP INDEX action_log_client_id_idx')

    print 'Dropping table action_log'
    curs.execute('DROP TABLE action_log')

