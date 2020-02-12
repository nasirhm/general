#
# (c) 2018 Extreme Networks Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.modules.utils import set_module_args
from ansible_collections.community.general.plugins.modules import exos_command
from ..exos_module import TestExosModule, load_fixture


class TestExosCommandModule(TestExosModule):

    module = exos_command

    def setUp(self):
        super(TestExosCommandModule, self).setUp()

        self.mock_run_commands = patch('ansible_collections.community.general.plugins.modules.exos_command.run_commands')
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self):
        super(TestExosCommandModule, self).tearDown()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None):

        def load_from_file(*args, **kwargs):
            module, commands = args
            output = list()

            for item in commands:
                try:
                    obj = json.loads(item['command'])
                    command = obj['command']
                except ValueError:
                    command = item['command']
                filename = str(command).replace(' ', '_')
                output.append(load_fixture(filename))
            return output

        self.run_commands.side_effect = load_from_file

    def test_exos_command_simple(self):
        set_module_args(dict(commands=['show version']))
        result = self.execute_module()
        self.assertEqual(len(result['stdout']), 1)
        self.assertTrue(result['stdout'][0].startswith('Switch      :'))

    def test_exos_command_multiple(self):
        set_module_args(dict(commands=['show version', 'show version']))
        result = self.execute_module()
        self.assertEqual(len(result['stdout']), 2)
        self.assertTrue(result['stdout'][0].startswith('Switch      :'))

    def test_exos_command_wait_for(self):
        wait_for = 'result[0] contains "Switch      :"'
        set_module_args(dict(commands=['show version'], wait_for=wait_for))
        self.execute_module()

    def test_exos_command_wait_for_fails(self):
        wait_for = 'result[0] contains "test string"'
        set_module_args(dict(commands=['show version'], wait_for=wait_for))
        self.execute_module(failed=True)
        self.assertEqual(self.run_commands.call_count, 10)

    def test_exos_command_retries(self):
        wait_for = 'result[0] contains "test string"'
        set_module_args(dict(commands=['show version'], wait_for=wait_for, retries=2))
        self.execute_module(failed=True)
        self.assertEqual(self.run_commands.call_count, 2)

    def test_exos_command_match_any(self):
        wait_for = ['result[0] contains "Switch"',
                    'result[0] contains "test string"']
        set_module_args(dict(commands=['show version'], wait_for=wait_for, match='any'))
        self.execute_module()

    def test_exos_command_match_all(self):
        wait_for = ['result[0] contains "Switch"',
                    'result[0] contains "Switch      :"']
        set_module_args(dict(commands=['show version'], wait_for=wait_for, match='all'))
        self.execute_module()

    def test_exos_command_match_all_failure(self):
        wait_for = ['result[0] contains "Switch      :"',
                    'result[0] contains "test string"']
        commands = ['show version', 'show version']
        set_module_args(dict(commands=commands, wait_for=wait_for, match='all'))
        self.execute_module(failed=True)

    def test_exos_command_configure_error(self):
        commands = ['disable ospf']
        set_module_args({
            'commands': commands,
            '_ansible_check_mode': True,
        })
        result = self.execute_module()
        self.assertEqual(
            result['warnings'],
            ['only show commands are supported when using check mode, not executing `disable ospf`']
        )
