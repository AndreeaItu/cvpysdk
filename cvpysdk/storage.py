#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright ©2016 Commvault Systems, Inc.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for performing storage related operations on the commcell.

This file has all the classes related to Storage operations.

MediaAgents:      Class for representing all the media agents attached to the commcell.
MediaAgent:       Class for representing a single media agent attached to the commcell.
DiskLibraries:    Class for representing all the disk libraries attached to the commcell.
DiskLibrary:      Class for representing a single disk library associated with the commcell.
StoragePolicies:  Class for all the Storage Policies associated to the commcell.

MediaAgents:
    __init__(commcell_object) -- initialize the MediaAgents class instance for the commcell
    __repr__()   -- returns a string representation of all the media agents associated
    _get_media_agents()  -- gets all the media agents of the commcell
    get(media_agent_name) -- returns the instance of MediaAgent class of the media agent specified

MediaAgent:
    __init__(commcell_object,
             media_agent_name,
             media_agent_id)   --  initialize the instance of MediaAgent class for a specific
                                     media agent of the commcell
    __repr__()                 --  returns a string representation of the MediaAgent instance
    _get_media_agent_id()      --  gets the id of the MediaAgent instance from commcell

DiskLibraries:
    __init__(commcell_object) -- initialize the DiskLibraries class instance for the commcell
    __repr__()   -- returns a string representation of all the disk libraries associated
    _get_libraries()  --  gets all the disk libraries of the commcell
    get(library_name)  --  returns the instance of the DiskLibrary class for the library specified
    add()    --   adds a new disk library to the commcell

DiskLibrary:
    __init__(commcell_object,
             library_name,
             library_id)   --  initialize the instance of DiskLibrary class for a specific
                                     disk library of the commcell
    __repr__()                 --  returns a string representation of the DiskLibrary instance
    _get_library_id()      --  gets the id of the DiskLibrary instance from commcell

StoragePolicies:
    __init__(commcell_object) -- initialize the StoragePolicies class instance for the commcell
    __repr__()   -- returns a string representation of all the storage policies associated
    _get_policies()  --  gets all the storage policies of the commcell
    add()    --   adds a new storage policy to the commcell
    delete(storage_policy_name)   --  removes the specified storage policy from the commcell

SchedulePolicies:
    __init__(commcell_object) -- initialize the SchedulePolicies class instance for the commcell
    __repr__()   -- returns a string representation of all the schedule policies associated
    _get_policies()  --  gets all the schedule policies of the commcell
"""

import urllib

from exception import SDKException


class MediaAgents(object):
    """Class for getting all the media agents associated with the commcell."""

    def __init__(self, commcell_object):
        """Initialize object of the MediaAgents class.

            Args:
                commcell_object (object) - instance of the Commcell class

            Returns:
                object - instance of the MediaAgents class
        """
        self._commcell_object = commcell_object
        self._MEDIA_AGENTS = self._commcell_object._services.GET_MEDIA_AGENTS
        self._media_agents = self._get_media_agents()

    def __repr__(self):
        """Returns all the media agents associated with the commcell.

            Returns:
                str - string consisting of all the media agents of the commcell
        """
        representation_string = ''

        for media_agent_name, media_agent_id in self._media_agents.items():
            sub_str = 'Media Agent "{0}" of Commcell: "{1}"\n'
            sub_str = sub_str.format(media_agent_name, self._commcell_object._headers['Host'])
            representation_string += sub_str

        return representation_string.strip()

    def _get_media_agents(self):
        """Gets all the media agents associated to the commcell specified by commcell object.

            Returns:
                dict - consists of all media agents of the commcell
                    {
                         "media_agent1_name": media_agent1_id,
                         "media_agent2_name": media_agent2_id
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'GET', self._MEDIA_AGENTS)

        if flag:
            if response.json() and 'response' in response.json():
                media_agents = response.json()['response']
                media_agents_dict = {}

                for media_agent in media_agents:
                    temp_name = str(media_agent['entityInfo']['name']).lower()
                    temp_id = str(media_agent['entityInfo']['id']).lower()
                    media_agents_dict[temp_name] = temp_id

                return media_agents_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def get(self, media_agent_name):
        """Returns a MediaAgent object of the specified media agent name.

            Args:
                media_agent_name (str) - name of the media agent

            Returns:
                object - instance of the MediaAgent class for the given media agent name

            Raises:
                SDKException:
                    if type of the media agent name argument is not string
                    if no media agent exists with the given name
        """
        if not isinstance(media_agent_name, str):
            raise SDKException('Storage', '102')
        else:
            media_agent_name = str(media_agent_name).lower()
            all_media_agents = self._media_agents

            if all_media_agents and media_agent_name in all_media_agents:
                return MediaAgent(self._commcell_object,
                                  media_agent_name,
                                  all_media_agents[media_agent_name])

            raise SDKException('Storage',
                               '101',
                               'No media agent exists with name: {0}'.format(media_agent_name))


class MediaAgent(object):
    """Class for a specific media agent."""

    def __init__(self, commcell_object, media_agent_name, media_agent_id=None):
        """Initialise the MediaAgent object.

            Args:
                commcell_object (object) - instance of the Commcell class
                media_agent_name (str) - name of the media agent
                media_agent_id (str) - id of the media agent
                    default: None

            Returns:
                object - instance of the MediaAgent class
        """
        self._commcell_object = commcell_object
        self._media_agent_name = str(media_agent_name).lower()
        if media_agent_id:
            self._media_agent_id = str(media_agent_id)
        else:
            self._media_agent_id = self._get_media_agent_id()

    def __repr__(self):
        """String representation of the instance of this class.

            Returns:
                str - string containing the details of this media agent
        """
        representation_string = 'Media Agent Instance for media agent: "{0}", of Commcell: "{1}"'

        return representation_string.format(self.media_agent_name,
                                            self._commcell_object._headers['Host'])

    def _get_media_agent_id(self):
        """Gets the media agent id associated with this media agent.

            Returns:
                str - id associated with this media agent
        """
        media_agents = MediaAgents(self._commcell_object)
        return media_agents.get(self.media_agent_name).media_agent_id

    @property
    def media_agent_name(self):
        """Treats the media agent name as a read-only attribute."""
        return self._media_agent_name

    @property
    def media_agent_id(self):
        """Treats the media agent id as a read-only attribute."""
        return self._media_agent_id


class DiskLibraries(object):
    """Class for getting all the disk libraries associated with the commcell."""

    def __init__(self, commcell_object):
        """Initialize object of the DiskLibraries class.

            Args:
                commcell_object (object) - instance of the Commcell class

            Returns:
                object - instance of the DiskLibraries class
        """
        self._commcell_object = commcell_object
        self._LIBRARY = self._commcell_object._services.LIBRARY
        self._libraries = self._get_libraries()

    def __repr__(self):
        """Returns all the disk libraries associated with the commcell.

            Returns:
                str - string consisting of all the disk libraries of the commcell
        """
        representation_string = ''

        for library_name, library_id in self._libraries.items():
            sub_str = 'Disk Library "{0}" of Commcell: "{1}"\n'
            sub_str = sub_str.format(library_name, self._commcell_object._headers['Host'])
            representation_string += sub_str

        return representation_string.strip()

    def _get_libraries(self):
        """Gets all the disk libraries associated to the commcell specified by commcell object.

            Returns:
                dict - consists of all disk libraries of the commcell
                    {
                         "disk_library1_name": disk_library1_id,
                         "disk_library2_name": disk_library2_id
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('GET',
                                                                            self._LIBRARY)

        if flag:
            if response.json() and 'response' in response.json():
                libraries = response.json()['response']
                libraries_dict = {}

                for library in libraries:
                    temp_name = str(library['entityInfo']['name']).lower()
                    temp_id = str(library['entityInfo']['id']).lower()
                    libraries_dict[temp_name] = temp_id

                return libraries_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def get(self, library_name):
        """Returns a DiskLibrary object of the specified disk library name.

            Args:
                library_name (str) - name of the disk library

            Returns:
                object - instance of the DiskLibrary class for the given library name

            Raises:
                SDKException:
                    if type of the library name argument is not string
                    if no disk library exists with the given name
        """
        if not isinstance(library_name, str):
            raise SDKException('Storage', '102')
        else:
            library_name = str(library_name).lower()
            all_libraries = self._libraries

            if all_libraries and library_name in all_libraries:
                return DiskLibrary(self._commcell_object,
                                   library_name,
                                   all_libraries[library_name])

            raise SDKException('Storage',
                               '101',
                               'No disk library exists with name: {0}'.format(library_name))

    def add(self, library_name, media_agent, mount_path, username="", password=""):
        """Adds a new Disk Library to the Commcell.

            Args:
                library_name (str) - name of the new library to add
                media_agent (str/object) - name or instance of media agent to add the library to
                mount_path (str) - full string path of the folder to mount the library to
                username (str) - username that is used by the system to access the mount path
                    default: ""
                password (str) - password that is used by the system to access the mount path
                    default: ""

            Returns:
                object - instance of the DiskLibrary class, if created successfully
                None - if failed to add disk library

            Raises:
                SDKException:
                    if type of the library name argument is not string
                    if type of the mount path argument is not string
                    if type of the username argument is not string
                    if type of the password argument is not string
                    if type of the media agent argument is not either string or MediaAgent instance
                    if response is empty
                    if response is not success
        """
        if not (isinstance(library_name, str) and
                isinstance(mount_path, str) and
                isinstance(username, str) and
                isinstance(password, str)):
            raise SDKException('Storage', '102')

        if isinstance(media_agent, MediaAgent):
            media_agent = media_agent
        elif isinstance(media_agent, str):
            media_agent = MediaAgent(self._commcell_object, media_agent)
        else:
            raise SDKException('Storage', '103')

        request_json = {
            "EVGui_ConfigureStorageLibraryReq": {
                "isConfigRequired": 1,
                "library": {
                    "mediaAgentId": int(media_agent.media_agent_id),
                    "libraryName": library_name,
                    "mountPath": mount_path,
                    "loginName": username,
                    "password": password,
                    "opType": 1
                }
            }
        }

        flag, response = self._commcell_object._cvpysdk_object.make_request('POST',
                                                                            self._LIBRARY,
                                                                            request_json)

        if flag:
            if response.json():
                if 'library' in response.json():
                    library = response.json()['library']
                    print 'Created library: "{0}" successfully.'.format(library['libraryName'])

                    # initialize the libraries again
                    # so the libraries object has all the libraries
                    self._libraries = self._get_libraries()

                    return DiskLibrary(self._commcell_object, library['libraryName'])
                elif 'errorCode' in response.json():
                    error_code = response.json()['errorCode']
                    error_message = response.json()['errorMessage']
                    o_str = 'Failed to create disk library with error code: "{0}", error: "{1}"'
                    print o_str.format(error_code, error_message)
                    return None
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)


class DiskLibrary(object):
    """Class for a specific disk library."""

    def __init__(self, commcell_object, library_name, library_id=None):
        """Initialise the DiskLibrary object.

            Args:
                commcell_object (object) - instance of the Commcell class
                library_name (str) - name of the disk library
                library_id (str) - id of the disk library
                    default: None

            Returns:
                object - instance of the DiskLibrary class
        """
        self._commcell_object = commcell_object
        self._library_name = str(library_name)
        if library_id:
            self._library_id = str(library_id)
        else:
            self._library_id = self._get_library_id()

        if not self._library_id:
            raise SDKException('Storage',
                               '101',
                               'No disk library exists with name: {0}'.format(library_name))

    def __repr__(self):
        """String representation of the instance of this class.

            Returns:
                str - string containing the details of this library
        """
        representation_string = 'Disk Library Instance for library: "{0}" of Commcell: "{1}"'
        return representation_string.format(self.library_name,
                                            self._commcell_object._headers['Host'])

    def _get_library_id(self):
        """Gets the library id associated with this disk library.

            Returns:
                str - id associated with this disk library
        """
        libraries = DiskLibraries(self._commcell_object)
        return libraries.get(self.library_name).library_id

    @property
    def library_name(self):
        """Treats the library name as a read-only attribute."""
        return self._library_name

    @property
    def library_id(self):
        """Treats the library id as a read-only attribute."""
        return self._library_id


class StoragePolicies(object):
    """Class for getting all the storage policies associated with the commcell."""

    def __init__(self, commcell_object):
        """Initialize object of the StoragePolicies class.

            Args:
                commcell_object (object) - instance of the Commcell class

            Returns:
                object - instance of the StoragePolicies class
        """
        self._commcell_object = commcell_object
        self._POLICY = self._commcell_object._services.STORAGE_POLICY
        self._policies = self._get_policies()

    def __repr__(self):
        """Returns all the storage policies associated with the commcell.

            Returns:
                str - string consisting of all the storage policies of the commcell
        """
        representation_string = ''
        for policy_name, policy_id in self._policies.items():
            sub_str = 'Storage Policy "{0}" of Commcell: "{1}"\n'
            sub_str = sub_str.format(policy_name, self._commcell_object._headers['Host'])
            representation_string += sub_str

        return representation_string.strip()

    def _get_policies(self):
        """Gets all the storage policies associated to the commcell specified by commcell object.

            Returns:
                dict - consists of all storage policies of the commcell
                    {
                         "storage_policy1_name": storage_policy1_id,
                         "storage_policy2_name": storage_policy2_id
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('GET',
                                                                            self._POLICY)

        if flag:
            if response.json() and 'policies' in response.json():
                policies = response.json()['policies']
                policies_dict = {}

                for policy in policies:
                    temp_name = str(policy['storagePolicyName']).lower()
                    temp_id = str(policy['storagePolicyId']).lower()
                    policies_dict[temp_name] = temp_id

                return policies_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def add(self,
            storage_policy_name,
            library,
            media_agent,
            dedup_path=None,
            incremental_sp=None,
            retention_period=5):
        """Adds a new Storage Policy to the Commcell.

            Args:
                storage_policy_name (str) - name of the new storage policy to add
                library (str/object) - name or instance of the library to add the storage policy to
                media_agent (str/object) - name or instance of media agent to add the policy to
                dedup_path (str) - the path of the deduplication database
                    default: None
                incremental_sp (str) - the name of the incremental storage policy
                                        associated with the storage policy
                    default: None
                retention_period (int)  -  time period in days to retain the data backup for
                    default: 5

            Returns:
                object - instance of the DiskLibrary class, if created successfully
                None - if failed to add disk library

            Raises:
                SDKException:
                    if type of the storage policy name argument is not string
                    if type of the retention period argument is not int
                    if type of the library argument is not either string or DiskLibrary instance
                    if type of the media agent argument is not either string or MediaAgent instance
                    if response is empty
                    if response is not success
        """
        if ((dedup_path is not None and not isinstance(dedup_path, str)) or
                (not (isinstance(storage_policy_name, str) and
                      isinstance(retention_period, int))) or
                (incremental_sp is not None and not isinstance(incremental_sp, str))):
            raise SDKException('Storage', '102')

        if isinstance(library, DiskLibrary):
            disk_library = library
        elif isinstance(library, str):
            disk_library = DiskLibrary(self._commcell_object, library)
        else:
            raise SDKException('Storage', '104')

        if isinstance(media_agent, MediaAgent):
            media_agent = media_agent
        elif isinstance(media_agent, str):
            media_agent = MediaAgent(self._commcell_object, media_agent)
        else:
            raise SDKException('Storage', '103')

        if dedup_path or incremental_sp:
            encode_dict = {
                "storagepolicy": storage_policy_name,
                "mediaagent": media_agent.media_agent_name,
                "library": disk_library.library_name
            }
            if dedup_path:
                encode_dict["deduppath"] = dedup_path
            if incremental_sp:
                encode_dict["incstoragepolicy"] = incremental_sp

            web_service = self._POLICY + '?' + urllib.urlencode(encode_dict)

            flag, response = self._commcell_object._cvpysdk_object.make_request('PUT', web_service)

            if flag:
                try:
                    if response.json():
                        if 'errorCode' in response.json() and 'errorMessage' in response.json():
                            error_code = str(response.json()['errorCode'])
                            error_message = str(response.json()['errorMessage']).split('\n')[0]
                            o_str = 'Failed to add storage policy with error code: "{0}", error: "{1}"'
                            print o_str.format(error_code, error_message)
                except ValueError:
                    if response.text:
                        print response.text.strip()
                        self._policies = self._get_policies()
                    else:
                        raise SDKException('Response', '102')
            else:
                response_string = self._commcell_object._update_response_(response.text)
                raise SDKException('Response', '101', response_string)
        else:
            request_json = {
                "storagePolicyCopyInfo": {
                    "library": {
                        "libraryId": int(disk_library.library_id)
                    },
                    "mediaAgent": {
                        "mediaAgentId": int(media_agent.media_agent_id)
                    },
                    "retentionRules": {
                        "retainBackupDataForDays": retention_period
                    }
                },
                "storagePolicyName": storage_policy_name
            }

            flag, response = self._commcell_object._cvpysdk_object.make_request('POST',
                                                                                self._POLICY,
                                                                                request_json)

            if flag:
                if response.json():
                    if 'archiveGroupCopy' in response.json():
                        policy = response.json()['archiveGroupCopy']
                        policy_name = policy['storagePolicyName']
                        print 'Created Storage Policy: "{0}" successfully.'.format(policy_name)

                        # initialize the policies again
                        # so the policies object has all the policies
                        self._policies = self._get_policies()
                    elif 'error' in response.json():
                        error_code = response.json()['error']['errorCode']
                        error_message = response.json()['error']['errorMessage']
                        o_str = 'Failed to create storage policy with error code: "{0}", error: "{1}"'
                        print o_str.format(error_code, error_message)
                else:
                    raise SDKException('Response', '102')
            else:
                response_string = self._commcell_object._update_response_(response.text)
                raise SDKException('Response', '101', response_string)

    def delete(self, storage_policy_name):
        """Deletes a storage policy from the commcell.

            Args:
                storage_policy_name (str) - name of the storage policy to delete

            Returns:
                None

            Raises:
                SDKException:
                    if type of the storage policy name argument is not string
                    if response is empty
                    if response is not success
        """
        if not isinstance(storage_policy_name, str):
            raise SDKException('Storage', '102')

        policy_delete_service = self._POLICY + '/{0}'.format(storage_policy_name)

        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'DELETE', policy_delete_service)

        if flag:
            try:
                if response.json():
                    if 'errorCode' in response.json() and 'errorMessage' in response.json():
                        error_code = str(response.json()['errorCode'])
                        error_message = str(response.json()['errorMessage'])
                        o_str = 'Failed to delete storage policy with error code: "{0}", error: "{1}"'
                        print o_str.format(error_code, error_message)
            except ValueError:
                if response.text:
                    print response.text
                    self._policies = self._get_policies()
                else:
                    raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)


class SchedulePolicies(object):
    """Class for getting all the schedule policies associated with the commcell."""

    def __init__(self, commcell_object):
        """Initialize object of the SchedulePolicies class.

            Args:
                commcell_object (object) - instance of the Commcell class

            Returns:
                object - instance of the SchedulePolicies class
        """
        self._commcell_object = commcell_object
        self._POLICY = self._commcell_object._services.SCHEDULE_POLICY
        self._policies = self._get_policies()

    def __repr__(self):
        """Returns all the storage policies associated with the commcell.

            Returns:
                str - string consisting of all the storage policies of the commcell
        """
        representation_string = ''
        for policy_name, policy_id in self._policies.items():
            sub_str = 'Schedule Policy "{0}" of Commcell: "{1}"\n'
            sub_str = sub_str.format(policy_name, self._commcell_object._headers['Host'])
            representation_string += sub_str

        return representation_string.strip()

    def _get_policies(self):
        """Gets all the schedule policies associated to the commcell specified by commcell object.

            Returns:
                dict - consists of all schedule policies of the commcell
                    {
                         "schedule_policy1_name": schedule_policy1_id,
                         "schedule_policy2_name": schedule_policy2_id
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('GET',
                                                                            self._POLICY)

        if flag:
            if response.json() and 'taskDetail' in response.json():
                policies = response.json()['taskDetail']
                policies_dict = {}

                for policy in policies:
                    temp_name = str(policy['task']['taskName']).lower()
                    temp_id = str(policy['task']['taskId']).lower()
                    policies_dict[temp_name] = temp_id

                return policies_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)
