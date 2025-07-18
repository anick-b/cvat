from cvat.settings.production import *

# add custom apps here
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, NestedActiveDirectoryGroupType, LDAPGroupQuery

IAM_TYPE = 'LDAP'
AUTH_LOGIN_NOTE = '''<p>
    For successful login please make sure you are member of cvat_users group
</p>'''

# Baseline configuration - using host IP to reach host LDAP
AUTH_LDAP_SERVER_URI = "ldap://192.168.1.143:389"
#base path
_BASE_PATH="dc=example,dc=org"
# Credentials for LDAP server - using admin account for now
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=org"
AUTH_LDAP_BIND_PASSWORD = "admin"

# User search - using uid instead of sAMAccountName for local LDAP
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=org", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# Group search - using local group structure
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=Security,ou=IDM,ou=Groups,dc=example,dc=org", ldap.SCOPE_SUBTREE,"(objectClass=*)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_REQUIRE_GROUP = (
    LDAPGroupQuery('cn=ITS-NPR-EDGEAI-ADMIN,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org')
    | LDAPGroupQuery('cn=ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org')
    | LDAPGroupQuery('cn=ITS-NPR-EDGEAI-AICOMODO-ENDUSER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org')
)

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
AUTH_LDAP_AUTHORIZE_ALL_USERS = True

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS += ['django_auth_ldap.backend.LDAPBackend']

# Map groups to CVAT roles - using local group structure
AUTH_LDAP_ADMIN_GROUPS = [
    'cn=ITS-NPR-EDGEAI-ADMIN,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]
AUTH_LDAP_BUSINESS_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]
AUTH_LDAP_USER_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-ENDUSER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]

DJANGO_AUTH_LDAP_GROUPS = {
        "admin": AUTH_LDAP_ADMIN_GROUPS,
        "business": AUTH_LDAP_BUSINESS_GROUPS,
        "user": AUTH_LDAP_USER_GROUPS,
        "worker": AUTH_LDAP_USER_GROUPS,
        }