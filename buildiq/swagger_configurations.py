
def get_swagger_config():
    return {
        'SECURITY_DEFINITIONS': {
            'basic': {
                'type': 'basic'
            }
        },
        'exclude_url_names': [],
        'exclude_namespaces': [],
        'api_version': '0.5',
        'api_path': '/terst',
        'relative_paths': True,
        'enabled_methods': [
            'post',
            'put',
            'patch',
            'delete'
        ],
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
        'is_authenticated': True,
        'is_superuser': False,
        'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
        'permission_denied_handler': None,
        'resource_access_handler': None,
        'doc_expansion': 'none',
    }
