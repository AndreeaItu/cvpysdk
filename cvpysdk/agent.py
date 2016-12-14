#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright ©2016 Commvault Systems, Inc.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for performing agent specific operations.

Agents and Agent are 2 classes defined in this file.

Agents: Class for representing all the agents associated with a specific client

Agent: Class for a single agent selected for a client, and to perform operations on that agent


Agents:
    __init__(client_object)     --  initialise object of Agents class associated with
                                        the specified client
    __str__()                   --  returns all the agents associated with the client
    __repr__()                  --  returns the string for the instance of the Agents class
    _get_agents()               --  gets all the agents associated with the client specified
    has_agent(agent_name)       --  checks if an agent exists with the given name
    get(agent_name)             --  returns the Agent class object of the input agent name

Agent:
    __init__(client_object,
             agent_name,
             agent_id=None)     --   initialise object of Agent with the specified agent name
                                         and id, and associated to the specified client
    __repr__()                  --   return the agent name, the instance is associated with
    _get_agent_id()             --   method to get the agent id

"""

import string

from backupset import Backupsets
from schedules import Schedules
from exception import SDKException


class Agents(object):
    """Class for getting all the agents associated with a client."""

    def __init__(self, client_object):
        """Initialize object of the Agents class.

            Args:
                client_object (object)  --  instance of the Client class

            Returns:
                object - instance of the Agents class
        """
        self._client_object = client_object
        self._commcell_object = self._client_object._commcell_object

        self._ALL_AGENTS = self._commcell_object._services.GET_ALL_AGENTS % (
            self._client_object.client_id
        )

        self._agents = self._get_agents()

    def __str__(self):
        """Representation string consisting of all agents of the client.

            Returns:
                str - string of all the agents of a client
        """
        representation_string = '{:^5}\t{:^20}\t{:^20}\n\n'.format('S. No.', 'Agent', 'Client')

        for index, agent in enumerate(self._agents):
            sub_str = '{:^5}\t{:20}\t{:20}\n'.format(
                index + 1,
                agent,
                self._client_object.client_name
            )
            representation_string += sub_str

        return representation_string.strip()

    def __repr__(self):
        """Representation string for the instance of the Clients class."""
        return "Agents class instance for Client: '{0}'".format(self._client_object.client_name)

    def _get_agents(self):
        """Gets all the agents associated to the client specified with this client object.

            Returns:
                dict - consists of all agents in the client
                    {
                         "agent1_name": agent1_id,
                         "agent2_name": agent2_id
                    }

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._client_object._commcell_object._cvpysdk_object.make_request(
            'GET', self._ALL_AGENTS
        )

        if flag:
            if response.json():
                agent_dict = {}
                for dictionary in response.json()['agentProperties']:
                    temp_name = str(dictionary['idaEntity']['appName']).lower()
                    temp_id = str(dictionary['idaEntity']['applicationId']).lower()
                    agent_dict[temp_name] = temp_id

                return agent_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def has_agent(self, agent_name):
        """Checks if an agent is installed for the client with the input agent name.

            Args:
                agent_name (str)  --  name of the agent

            Returns:
                bool - boolean output whether the agent is installed for the client or not

            Raises:
                SDKException:
                    if type of the agent name argument is not string
        """
        if not isinstance(agent_name, str):
            raise SDKException('Agent', '103')

        return self._agents and str(agent_name).lower() in self._agents

    def get(self, agent_name):
        """Returns a agent object of the specified client.

            Args:
                agent_name (str)  --  name of the agent

            Returns:
                object - instance of the Agent class for the given agent name

            Raises:
                SDKException:
                    if type of the agent name argument is not string
                    if no agent exists with the given name
        """
        if not isinstance(agent_name, str):
            raise SDKException('Agent', '103')
        else:
            agent_name = str(agent_name).lower()

            if self.has_agent(agent_name):
                return Agent(self._client_object, agent_name, self._agents[agent_name])

            raise SDKException('Agent',
                               '102',
                               'No agent exists with name: {0}'.format(agent_name))


class Agent(object):
    """Class for performing agent operations of an agent for a specific client."""

    def __init__(self, client_object, agent_name, agent_id=None):
        """Initialise the agent object.

            Args:
                client_object (object)  --  instance of the Client class to which the agent belongs
                agent_name (str)        --  name of the agent (File System, Virtual Server, etc.)
                agent_id (str)          --  id of the associated agent
                    default: None

            Returns:
                object - instance of the Agent class
        """
        self._client_object = client_object
        self._commcell_object = self._client_object._commcell_object
        self._agent_name = str(agent_name)

        if agent_id:
            # Use the agent id mentioned in the arguments
            self._agent_id = str(agent_id)
        else:
            # Get the agent id if agent id is not provided
            self._agent_id = self._get_agent_id()

        self.backupsets = Backupsets(self)
        self.schedules = Schedules(self)

    def __repr__(self):
        """String representation of the instance of this class."""
        representation_string = '"{0}" Agent instance for Client: "{1}"'

        return representation_string.format(string.capwords(self.agent_name),
                                            self._client_object.client_name)

    def _get_agent_id(self):
        """Gets the agent id associated with this agent.

            Returns:
                str - id associated with this agent
        """
        agents = Agents(self._client_object)
        return agents.get(self.agent_name).agent_id

    @property
    def agent_id(self):
        """Treats the agent id as a read-only attribute."""
        return self._agent_id

    @property
    def agent_name(self):
        """Treats the agent name as a read-only attribute."""
        return self._agent_name
