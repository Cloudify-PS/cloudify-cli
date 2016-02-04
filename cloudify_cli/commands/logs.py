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

CLOUDIFY_LOGS_PATH = '/var/log/cloudify'


def _build_host_string():
    return '{0}@{1}'.format(
        utils.get_management_user(),
        utils.get_management_server_ip())


def _run(command):
    def execute():
        with fab.settings(host_string=_build_host_string()):
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


def _archive_logs(format='tar.gz'):
    logger = get_logger()
    with fab.hide('running', 'stdout'):
        date = _run('date +%Y%m%dT%H%M%S').stdout
    # TODO: maybe allow the user to set the prefix?
    archive_filename = 'cloudify-manager-logs_{0}_{1}.{2}'.format(
        date, utils.get_management_server_ip(), format)
    archive_path = os.path.join('/tmp', archive_filename)

    _run('journalctl | tee {0}/journalctl_log'.format(CLOUDIFY_LOGS_PATH))
    logger.info('Creating logs archive in Manager: {0}'.format(archive_path))
    # We skip checking if the zip/tar executables can be found on the machine
    # knowingly. We don't want to run another ssh command just to verify
    # something that will almost never happen.
    if format == 'zip':
        cmd = 'zip {0} {1}'
    elif format == 'tar.gz':
        cmd = 'tar -czf {0} {1}'
    _run(cmd.format(archive_path, CLOUDIFY_LOGS_PATH))
    return archive_path


def get(destination_path, format='tar.gz'):
    logger = get_logger()
    fab.env.key_filename = os.path.expanduser(utils.get_management_key())
    archive_path = _archive_logs(format=format)
    with fab.settings(host_string=_build_host_string()):
        logger.info('Downloading archive to: {0}'.format(destination_path))
        with fab.hide('running', 'stdout'):
            fab.get(archive_path, destination_path)
    logger.info('Removing archive from Manager...')
    _run('rm {0}'.format(archive_path))


def purge(force=False, backup_first=False):
    logger = get_logger()
    fab.env.key_filename = os.path.expanduser(utils.get_management_key())
    if backup_first:
        backup()
    if not force:
        msg = messages.LOG_PURGE_REQUIRES_FORCE
        raise CloudifyCliError(msg)

    logger.info('Purging Manager Logs...')
    _run('rm -f {0}/**/*'.format(CLOUDIFY_LOGS_PATH))


def backup(format='tar.gz'):
    logger = get_logger()
    fab.env.key_filename = os.path.expanduser(utils.get_management_key())
    archive_path = _archive_logs(format=format)
    filename = os.path.basename(archive_path)
    logger.info('Backing up Manager logs to /var/log/{0}'.format(filename))
    _run('mv {0} {1}'.format(archive_path, '/var/log/'))
