package projects

import rego.v1

import data.utils
import data.organizations

# input: {
#     "scope": <"create"|"list"|"update:desc"|"update:owner"|"update:assignee"|
#               "update:associated_storage"|"view"|"delete"|"export:dataset"|"export:annotations"|
#               "import:dataset"> or null,
#     "auth": {
#         "user": {
#             "id": <num>,
#             "privilege": <"admin"|"user"|"worker"> or null
#         },
#         "organization": {
#             "id": <num>,
#             "owner": {
#                 "id": <num>
#             },
#             "user": {
#                 "role": <"owner"|"maintainer"|"supervisor"|"worker"> or null
#             }
#         } or null,
#     },
#     "resource": {
#         "id": <num>,
#         "owner": { "id": <num> },
#         "assignee": { "id": <num> },
#         "organization": { "id": <num> } or null,
#         "rq_job": { "owner": { "id": <num> } } or null,
#     }
# }

default allow := false

is_project_staff if {
    utils.is_resource_owner
}

is_project_staff if {
    utils.is_resource_assignee
}

                                                                 #Comment lines to disable Admin
#allow if {
#    utils.is_admin
#}

                                                                 #Comment: USER cannot create a project/backup
#allow if {
#    input.scope in {utils.CREATE, utils.IMPORT_BACKUP}
#    utils.is_sandbox
#    utils.has_perm(utils.USER)
#}

allow if {
    input.scope in {utils.CREATE, utils.IMPORT_BACKUP}
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.has_perm(organizations.SUPERVISOR)
    not utils.is_admin                                          # Added to deny Admin
}
                                                                # Added so BUSINESS user with MAINTAINER role can create project/backup
allow if {
    input.scope in { utils.CREATE, utils.IMPORT_BACKUP }[input.scope]
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.BUSINESS)
    organizations.has_perm(organizations.MAINTAINER)
    not utils.is_admin
}

                                                                #Comment to disable sandbox

#allow if {
#    input.scope == utils.LIST
#    utils.is_sandbox
#}

allow if {
    input.scope == utils.LIST
    organizations.is_member
    input.auth.organization.user.role != organizations.OWNER     #Added - Deny admin to see list of projects etc.
}

filter := [] if { # Django Q object to filter list of entries
#    utils.is_admin                     #Comment- verify
    utils.is_sandbox
} else := qobject if {
#    utils.is_admin                     #Comment- verify
    utils.is_organization
    qobject := [ {"organization": input.auth.organization.id} ]
} else := qobject if {
    utils.is_sandbox
    user := input.auth.user
    qobject := [ {"owner_id": user.id}, {"assignee_id": user.id}, "|" ]
} else := qobject if {
    utils.is_organization
    utils.has_perm(utils.USER)
    organizations.has_perm(organizations.MAINTAINER)
    qobject := [ {"organization": input.auth.organization.id} ]
} else := qobject if {
    organizations.has_perm(organizations.WORKER)
    user := input.auth.user
    qobject := [ {"owner_id": user.id}, {"assignee_id": user.id}, "|",
        {"organization": input.auth.organization.id}, "&" ]
}
                                                            #Comment- Deny view + sandbox
#allow if {
#    input.scope == utils.VIEW
#    utils.is_sandbox
#    is_project_staff
#}

allow if {
    input.scope == utils.VIEW
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.BUSINESS)                         #Modified- Give BUSINESS group view access
    organizations.has_perm(organizations.MAINTAINER)
}
                                                            #Added- Give SUPERVISOR group view access
allow if {
    input.scope == utils.VIEW
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.has_perm(organizations.SUPERVISOR)
}
                                                            ###utils.UPDATE_ASSOCIATED_STORAGE -->New utility 2.40##
                                                            #Comment- Deny WORKER view access
#allow if {
#    input.scope == utils.VIEW
#    input.auth.organization.id == input.resource.organization.id
#    organizations.has_perm(organizations.WORKER)
#    is_project_staff
#}

                                                            #Comment- Deny WORKER in scope below
#allow if {
#    input.scope in {utils.DELETE, utils.UPDATE_ORG, utils.UPDATE_ASSOCIATED_STORAGE}
#    utils.is_sandbox
#    utils.has_perm(utils.WORKER)
#    utils.is_resource_owner
#}

allow if {
    input.scope in {utils.DELETE, utils.UPDATE_ORG, utils.UPDATE_ASSOCIATED_STORAGE}
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)                             #Modifed- Worker -> USER group
    organizations.has_perm(organizations.SUPERVISOR)       #Modified is_member -> SUPERVISOR
    utils.is_resource_owner
}

                                                           #Added- BUSINESS group with scope
allow if {
    input.scope in { utils.DELETE, utils.UPDATE_ORG }[input.scope]
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.BUSINESS)
    organizations.is_member
    utils.is_resource_owner
}
                                                           #Comment- Deny user scope
#allow if {
#    input.scope in {utils.DELETE, utils.UPDATE_ORG, utils.UPDATE_ASSOCIATED_STORAGE}
#    input.auth.organization.id == input.resource.organization.id
#    utils.has_perm(utils.USER)
#    organizations.is_staff
#}
                                                            #Comment- Deny scope for user
#allow if {
#    input.scope in {utils.UPDATE_DESC, utils.IMPORT_DATASET}
#    utils.is_sandbox
#    is_project_staff
#    utils.has_perm(utils.USER)                            #Modify- WORKER -> USER
#}

allow if {
    input.scope in {utils.UPDATE_DESC, utils.IMPORT_DATASET}
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.is_staff
}

allow if {
    input.scope in {utils.UPDATE_DESC, utils.IMPORT_DATASET}
    is_project_staff
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.WORKER)
    organizations.is_member
}
                                                    #Comment- sandbox',deny worker scope
#allow if {
#    input.scope == utils.UPDATE_ASSIGNEE
#    utils.is_sandbox
#    utils.is_resource_owner
#    utils.has_perm(utils.WORKER)
#}

allow if {
    input.scope == utils.UPDATE_ASSIGNEE
    input.auth.organization.id == input.resource.organization.id
    utils.is_resource_owner
    utils.has_perm(utils.USER)                  #Modified - WORKER -> USER?
    organizations.is_member
}

allow if {
    input.scope == utils.UPDATE_ASSIGNEE
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.is_staff
}

allow if {
    input.scope == utils.UPDATE_OWNER
    input.auth.organization.id == input.resource.organization.id
    utils.is_resource_owner
    utils.has_perm(utils.USER)                 #Modify- WORKER-> USER?
    organizations.is_staff
}

allow if {
    input.scope == utils.UPDATE_OWNER
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.is_staff
}
                                                #Comment - Deny sandbom privilege
#allow if {
#    input.scope in {utils.EXPORT_ANNOTATIONS, utils.EXPORT_DATASET, utils.EXPORT_BACKUP}
#    utils.is_sandbox
#    is_project_staff
#}

allow if {
    input.scope in {utils.EXPORT_ANNOTATIONS, utils.EXPORT_DATASET, utils.EXPORT_BACKUP}
    input.auth.organization.id == input.resource.organization.id
    organizations.is_member
    is_project_staff
}

allow if {
    input.scope in {utils.EXPORT_ANNOTATIONS, utils.EXPORT_DATASET, utils.EXPORT_BACKUP}
    input.auth.organization.id == input.resource.organization.id
    utils.has_perm(utils.USER)
    organizations.has_perm(organizations.MAINTAINER)
}
                                                #Comment - Please check scope?
allow if {
    input.scope == utils.DOWNLOAD_EXPORTED_FILE
    input.auth.user.id == input.resource.rq_job.owner.id
}