########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

"""
Handles 'cfy install'
"""

import os
import urlparse

from cloudify_cli import utils
from cloudify_cli.commands import blueprints
from cloudify_cli.commands import deployments
from cloudify_cli.commands import executions
from cloudify_cli.constants import DEFAULT_BLUEPRINT_FILE_NAME
from cloudify_cli.constants import DEFAULT_BLUEPRINT_PATH
from cloudify_cli.constants import DEFAULT_INPUTS_PATH_FOR_INSTALL_COMMAND
from cloudify_cli.exceptions import CloudifyCliError


def install(blueprint_path, blueprint_id, archive_location, blueprint_filename,
            deployment_id, inputs, workflow_id, parameters,
            allow_custom_parameters, timeout, include_logs):

    # First, make sure the `blueprint-path` wasn't supplied with
    # `archive_location` or with `blueprint_filename`
    check_for_mutually_exclusive_arguments(blueprint_path,
                                           archive_location,
                                           blueprint_filename)

    # The presence of the `archive_location` argument is used to distinguish
    # between `install` in 'blueprints upload' mode,
    # and `install` in 'blueprints publish archive' mode.
    if archive_location:

        if blueprint_filename is None:
            blueprint_filename = DEFAULT_BLUEPRINT_FILE_NAME

        # If blueprint-id wasn't supplied, assign it to the name of the archive
        if blueprint_id is None:

            blueprints.check_if_archive_type_is_supported(archive_location)

            (archive_location, archive_location_type) = \
                blueprints.determine_archive_type(archive_location)

            # if the archive is a local path, assign blueprint-id the name of
            # the archive file without the extension
            if archive_location_type == 'path':
                filename, ext = os.path.splitext(
                        os.path.basename(archive_location))
                blueprint_id = filename

            # if the archive is a url, assign blueprint-id name of the file
            # that the url leads to, without the extension.
            # e.g. http://example.com/path/archive.zip?para=val#sect -> archive
            if archive_location_type == 'url':

                path = urlparse.urlparse(archive_location).path
                archive_file = path.split('/')[-1]
                archive_name = archive_file.split('.')[0]
                blueprint_id = archive_name

        blueprints.publish_archive(archive_location, blueprint_filename,
                                   blueprint_id)
    else:

        if blueprint_path is None:
            blueprint_path = os.path.join(utils.get_cwd(),
                                          DEFAULT_BLUEPRINT_PATH)

        # If blueprint-id wasn't supplied, assign it to the name of
        # folder containing the application's blueprint file.
        if blueprint_id is None:

            blueprint_id = os.path.basename(
                    os.path.dirname(
                            os.path.abspath(
                                    blueprint_path)))
        # Try opening `blueprint_path`, since `blueprints.upload` expects the
        # `blueprint_path` argument to be a file.
        # (The reason for this is beyond me. That's just the way it is)
        try:
            with open(blueprint_path) as blueprint_file:
                blueprints.upload(blueprint_file, blueprint_id)
        except IOError:
            raise CloudifyCliError("Can't open the the file that "
                                   "`blueprint_path` leads to)"
                                   )

    # If deployment-id wasn't supplied, use the same name as the blueprint id.
    if deployment_id is None:
        deployment_id = blueprint_id

    # If no inputs were supplied, and there is a file named inputs.yaml in
    # the cwd, use it as the inputs file
    if inputs is None:
        if os.path.isfile(
                os.path.join(utils.get_cwd(),
                             DEFAULT_INPUTS_PATH_FOR_INSTALL_COMMAND)):

            inputs = DEFAULT_INPUTS_PATH_FOR_INSTALL_COMMAND

    deployments.create(blueprint_id, deployment_id, inputs)

    # although the `install` command does not need the `force` argument,
    # we *are* using the `executions start` handler as a part of it.
    # as a result, we need to provide it with a `force` argument, which is
    # defined below.
    force = False

    executions.start(workflow_id, deployment_id, timeout, force,
                     allow_custom_parameters, include_logs, parameters)


def check_for_mutually_exclusive_arguments(blueprint_path,
                                           archive_location,
                                           blueprint_filename):
    if blueprint_path and (archive_location or blueprint_filename):
        raise CloudifyCliError(
            "`blueprint-path` can't be supplied with "
            "`archive-location` and/or `blueprint-filename`"
        )
