#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright ©2016 Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for performing operations on a job.

Job: Class for keeping track of a job and perform various operations on it.

Job:
    __init__(commcell_object,
             job_id)            --  initialises the instance of Job class associated with the
                                        specified commcell of job with id: 'job_id'
    __repr__()                  --  returns the string representation of the object of this class,
                                        with the job id it is associated with
    _is_valid_job()             --  checks if the job with the given id is a valid job or not.
    _check_finished()           --  checks if the job has finished or not yet
    _is_finished()              --  checks for the status of the job.
                                        Returns True if finished, else False
    _get_job_summary()          --  gets the summary of the job with the given job id
    _get_job_details()          --  gets the details of the job with the given job id
    _initialize_job_properties()--  initializes the properties of the job
    pause()                     --  suspend the job
    resume()                    --  resumes the job
    kill()                      --  kills the job


job.status                      --  Gives the current status of the job.
                                        (Completed / Suspended / Waiting / ... / etc.)
job.finished                    --  Tells whether the job is finished or not. (True / False)

"""

from __future__ import absolute_import

import time
import threading

from .exception import SDKException


class Job(object):
    """Class for performing client operations for a specific client."""

    def __init__(self, commcell_object, job_id):
        """Initialise the Job class instance.

            Args:
                commcell_object (object)     --  instance of the Commcell class
                job_id          (str / int)  --  id of the job

            Returns:
                object - instance of the Job class

            Raises:
                SDKException:
                    if job id is not of type int
                    if job is not a valid job, i.e., does not exist in the Commcell
        """
        try:
            int(job_id)
        except ValueError:
            raise SDKException('Job', '101')

        self._commcell_object = commcell_object
        self._job_id = str(job_id)

        self._JOB = self._commcell_object._services.JOB % (self.job_id)

        if not self._is_valid_job():
            raise SDKException('Job', '102')

        self._JOB_DETAILS = self._commcell_object._services.JOB_DETAILS
        self._SUSPEND = self._commcell_object._services.SUSPEND_JOB % (self.job_id)
        self._RESUME = self._commcell_object._services.RESUME_JOB % (self.job_id)
        self._KILL = self._commcell_object._services.KILL_JOB % (self.job_id)

        self.finished = self._is_finished()
        self.status = str(self._get_job_summary()['status'])

        self._delay_reason = None
        self._pending_reason = None

        self._initialize_job_properties()

        thread = threading.Thread(target=self._check_finished)
        thread.start()

    def __repr__(self):
        """String representation of the instance of this class.

            Returns:
                str - string for instance of this class
        """
        representation_string = 'Job class instance for job id: "{0}"'
        return representation_string.format(self.job_id)

    def _is_valid_job(self):
        """Checks if the job submitted with the job id is a valid job or not.

            Returns:
                bool - boolean that represents whether the job is valid or not
        """
        for i in range(3):
            try:
                self._get_job_summary()
                return True
            except SDKException as excp:
                if excp.exception_module == 'Job' and excp.exception_id == '103':
                    continue
                else:
                    raise excp
            time.sleep(5)

        return False

    def _check_finished(self):
        """Checks whether the job has finished or not.

            Returns:
                None
        """
        while not self._is_finished():
            time.sleep(5)

        self.finished = self._is_finished()

    def _is_finished(self):
        """Checks whether the job has finished or not.

            Returns:
                bool - boolean that represents whether the job has finished or not
        """
        job_summary = self._get_job_summary()
        job_details = self._get_job_details()

        self.status = str(job_summary['status'])

        if job_summary['lastUpdateTime'] != 0:
            self._end_time = time.ctime(job_summary['lastUpdateTime'])
        else:
            self._end_time = None

        if 'pendingReason' in job_summary:
            if job_summary['pendingReason']:
                self._pending_reason = job_summary['pendingReason']

        if 'reasonForJobDelay' in job_details['jobDetail']['progressInfo']:
            if job_details['jobDetail']['progressInfo']['reasonForJobDelay']:
                self._delay_reason = job_details['jobDetail']['progressInfo']['reasonForJobDelay']

        return ('completed' in self.status.lower() or
                'killed' in self.status.lower() or
                'failed' in self.status.lower())

    def _get_job_summary(self):
        """Gets the properties of this job.

            Returns:
                dict - dict that contains the summary of this job

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('GET', self._JOB)

        if flag:
            if response.json():
                if response.json()['totalRecordsWithoutPaging'] == 0:
                    raise SDKException('Job', '103')

                if 'jobs' in response.json():
                    for job in response.json()['jobs']:
                        return job['jobSummary']
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _get_job_details(self):
        """Gets the detailed properties of this job.

            Returns:
                dict - dict consisting of the detailed properties of the job

            Raises:
                SDKException:
                    if response is empty
                    if response is not success
        """
        payload = {
            "jobId": int(self.job_id)
        }

        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', self._JOB_DETAILS, payload
        )

        if flag:
            if response.json() and 'job' in response.json():
                return response.json()['job']
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _initialize_job_properties(self):
        """Initializes the common properties for the job.
            Adds the client, agent, backupset, subclient name to the job object.

            Returns:
                None
        """
        job_summary = self._get_job_summary()
        job_details = self._get_job_details()

        subclient_properties = job_summary['subclient']

        self._client_name = str(subclient_properties['clientName'])
        self._agent_name = str(subclient_properties['appName'])

        if 'backupsetName' in subclient_properties:
            self._backupset_name = str(subclient_properties['backupsetName'])
        else:
            self._backupset_name = None

        if 'instanceName' in subclient_properties:
            self._instance_name = str(subclient_properties['instanceName'])
        else:
            self._instance_name = None

        self._job_type = str(job_summary['jobType'])

        if self._job_type == 'Backup' and 'backupLevelName' in job_summary:
            self._backup_level = str(job_summary['backupLevelName'])
        else:
            self._backup_level = None

        self._start_time = time.ctime(job_summary['jobStartTime'])

        if 'subclientName' in subclient_properties:
            self._subclient_name = str(subclient_properties['subclientName'])
        else:
            self._subclient_name = 'Not provided in Job details'

        if 'pendingReason' in job_summary:
            if job_summary['pendingReason']:
                self._pending_reason = job_summary['pendingReason']

        if 'reasonForJobDelay' in job_details['jobDetail']['progressInfo']:
            if job_details['jobDetail']['progressInfo']['reasonForJobDelay']:
                self._delay_reason = job_details['jobDetail']['progressInfo']['reasonForJobDelay']

    @property
    def client_name(self):
        """Treats the client name as a read-only attribute."""
        return self._client_name

    @property
    def agent_name(self):
        """Treats the agent name as a read-only attribute."""
        return self._agent_name

    @property
    def backupset_name(self):
        """Treats the backupset name as a read-only attribute."""
        return self._backupset_name

    @property
    def instance_name(self):
        """Treats the instance name as a read-only attribute."""
        return self._instance_name

    @property
    def subclient_name(self):
        """Treats the subclient name as a read-only attribute."""
        return self._subclient_name

    @property
    def job_id(self):
        """Treats the job id as a read-only attribute."""
        return self._job_id

    @property
    def job_type(self):
        """Treats the job type as a read-only attribute."""
        return self._job_type

    @property
    def backup_level(self):
        """Treats the backup level as a read-only attribute."""
        return self._backup_level

    @property
    def start_time(self):
        """Treats the start time as a read-only attribute."""
        return self._start_time

    @property
    def end_time(self):
        """Treats the end time as a read-only attribute."""
        return self._end_time

    @property
    def delay_reason(self):
        """Treats the job delay reason as a read-only attribute."""
        return self._delay_reason

    @property
    def pending_reason(self):
        """Treats the job pending reason as a read-only attribute."""
        return self._pending_reason

    def pause(self):
        """Suspend the job.

            Returns:
                None

            Raises:
                SDKException:
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('POST', self._SUSPEND)

        if flag:
            if response.json() and 'errors' in response.json():
                error_list = response.json()['errors'][0]['errList'][0]
                error_message = str(error_list['errLogMessage']).strip()

                return 'Job suspend failed\nError: "{0}"'.format(error_message)
            else:
                self.status = str(self._get_job_summary()['status'])
                return 'Job suspended successfully'
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def resume(self):
        """Resume the job.

            Returns:
                None

            Raises:
                SDKException:
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('POST', self._RESUME)

        if flag:
            if response.json() and 'errors' in response.json():
                error_list = response.json()['errors'][0]['errList'][0]
                error_message = str(error_list['errLogMessage']).strip()

                return 'Job resume failed\nError: "{0}"'.format(error_message)
            else:
                self.status = str(self._get_job_summary()['status'])
                return 'Job resumed successfully'
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def kill(self):
        """Kill the job.

            Returns:
                None

            Raises:
                SDKException:
                    if response is not success
        """
        flag, response = self._commcell_object._cvpysdk_object.make_request('POST', self._KILL)

        if flag:
            if response.json() and 'errors' in response.json():
                error_list = response.json()['errors'][0]['errList'][0]
                error_message = str(error_list['errLogMessage']).strip()

                return 'Job kill failed\nError: "{0}"'.format(error_message)
            else:
                self.status = str(self._get_job_summary()['status'])
                self.finished = True
                return 'Job killed successfully'
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)
