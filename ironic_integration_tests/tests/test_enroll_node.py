"""
Copyright 2017 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import time

from jinja2 import Environment, PackageLoader

from ironic_integration_tests.tests.base import BaseTest
from ironic_integration_tests.common import output_parser as parser
from ironic_integration_tests.common.config import get_config


class EnrollmentTests(BaseTest):

    def setUp(self):
        super(EnrollmentTests, self).setUp()
        self.delete_cmd = "ironic node-delete {0}"

    def test_single_node_enrollment(self):
        result = self.cli.execute_cmd("ironic node-create -d agent_ipmitool")
        node = parser.details(result)
        self.assertEqual(node.get("driver"), "agent_ipmitool")
        uuid = node.get("uuid")
        self.resource_deletion.append(self.delete_cmd.format(uuid))

        result = self.cli.execute_cmd("ironic node-show {0}".format(uuid))
        node = parser.details(result)
        self.assertEqual(node.get("provision_state"), "available")
        self.assertEqual(node.get("maintenance"), "False")

        result = self.cli.execute_cmd("ironic node-list")
        nodes = parser.listing(result)
        node_listed = False
        for node in nodes:
            if node.get("UUID") == uuid:
                node_listed = True
                break
        self.assertTrue(node_listed)

    def test_bulk_node_enrollment(self):
        # Set dynamic variables of nodes
        dell_name = self._random_name("dell_")
        hp_name = self._random_name("hp_")
        dell_ipmi_password = get_config("ironic", "dell_ipmi_password")
        hp_ipmi_password = get_config("ironic", "hp_ipmi_password")
        cmd = "glance image-list | awk '/ironic-deploy.initramfs/ {print $2}'"
        ramdisk = self.cli.execute_cmd(cmd)
        cmd = "glance image-list | awk '/ironic-deploy.kernel/ {print $2}')"
        kernel = self.cli.execute_cmd(cmd)

        # Create the nodes JSON file
        env = Environment(
            loader=PackageLoader('ironic_integration_tests', 'templates'))
        template = env.get_template('nodes.json.j2')
        template_rendered = template.render(
            dell_name=dell_name,
            dell_ipmi_password=dell_ipmi_password,
            hp_name=hp_name,
            hp_ipmi_password=hp_ipmi_password,
            deploy_ramdisk=ramdisk,
            deploy_kernel=kernel)
        f = open('nodes.json', 'w')
        f.write(template_rendered)

        # Create the nodes
        cmd = "ironic --ironic-api-version 1.22 create nodes.json"
        self.cli.execute_cmd(cmd)
        cmd = "ironic node-list"
        result = self.cli.execute_cmd(cmd)
        nodes = parser.listing(result)
        self.assertGreaterEqual(len(nodes), 2, "Nodes not created")

        # Verify node properties
        cmd = "ironic node-show {0}".format(dell_name)
        result = self.cli.execute_cmd(cmd)
        dell_node = parser.details(result)
        # check some values
        cmd = "ironic node-show {0}".format(hp_name)
        result = self.cli.execute_cmd(cmd)
        hp_node = parser.details(result)
        # check some values

        # Set provision states
        cmd = 'ironic --ironic-api-version 1.22 node-set-provision-state ' \
              '"{0}" manage'.format(dell_name)
        self.cli.execute_cmd(cmd)
        cmd = 'ironic --ironic-api-version 1.22 node-set-provision-state ' \
              '"{0}" manage'.format(hp_name)
        self.cli.execute_cmd(cmd)

        time.sleep(60)

        cmd = 'ironic --ironic-api-version 1.22 node-set-provision-state ' \
              '"{0}" provide'.format(dell_name)
        self.cli.execute_cmd(cmd)
        cmd = 'ironic --ironic-api-version 1.22 node-set-provision-state ' \
              '"{0}" provide'.format(hp_name)
        self.cli.execute_cmd(cmd)

        # Verify states of nodes
        cmd = "ironic node-show {0}".format(dell_name)
        result = self.cli.execute_cmd(cmd)
        dell_node = parser.details(result)
        self.assertEqual(dell_node.get("provision_state"), "available")
        self.assertEqual(dell_node.get("maintenance"), "False")

        cmd = "ironic node-show {0}".format(hp_name)
        result = self.cli.execute_cmd(cmd)
        hp_node = parser.details(result)
        self.assertEqual(hp_node.get("provision_state"), "available")
        self.assertEqual(hp_node.get("maintenance"), "False")
