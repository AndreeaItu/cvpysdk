#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright ©2016 Commvault Systems, Inc.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Service urls for rest api operations.

ApiLibrary: class having all the REST API services initialized with the commcell

ApiLibrary:
    __init__(commcell_service)      --  initialize all the API services with the commcell service
    __repr__()                      --  retuns string representation for this class

"""


class ApiLibrary(object):
    """Class ApiLibrary for defining all the rest api urls."""

    def __init__(self, commcell_service):
        """Initializes the instance of the class ApiLibrary.

            Args:
                commcell_service (str)  --  the url of the commcell service for the API
        """
        self.LOGIN = '{0}Login'
        self.LOGOUT = '{0}Logout'

        self.GET_ALL_CLIENTS = '{0}Client'
        self.GET_VIRTUAL_CLIENTS = '{0}Client?PseudoClientType=VSPseudo'
        self.CLIENT = '{0}Client/%s'

        self.GET_ALL_AGENTS = '{0}Agent?clientId=%s'
        self.AGENT = '{0}Agent'

        self.GET_ALL_BACKUPSETS = '{0}Backupset?clientId=%s'
        self.BACKUPSET = '{0}Backupset/%s'
        self.ADD_BACKUPSET = '{0}Backupset'

        self.GET_ALL_SUBCLIENTS = '{0}Subclient?clientId=%s'
        self.ADD_SUBCLIENT = '{0}Subclient'
        self.SUBCLIENT = '{0}Subclient/%s'
        self.SUBCLIENT_BACKUP = '{0}Subclient/%s/action/backup?backupLevel=%s'

        self.GET_JOBS = '{0}Job?clientId=%s&jobFilter=%s'
        self.JOB = '{0}Job/%s'
        self.JOB_DETAILS = '{0}JobDetails'
        self.SUSPEND_JOB = '{0}Job/%s/action/pause'
        self.RESUME_JOB = '{0}Job/%s/action/resume'
        self.KILL_JOB = '{0}Job/%s/action/kill'

        self.GET_MEDIA_AGENTS = '{0}MediaAgent'
        self.LIBRARY = '{0}Library'

        self.STORAGE_POLICY = '{0}StoragePolicy'
        self.SCHEDULE_POLICY = '{0}SchedulePolicy'

        self.GET_ALL_ALERTS = '{0}/AlertRule'
        self.ALERT = '{0}/AlertRule/%s'
        self.GET_ALL_CONSOLE_ALERTS = '{0}/Alert?pageNo=%s&pageCount=%s'
        self.ENABLE_ALERT_NOTIFICATION = '{0}/AlertRule/%s/notificationType/%s/Action/Enable'
        self.DISABLE_ALERT_NOTIFICATION = '{0}/AlertRule/%s/notificationType/%s/Action/Disable'
        self.ENABLE_ALERT = '{0}/AlertRule/%s/Action/Enable'
        self.DISABLE_ALERT = '{0}/AlertRule/%s/Action/Disable'

        self.CLIENT_SCHEDULES = '{0}Schedules?clientId=%s'
        self.AGENT_SCHEDULES = '{0}Schedules?clientId=%s&apptypeId=%s'
        self.BACKUPSET_SCHEDULES = '{0}Schedules?clientId=%s&apptypeId=%s&backupsetId=%s'
        self.SUBCLIENT_SCHEDULES = ('{0}Schedules?clientId=%s&apptypeId=%s&'
                                    'backupsetId=%s&subclientId=%s')

        self.CLIENTGROUPS = '{0}ClientGroup'
        self.CLIENTGROUP = '{0}ClientGroup/%s'

        self.USERGROUPS = '{0}UserGroup'
        self.USERGROUP = '{0}UserGroup/%s'

        self.BROWSE = '{0}DoBrowse'
        self.RESTORE = '{0}retrieveToClient'

        self.GET_WORKFLOWS = '{0}Workflow'
        self.EXECUTE_WORKFLOW = '{0}Workflow/%s/Action/Execute'

        for key, value in vars(self).items():
            setattr(self, key, value.format(commcell_service))

    def __repr__(self):
        """Representation string for this class instance."""
        return 'ApiLibrary class instance for all REST API services.'
