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
Tests 'cfy install'
"""

import os

from mock import patch

from cloudify_cli.exceptions import CloudifyCliError
from cloudify_cli.tests import cli_runner
from cloudify_cli.tests.commands.test_cli_command import CliCommandTest
from cloudify_cli.tests.commands.test_cli_command import BLUEPRINTS_DIR

sample_blueprint_path = os.path.join(BLUEPRINTS_DIR,
                                     'helloworld',
                                     'blueprint.yaml')
stub_filename = 'filename'
stub_archive = 'archive'


class InstallTest(CliCommandTest):

    @patch('cloudify_cli.commands.blueprints.upload')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.executions.start')
    def test_mutually_exclusive_arguments(self, *args):

        path_and_filename_cmd = \
            'cfy install -p {0} -n {1}'.format(sample_blueprint_path,
                                               stub_filename)

        path_and_archive_cmd = \
            'cfy install -p {0} --archive-location={1}'\
            .format(sample_blueprint_path,
                    stub_archive)

        path_and_filename_and_archive_cmd = \
            'cfy install -p {0} -n {1} --archive-location={2}'\
            .format(sample_blueprint_path,
                    stub_filename,
                    stub_archive)

        self.assertRaises(CloudifyCliError,
                          cli_runner.run_cli,
                          path_and_filename_cmd
                          )
        self.assertRaises(CloudifyCliError,
                          cli_runner.run_cli,
                          path_and_archive_cmd
                          )
        self.assertRaises(CloudifyCliError,
                          cli_runner.run_cli,
                          path_and_filename_and_archive_cmd
                          )

    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_use_blueprints_upload_mode(
            self,
            blueprints_upload_mock,
            blueprints_publish_archive_mock,
            deployments_create_mock,
            executions_start_mock):

        upload_mode_install_cmd = 'cfy install -p {0}'\
            .format(sample_blueprint_path)

        cli_runner.run_cli(upload_mode_install_cmd)

        self.assertTrue(blueprints_upload_mock.called)
        self.assertTrue(deployments_create_mock.called)
        self.assertTrue(executions_start_mock.called)
        self.assertFalse(blueprints_publish_archive_mock.called)

    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_use_blueprints_publish_archive_mode(
            self,
            blueprints_upload_mock,
            blueprints_publish_archive_mock,
            deployments_create_mock,
            executions_start_mock):

        publish_archive_command = \
            'cfy install -n {0} --archive-location={1}'.format(stub_filename,
                                                               stub_archive)

        cli_runner.run_cli(publish_archive_command)

        self.assertTrue(blueprints_publish_archive_mock)
        self.assertTrue(deployments_create_mock)
        self.assertTrue(executions_start_mock)
        self.assertFalse(blueprints_upload_mock.called)


