# Copyright: (c) 2018, Pluribus Networks
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules import pn_stp_port
from ansible_collections.community.general.tests.unit.modules.utils import set_module_args
from ..nvos_module import TestNvosModule


class TestStpPortModule(TestNvosModule):

    module = pn_stp_port

    def setUp(self):
        self.mock_run_nvos_commands = patch('ansible_collections.community.general.plugins.modules.pn_stp_port.run_cli')
        self.run_nvos_commands = self.mock_run_nvos_commands.start()

    def tearDown(self):
        self.mock_run_nvos_commands.stop()

    def run_cli_patch(self, module, cli, state_map):
        if state_map['update'] == 'stp-port-modify':
            results = dict(
                changed=True,
                cli_cmd=cli
            )
        module.exit_json(**results)

    def load_fixtures(self, commands=None, state=None, transport='cli'):
        self.run_nvos_commands.side_effect = self.run_cli_patch

    def test_stp_port_modify_t1(self):
        set_module_args({'pn_cliswitch': 'sw01', 'pn_port': '1',
                         'pn_filter': True, 'pn_priority': '144', 'state': 'update'})
        result = self.execute_module(changed=True, state='update')
        expected_cmd = ' switch sw01 stp-port-modify  priority 144 cost 2000 port 1 filter '
        self.assertEqual(result['cli_cmd'], expected_cmd)

    def test_stp_port_modify_t2(self):
        set_module_args({'pn_cliswitch': 'sw01', 'pn_port': '1,2',
                         'pn_cost': '200', 'state': 'update'})
        result = self.execute_module(changed=True, state='update')
        expected_cmd = ' switch sw01 stp-port-modify  priority 128 cost 200 port 1,2'
        self.assertEqual(result['cli_cmd'], expected_cmd)
