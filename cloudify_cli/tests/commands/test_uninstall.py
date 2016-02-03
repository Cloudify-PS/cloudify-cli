########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
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
Tests 'cfy uninstall'
"""

from mock import patch

from cloudify_cli.constants import DEFAULT_TIMEOUT
from cloudify_cli.constants import DEFAULT_PARAMETERS
from cloudify_cli.tests import cli_runner
from cloudify_cli.tests.commands.test_cli_command import CliCommandTest


class UninstallTest(CliCommandTest):

    @patch('cloudify_cli.commands.blueprints.delete')
    @patch('cloudify_cli.commands.deployments.delete')
    @patch('cloudify_cli.utils.get_rest_client')
    @patch('cloudify_cli.commands.executions.start')
    def test_default_executions_start_arguments(self,
                                               executions_start_mock, *args
                                               ):
        uninstall_command = 'cfy uninstall -b bid -d did'
        cli_runner.run_cli(uninstall_command)

        executions_start_mock.assert_called_with('uninstall',
                                                 'did',
                                                 DEFAULT_TIMEOUT,
                                                 False,
                                                 False,
                                                 False,
                                                 DEFAULT_PARAMETERS
                                                 )

    @patch('cloudify_cli.commands.blueprints.delete')
    @patch('cloudify_cli.commands.deployments.delete')
    @patch('cloudify_cli.utils.get_rest_client')
    @patch('cloudify_cli.commands.executions.start')
    def test_custom_executions_start_arguments(self,
                                              executions_start_mock, *args
                                              ):
        uninstall_command = 'cfy uninstall -b bid ' \
                            '-w my_uninstall ' \
                            '-d did ' \
                            '--timeout 1987 ' \
                            '--allow-custom-parameters ' \
                            '--include-logs ' \
                            '--parameters key=value ' \

        cli_runner.run_cli(uninstall_command)

        executions_start_mock.assert_called_with('my_uninstall',
                                                 'did',
                                                 1987,
                                                 False,
                                                 True,
                                                 True,
                                                 "key=value"
                                                 )

    @patch('cloudify_cli.commands.blueprints.delete')
    @patch('cloudify_cli.utils.get_rest_client')
    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.delete')
    def test_deployments_delete_arguments(self, deployments_delete_mock,
                                          *args):

        uninstall_command = 'cfy uninstall -b bid -d did'

        cli_runner.run_cli(uninstall_command)

        deployments_delete_mock.assert_called_with('did', True)

    @patch('cloudify_cli.utils.get_rest_client')
    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.delete')
    @patch('cloudify_cli.commands.blueprints.delete')
    def test_blueprints_delete_arguments(self, blueprints_delete_mock, *args):

        uninstall_command = 'cfy uninstall -b bid -d did'

        cli_runner.run_cli(uninstall_command)

        blueprints_delete_mock.assert_called_with('bid')


