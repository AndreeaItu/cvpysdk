#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright ©2016 Commvault Systems, Inc.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for performing schedule related operations for client/agent/backupset/subclient.

Schedules: Initializes instance of all schedules for a commcell entity.

Schedules:
    __init__(class_object)  --  initialise object of the Schedules class
    __repr__()              -- string of all the schedules associated with the commcell entity
    _get_schedules()        -- gets all the schedules associated with the commcell entity
"""

from exception import SDKException


class Schedules(object):
    """Class for getting the schedules of a commcell entity."""

    def __init__(self, class_object):
        """Initialise the Schedules class instance.

            Args:
                class_object (object) - instance of the client/agent/backupset/subclient class

            Returns:
                object - instance of the Schedules class

            Raises:
                SDKException:
                    if class object does not belong to any of the Client or Agent or Backupset or
                        Subclient class
        """
        # imports inside the __init__ method definition to avoid cyclic imports
        from client import Client
        from agent import Agent
        from backupset import Backupset
        from subclient import Subclient

        self._commcell_object = class_object._commcell_object

        if isinstance(class_object, Client):
            self._SCHEDULES = self._commcell_object._services.CLIENT_SCHEDULES % (
                class_object.client_id
            )
        elif isinstance(class_object, Agent):
            self._SCHEDULES = self._commcell_object._services.AGENT_SCHEDULES % (
                class_object._client_object.client_id,
                class_object.agent_id
            )
        elif isinstance(class_object, Backupset):
            self._SCHEDULES = self._commcell_object._services.BACKUPSET_SCHEDULES % (
                class_object._agent_object._client_object.client_id,
                class_object._agent_object.agent_id,
                class_object.backupset_id
            )
        elif isinstance(class_object, Subclient):
            self._SCHEDULES = self._commcell_object._services.SUBCLIENT_SCHEDULES % (
                class_object._backupset_object._agent_object._client_object.client_id,
                class_object._backupset_object._agent_object.agent_id,
                class_object._backupset_object.backupset_id,
                class_object.subclient_id
            )
        else:
            raise SDKException('Schedules', '101')

        self.schedules = self._get_schedules()

    def __repr__(self):
        """Representation string for the instance of the Schedules class.

            Returns:
                str - string of all the schedules of a commcell entity
        """
        representation_string = ''

        for schedule_name, _ in self.schedules.items():
            sub_str = 'Schedule: "{0}"\n'
            sub_str = sub_str.format(schedule_name)
            representation_string += sub_str

        return representation_string.strip()

    def _get_schedules(self):
        """Gets the schedules associated with the input commcell entity.
            Client / Agent / Backupset / Subclient

            Returns:
                dict - consists of all schedules for the commcell entity
                    {
                         "schedule1_name": [
                             schedule1_id, {
                                 "subtask1_name": subtask1_id,
                                 "subtask2_name": subtask2_id
                             }
                         ],
                         "schedule2_name": [
                             schedule2_id, {
                                 "subtask1_name": subtask1_id,
                                 "subtask2_name": subtask2_id
                             }
                         ]
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('GET', self._SCHEDULES)

        if flag:
            if response.json():
                schedules_dict = {}

                for schedule in response.json()['taskDetail']:
                    if 'taskName' in schedule['task'] and schedule['task']['taskName']:
                        schedule_name = schedule['task']['taskName']
                    elif 'description' in schedule['task'] and schedule['task']['description']:
                        schedule_name = schedule['task']['description']
                    else:
                        continue

                    temp_name = str(schedule_name).lower()
                    temp_id = str(schedule['task']['taskId']).lower()

                    subtask_dict = {}

                    for subtask in schedule['subTasks']:
                        if 'subTaskName' in subtask['subTask']:
                            subtask_name = str(subtask['subTask']['subTaskName']).lower()
                        else:
                            continue

                        if 'subTaskId' in subtask['subTask']:
                            subtask_id = str(subtask['subTask']['subTaskId']).lower()
                        else:
                            continue

                        subtask_dict[subtask_name] = subtask_id

                    schedules_dict[temp_name] = [temp_id, subtask_dict]

                return schedules_dict
            else:
                return {}
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)
