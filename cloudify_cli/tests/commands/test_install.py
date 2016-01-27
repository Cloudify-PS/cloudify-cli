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

from cloudify_cli import commands
from cloudify_cli.constants import DEFAULT_BLUEPRINT_FILE_NAME
from cloudify_cli.constants import DEFAULT_BLUEPRINT_PATH
from cloudify_cli.exceptions import CloudifyCliError
from cloudify_cli.tests import cli_runner
from cloudify_cli.tests.commands.test_cli_command import CliCommandTest
from cloudify_cli.tests.commands.test_cli_command import BLUEPRINTS_DIR


sample_blueprint_path = os.path.join(BLUEPRINTS_DIR,
                                     'helloworld',
                                     'blueprint.yaml')
stub_filename = 'my_blueprint.yaml'
stub_archive = 'archive.zip'
stub_blueprint_id = 'blueprint_id'
stub_inputs = 'inputs.yaml'
stub_deployment_id = 'deployment_id'
stub_timeout = 900
stub_force = False
stub_allow_custom_parameters = False
stub_include_logs = False
stub_parameters = {}


class InstallTest(CliCommandTest):

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_mutually_exclusive_arguments(self, *args):

        path_and_filename_cmd = \
            'cfy install -p {0} -n {1}'.format(sample_blueprint_path,
                                               stub_filename)

        path_and_archive_cmd = \
            'cfy install -p {0} --archive-location={1}' \
                .format(sample_blueprint_path,
                        stub_archive)

        path_and_filename_and_archive_cmd = \
            'cfy install -p {0} -n {1} --archive-location={2}' \
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

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_use_blueprints_upload_mode(
            self,
            blueprints_upload_mock,
            blueprints_publish_archive_mock,
            deployments_create_mock,
            executions_start_mock):

        upload_mode_install_cmd = 'cfy install -p {0}' \
            .format(sample_blueprint_path)

        cli_runner.run_cli(upload_mode_install_cmd)

        self.assertTrue(blueprints_upload_mock.called)
        self.assertTrue(deployments_create_mock.called)
        self.assertTrue(executions_start_mock.called)
        self.assertFalse(blueprints_publish_archive_mock.called)

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
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


    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_blueprint_filename_default_value(self, *args):
        publish_archive_command = \
            'cfy install --archive-location={0} --blueprint-id={1}'\
            .format(stub_archive, stub_blueprint_id)

        self.assert_method_called(
                cli_command=publish_archive_command,
                module=commands.blueprints,
                function_name='publish_archive',
                args=[stub_archive, DEFAULT_BLUEPRINT_FILE_NAME,
                      stub_blueprint_id
                      ]
        )

    # # TODO figure out how to handle the fact that `DEFAULT_BLUEPRINT_PATH`
    # # TODO does not exists, and therefore `install.blueprints_action` raises an
    # # TODO exception before it calls `blueprints.upload
    # # TODO maybe create a tmp file in the cwd named 'blueprint.yaml'?
    # @patch('cloudify_cli.commands.executions.start')
    # @patch('cloudify_cli.commands.deployments.create')
    # @patch('cloudify_cli.commands.blueprints.publish_archive')
    # def test_blueprint_path_default_value(self, *args):
    #     upload_command = \
    #         'cfy install --blueprint-id={0}'.format(stub_blueprint_id)
    #
    #     self.assert_method_called(
    #             cli_command=upload_command,
    #             module=commands.blueprints,
    #             function_name='upload',
    #             args=[DEFAULT_BLUEPRINT_PATH, stub_blueprint_id]
    #     )

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_blueprint_id_default_publish_archive_mode(self, *args):

        publish_archive_command = \
            'cfy install -n {0} --archive-location={1}'.format(stub_filename,
                                                               stub_archive)
        archive_name = 'archive'

        self.assert_method_called(
                cli_command=publish_archive_command,
                module=commands.blueprints,
                function_name='publish_archive',
                args=[stub_archive, stub_filename, archive_name]
        )


    # # TODO address the fact that `blueprints upload` expects an open file
    # # TODO maybe create a tmp file in the cwd named 'blueprint.yaml'?
    # @patch('cloudify_cli.commands.executions.start')
    # @patch('cloudify_cli.commands.deployments.create')
    # @patch('cloudify_cli.commands.blueprints.upload')
    # def test_blueprint_id_default_upload_mode(self, *args):
    #
    #     upload_command = 'cfy install -p {0}'.format(sample_blueprint_path)
    #
    #     directory_name = 'helloworld'
    #
    #     self.assert_method_called(
    #             cli_command=upload_command,
    #             module=commands.blueprints,
    #             function_name='upload',
    #             args=[sample_blueprint_path, directory_name]
    #     )

    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.executions.start')
    def test_default_deployment_id(self, *args):

        command = \
            'cfy install -n {0} --archive-location={1} --inputs={2} -b {3}'\
                .format(stub_filename, stub_archive,
                        stub_inputs, stub_blueprint_id)

        self.assert_method_called(
                cli_command=command,
                module=commands.deployments,
                function_name='create',
                args=[stub_blueprint_id, stub_blueprint_id, stub_inputs]
        )

    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.executions.start')
    def test_custom_deployment_id(self, *args):

        command = \
            'cfy install -n {0} --archive-location={1} ' \
            '--inputs={2} -b {3} -d {4}' \
                .format(stub_filename, stub_archive,
                        stub_inputs, stub_blueprint_id,
                        stub_deployment_id)

        self.assert_method_called(
                cli_command=command,
                module=commands.deployments,
                function_name='create',
                args=[stub_blueprint_id, stub_deployment_id, stub_inputs]
        )
    # TODO both the above tests also in 'blueprints upload mode'?

    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.deployments.create')
    def test_default_workflow_name(self, *args):

        command = \
            'cfy install -n {0} --archive-location={1} ' \
            '--inputs={2} -d {3}' \
                .format(stub_filename, stub_archive,
                        stub_inputs, stub_deployment_id)

        self.assert_method_called(
                cli_command=command,
                module=commands.executions,
                function_name='start',
                args=['install', stub_deployment_id, stub_timeout,
                      stub_force, stub_allow_custom_parameters,
                      stub_include_logs, stub_parameters
                      ]
        )
    # TODO The above test also in 'blueprints upload mode'?
    



















        # test default workflow name (seperate modes too?)

        # test full 'regular' flow in 'light' mode (seperate?)

        # test full 'regular' flow in 'full' mode (seperate?)