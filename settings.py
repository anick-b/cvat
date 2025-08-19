from cvat.settings.production import *

# add custom apps here
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, NestedActiveDirectoryGroupType, LDAPGroupQuery

IAM_TYPE = 'LDAP'
AUTH_LOGIN_NOTE = '''<p>
    For successful login please make sure you are member of one of the authorized groups:<br/>
    - ITS-NPR-EDGEAI-EAIP-ADMIN (Platform Administrator)<br/>
    - ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER (Organization Maintainer)<br/>
    - ITS-NPR-EDGEAI-AICOMODO-ENDUSER (Organization Supervisor/Worker)
</p>'''

# Baseline configuration - using OpenLDAP container IP on ldap-net network
AUTH_LDAP_SERVER_URI = "ldap://172.21.0.3:389"
#base path
_BASE_PATH="dc=example,dc=org"
# Credentials for LDAP server - using admin account for now
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=org"
AUTH_LDAP_BIND_PASSWORD = "newadminpass"

# User search - using uid instead of sAMAccountName for local LDAP
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=org", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# Group search - using local group structure
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=Security,ou=IDM,ou=Groups,dc=example,dc=org", ldap.SCOPE_SUBTREE,"(objectClass=*)")
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

# Require users to be members of one of the authorized groups
AUTH_LDAP_REQUIRE_GROUP = (
    LDAPGroupQuery('cn=ITS-NPR-EDGEAI-EAIP-ADMIN,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org')
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


# Enable HTTPS-aware settings
#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Optional: allow all for testing (tighten this in production)
CSRF_TRUSTED_ORIGINS = ['https://localhost']

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS += ['django_auth_ldap.backend.LDAPBackend']

# Map AD groups to CVAT roles according to requirements:
# 1. ITS-NPR-EDGEAI-EAIP-ADMIN: Platform level admin
#    - Can create/register new organizations
#    - Can create/add new business owner users (maintainers)
#    - Can add S3 buckets to organizations
#    - No visibility to projects/tasks for data privacy
#    - Can only invite "Maintainer" role users
AUTH_LDAP_ADMIN_GROUPS = [
    'cn=ITS-NPR-EDGEAI-EAIP-ADMIN,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]

# 2. ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER: Organization level maintainer
#    - Can create users with "Supervisor" and "Worker" privileges
#    - Can add S3 buckets for their organization
#    - Can create projects, assign tasks, run auto-annotation
#    - Can annotate and approve work
#    - Cannot create other "Maintainer" users (only Platform Admin can)
AUTH_LDAP_BUSINESS_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-BUSINESSOWNER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]

# 3. ITS-NPR-EDGEAI-AICOMODO-ENDUSER: Organization level supervisor/worker
#    - Supervisors: Can create projects, assign tasks, approve work
#    - Workers: Can only see assigned tasks/jobs and annotate
#    - No organization-level privileges (user creation, etc.)
AUTH_LDAP_USER_GROUPS = [
    'cn=ITS-NPR-EDGEAI-AICOMODO-ENDUSER,ou=Security,ou=IDM,ou=Groups,dc=example,dc=org',
]

# Map LDAP groups to CVAT internal roles
# Note: Both user and worker roles map to the same AD group (ENDUSER)
# The specific role assignment (supervisor vs worker) is handled at the organization level
DJANGO_AUTH_LDAP_GROUPS = {
        "admin": AUTH_LDAP_ADMIN_GROUPS,        # Platform Administrator
        "business": AUTH_LDAP_BUSINESS_GROUPS,  # Organization Maintainer
        "user": AUTH_LDAP_USER_GROUPS,          # Organization Supervisor
        "worker": AUTH_LDAP_USER_GROUPS,        # Organization Worker
        }
