from datetime import timedelta


def get_jst_config(signing_key):
    return {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
        'ROTATE_REFRESH_TOKENS': False,
        'BLACKLIST_AFTER_ROTATION': False,
        'UPDATE_LAST_LOGIN': False,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': signing_key,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    }
