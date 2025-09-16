from cvat.settings.production import *

# add custom apps here
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, NestedActiveDirectoryGroupType, LDAPGroupQuery

IAM_TYPE = 'LDAP'
AUTH_LOGIN_NOTE = '''<p>
    For successful login please make sure you are member of cvat_users group
</p>'''

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://jnjdir.jnj.com:3268"
#base path
_BASE_PATH="DC=jnj,DC=com"
# Credentials for LDAP server
AUTH_LDAP_BIND_DN = "JNJ-AICOMODOSA_LDAP"
AUTH_LDAP_BIND_PASSWORD = "Newjersey@123"

AUTH_LDAP_USER_SEARCH = LDAPSearch(_BASE_PATH, ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com", ldap.SCOPE_SUBTREE,"(objectClass=*)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_REQUIRE_GROUP = (
    LDAPGroupQuery('CN=ITS-NPR-EDGEAI-ADMIN,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com')
    | LDAPGroupQuery('cn=ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com')
    | LDAPGroupQuery('cn=ITS-NPR-EDGEAI-AICOMODO-ENDUSER,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com')
)

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_staff": "cn=cvat_admin,ou=suborg1,dc=test,dc=outdu,dc=org",
#    "is_superuser": "cn=cvat_admin,ou=suborg1,dc=test,dc=outdu,dc=org",
#}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
AUTH_LDAP_AUTHORIZE_ALL_USERS = True

#AUTH_LDAP_MIRROR_GROUPS = True

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS += ['django_auth_ldap.backend.LDAPBackend']

# example 'cn=cvat_admin,cn=groups,cn=accounts,dc=example,dc=com'
# change your cn to match whatever groups you have in your LDAP
AUTH_LDAP_ADMIN_GROUPS = [
    'CN=ITS-NPR-EDGEAI-ADMIN,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com',
]
AUTH_LDAP_BUSINESS_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com',
]
AUTH_LDAP_USER_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-ENDUSER,OU=Security,OU=IDM,OU=Groups,DC=jnj,DC=com',
]

DJANGO_AUTH_LDAP_GROUPS = {
        "admin": AUTH_LDAP_ADMIN_GROUPS,
        "business": AUTH_LDAP_BUSINESS_GROUPS,
        "user": AUTH_LDAP_USER_GROUPS,
        "worker": AUTH_LDAP_USER_GROUPS,
        }