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
from ironic_integration_tests.tests.base import BaseTest
from ironic_integration_tests.common import output_parser as parser


class EnrollmentTest(BaseTest):
    def setUp(self):
        super(EnrollmentTest, self).setUp()
        self.delete_cmd = "ironic node-delete {0}"

    def test_single_node_enrollment(self):
        result = self.cli.execute_cmd("ironic node-create -d agent_ipmitool")
        node = parser.details(result)
        self.assertEqual(node.get("driver"), "agent_ipmitool")
        uuid = node.get("uuid")
        self.created_resources.append(uuid)

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

        result = self.cli.execute_cmd("ironic node-validate {0}".format(uuid))
        interfaces = parser.listing(result)
        for interface in interfaces:
            validate_result = interface.get("Result")
            self.assertNotEqual(
                validate_result, "False",
                "Validation failed for interface '{0}': {1}".format(
                    interface.get("Interface"), interface.get("Reason")))

    def test_bulk_node_enrollment(self):
        # create file
        # ironic create node.json
        # https://docs.openstack.org/python-ironicclient/latest/user/create_command.html
        pass
