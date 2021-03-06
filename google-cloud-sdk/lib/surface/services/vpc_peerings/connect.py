# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""services vpc-peerings connect command."""

from googlecloudsdk.api_lib.cloudresourcemanager import projects_api
from googlecloudsdk.api_lib.services import peering
from googlecloudsdk.api_lib.services import services_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.projects import util as projects_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties

OP_BASE_CMD = 'gcloud alpha services vpc-peerings operations '
OP_WAIT_CMD = OP_BASE_CMD + 'wait {0}'

_DETAILED_HELP = {
    'DESCRIPTION':
        """\
        This command connects a network to a service via VPC peering for a
        project.
        """,
    'EXAMPLES':
        """\
        To connect a network called `my-network`  on the current project to a
        service called `your-service` with reserved IP CIDR ranges
        `10.197.0.0/20,10.198.0.0/20` for the service to use, run:

          $ {command} --network my-network --service your-service \\
              --reserved-ranges 10.197.0.0/20,10.198.0.0/20

        To run the same command asynchronously (non-blocking), run:

          $ {command} --network my-network --service your-service \\
              --reserved-ranges 10.197.0.0/20,10.198.0.0/20 --async
        """,
}

_SERVICE_HELP = """The service to connect to"""
_NETWORK_HELP = """The network in the current project to be peered with the \
  service"""
_RESERVED_RANGES_HELP = """The reserved IP CIDR ranges for service to use"""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Connect(base.SilentCommand):
  """Connect to a service via VPC peering for a project network."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        '--network', metavar='NETWORK', required=True, help=_NETWORK_HELP)
    parser.add_argument(
        '--service', metavar='SERVICE', required=True, help=_SERVICE_HELP)
    parser.add_argument(
        '--reserved-ranges',
        metavar='RESERVED_RANGES',
        required=True,
        help=_RESERVED_RANGES_HELP)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run 'services vpc-peerings connect'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      Nothing.
    """
    project = properties.VALUES.core.project.Get(required=True)
    project_number = _GetProjectNumber(project)
    reserved_ranges = args.reserved_ranges.split(',')
    op = peering.PeerApiCall(project_number, args.service, args.network,
                             reserved_ranges)
    if args.async:
      cmd = OP_WAIT_CMD.format(op.name)
      log.status.Print('Asynchronous operation is in progress... '
                       'Use the following command to wait for its '
                       'completion:\n {0}'.format(cmd))
      return
    op = peering.WaitOperation(op.name)
    services_util.PrintOperation(op)


Connect.detailed_help = _DETAILED_HELP


def _GetProjectNumber(project_id):
  return projects_api.Get(projects_util.ParseProject(project_id)).projectNumber
