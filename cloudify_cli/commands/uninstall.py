########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
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
Handles 'cfy uninstall'
"""

import os

from cloudify_cli.exceptions import CloudifyCliError
from cloudify_cli import execution_events_fetcher
from cloudify_cli import utils
from cloudify_cli.commands import blueprints
from cloudify_cli.commands import deployments
from cloudify_cli.commands import executions


def uninstall(blueprint_id, deployment_id, workflow_id, parameters,
              allow_custom_parameters, timeout, include_logs):

    # Although the `uninstall` command does not use the `force` argument,
    # we are using the `executions start` handler as a part of it.
    # As a result, we need to provide it with a `force` argument, which is
    # defined below.
    force = False

    executions.start(workflow_id, deployment_id, timeout, force,
                     allow_custom_parameters, include_logs, parameters)

    # Because we want to delete the deployment right after executing the
    # uninstall workflow, we may need to wait for the deployment executions to
    # end.
    wait_for_stop_dep_env_execution_to_end(deployment_id)

    deployments.delete(deployment_id, ignore_live_nodes=False)

    blueprints.delete(blueprint_id)

# The function below (taken, with small modifications,
# from `cloudify-system-tests.cosmo_tester.framework.testenv`),
# enables to call `cfy deployments delete`
# immediately after calling `cfy executions start [-w uninstall]`
TERMINATED = 'terminated'
FAILED = 'failed'
CANCELLED = 'cancelled'
END_STATES = [TERMINATED, FAILED, CANCELLED]


def wait_for_stop_dep_env_execution_to_end(deployment_id):

    client = utils.get_rest_client()

    # The underscore in `_executions` is so that this variable's name
    # won't shadow `executions` from the import section.
    _executions = client.executions.list(
            deployment_id=deployment_id,
            include_system_workflows=True)
    running_stop_executions = [e for e in _executions if e.workflow_id ==
                               '_stop_deployment_environment' and
                               e.status not in END_STATES]

    if not running_stop_executions:
        return

    if len(running_stop_executions) > 1:
        raise CloudifyCliError('There is more than one running '
                               '"_stop_deployment_environment" execution: {0}'
                               .format(running_stop_executions))

    execution = running_stop_executions[0]
    return execution_events_fetcher.wait_for_execution(client, execution)
