from helixcore.security.auth import CoreAuthenticator

from helixtariff.wsgi.server import Server

def check_access(self, session_id, service_type, property):
    REGGI_USER_ID = 1
    REGGI_ENVIRONMENT_ID = 1
    return {
        'status': 'ok',
        'user_id': REGGI_USER_ID,
        'environment_id': REGGI_ENVIRONMENT_ID,
        'access': 'granted',
    }


def check_user_exist(self, session_id, user_id):
    return {'status': 'ok', 'exist': True}


if __name__ == '__main__':
    # Creating dumb authorizer
    CoreAuthenticator.check_access = check_access
    CoreAuthenticator.check_user_exist = check_user_exist

    Server.run()
