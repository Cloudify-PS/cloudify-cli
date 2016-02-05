########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

"""
Handles 'cfy logs'
"""
import os

import fabric.api as fab

from cloudify_cli import messages
from cloudify_cli import utils
from cloudify_cli.cli import get_global_verbosity
from cloudify_cli.logger import get_logger
from cloudify_cli.exceptions import CloudifyCliError


def _build_host_string():
    return '{0}@{1}'.format(
        utils.get_management_user(),
        utils.get_management_server_ip())


def _get_manager_date():
    # output here should be hidden anyway.
    with fab.settings(fab.hide('running', 'stdout')):
        return _run('date +%Y%m%dT%H%M%S').stdout


def _get(remote_source_path, destination_path):
    key_filename = os.path.expanduser(utils.get_management_key())
    with fab.settings(
            fab.hide('running', 'stdout'),
            host_string=_build_host_string(),
            key_filename=key_filename):
        fab.get(remote_source_path, destination_path)


def _run(command):
    def execute():
        key_filename = os.path.expanduser(utils.get_management_key())
        with fab.settings(
                host_string=_build_host_string(),
                key_filename=key_filename):
            result = fab.sudo(command)
            if result.failed:
                raise CloudifyCliError(
                    'Failed to execute: {0} ({1})'.format(
                        result.read_command, result.stderr))
            return result

    if get_global_verbosity():
        return execute()
    else:
        with fab.hide('running', 'stdout'):
            return execute()


def _archive_logs():
    logger = get_logger()
    # TODO: maybe allow the user to set the prefix?
    archive_filename = 'cloudify-manager-logs_{0}_{1}.tar.gz'.format(
        _get_manager_date(), utils.get_management_server_ip())
    archive_path = os.path.join('/tmp', archive_filename)

    _run('journalctl > /tmp/jctl && '
         'mv /tmp/jctl /var/log/cloudify/journalctl_log')
    logger.info('Creating logs archive in Manager: {0}'.format(archive_path))
    # We skip checking if the tar executable can be found on the machine
    # knowingly. We don't want to run another ssh command just to verify
    # something that will almost never happen.
    _run('tar -czf {0} -C /var/log cloudify'.format(archive_path))
    return archive_path


def get(destination_path):
    logger = get_logger()
    archive_path_on_manager = _archive_logs()
    logger.info('Downloading archive to: {0}'.format(destination_path))
    _get(archive_path_on_manager, destination_path)
    logger.info('Removing archive from Manager...')
    _run('rm {0}'.format(archive_path_on_manager))


def purge(force=False, backup_first=False):
    logger = get_logger()
    if backup_first:
        backup()
    if not force:
        msg = messages.LOG_PURGE_REQUIRES_FORCE
        raise CloudifyCliError(msg)

    logger.info('Purging Manager Logs...')
    # well, we could've just `find /var/log/cloudify -name "*" -type f -delete`
    # thing is, it will delete all files and nothing will be written into them
    # until the relevant service is restarted.
    # echo "" | sudo tee $f >/dev/null is an alternative for cleanup.
    _run('for f in $(sudo find /var/log/cloudify -name "*" -type f); '
         'do sudo truncate -s 0 $f; done')


def backup():
    logger = get_logger()
    archive_path_on_manager = _archive_logs()
    logger.info('Backing up Manager logs to /var/log/{0}'.format(
        os.path.basename(archive_path_on_manager)))
    _run('mv {0} {1}'.format(archive_path_on_manager, '/var/log/'))
