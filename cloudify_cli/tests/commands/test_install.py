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
from cloudify_cli import utils

from cloudify_cli.constants import DEFAULT_BLUEPRINT_FILE_NAME
from cloudify_cli.constants import DEFAULT_BLUEPRINT_PATH
from cloudify_cli.constants import DEFAULT_INPUTS_PATH_FOR_INSTALL_COMMAND
from cloudify_cli.constants import DEFAULT_TIMEOUT
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

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_blueprint_path_default_value(self, blueprints_upload_mock, *args):

        install_upload_mode_command = \
            'cfy install --blueprint-id={0}'.format(stub_blueprint_id)

        tmp_blueprint_path = os.path.join(self.original_utils_get_cwd(),
                                          DEFAULT_BLUEPRINT_PATH)

        # create a tmp file representing a blueprint to upload
        open(tmp_blueprint_path, 'w+').close()

        cli_runner.run_cli(install_upload_mode_command)

        blueprint_path_argument_from_upload = \
            blueprints_upload_mock.call_args_list[0][0][0]

        # check that the blueprint path value that was assigned in `install`
        # is indeed the default blueprint file path
        self.assertEqual(blueprint_path_argument_from_upload.name,
                         tmp_blueprint_path
                         )

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

    @patch('cloudify_cli.commands.executions.start')
    @patch('cloudify_cli.commands.deployments.create')
    @patch('cloudify_cli.commands.blueprints.upload')
    def test_blueprint_id_default_upload_mode(self, blueprints_upload_mock,
                                              *args):

        install_upload_mode_command = \
            'cfy install -p {0}'.format(sample_blueprint_path)

        directory_name = 'helloworld'

        cli_runner.run_cli(install_upload_mode_command)

        blueprint_id_argument_from_upload = \
            blueprints_upload_mock.call_args_list[0][0][1]

        # check that the blueprint id value that was assigned in `install`
        # is indeed the default blueprint id (that is, the name of the dir
        # that contains the blueprint file)
        self.assertEqual(blueprint_id_argument_from_upload,
                         directory_name
                         )

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

    @patch('cloudify_cli.commands.blueprints.publish_archive')
    @patch('cloudify_cli.commands.executions.start')
    def test_default_inputs_file_path(self, *args):

        # create an `inputs.yaml` file in the cwd.
        inputs_path = os.path.join(utils.get_cwd(), 'inputs.yaml')
        os.mknod(inputs_path)

        command = \
            'cfy install -n {0} --archive-location={1} ' \
            '-b {2} -d {3}' \
            .format(stub_filename, stub_archive,
                    stub_blueprint_id, stub_deployment_id)

        self.assert_method_called(
                cli_command=command,
                module=commands.deployments,
                function_name='create',
                args=[stub_blueprint_id,
                      stub_deployment_id,
                      DEFAULT_INPUTS_PATH_FOR_INSTALL_COMMAND]
        )

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

    @patch('cloudify_cli.commands.install')
    def test_default_full_flow_upload_mode(self, install_mock):

        install_command = 'cfy install'

        cli_runner.run_cli(install_command)

        install_command_arguments = \
            install_mock.call_args_list[0][1]

        expected_install_command_arguments = \
            {'blueprint_path': None,
             'blueprint_id': None,
             'archive_location': None,
             'blueprint_filename': None,
             'deployment_id': None,
             'inputs': None,
             'workflow_id': 'install',
             'parameters': {},
             'allow_custom_parameters': False,
             'timeout': DEFAULT_TIMEOUT,
             'include_logs': False
             }

        self.assertEqual(install_command_arguments,
                         expected_install_command_arguments)

    @patch('cloudify_cli.commands.install')
    def test_default_values_full_flow(self, install_mock):

        install_command = 'cfy install'

        cli_runner.run_cli(install_command)

        install_command_arguments = install_mock.call_args_list[0][1]

        expected_install_command_arguments = \
            {'blueprint_path': None,
             'blueprint_id': None,
             'archive_location': None,
             'blueprint_filename': None,
             'deployment_id': None,
             'inputs': None,
             'workflow_id': 'install',
             'parameters': {},
             'allow_custom_parameters': False,
             'timeout': DEFAULT_TIMEOUT,
             'include_logs': False
             }

        self.assertEqual(install_command_arguments,
                         expected_install_command_arguments)
