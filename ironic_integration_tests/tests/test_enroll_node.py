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
from ironic_integration_tests.common.output_parser import listing, details_multiple


class EnrollmentTest(BaseTest):
    def setUp(self):
        self.delete_cmd = "ironic node-delete {0}"

    def test_single_node_enrollment(self):
        result = self.cli.execute_cmd("ironic node-create -d agent_ipmitool")
        node = details_multiple(result)
        print node
        result = self.cli.execute_cmd("ironic node-list")
        table_ = listing(result)
        print table_


        result = self.cli.execute_cmd("ironic node-validate")
        table_ = listing(result)
        print table_
        # ironic node-validate

    def test_bulk_node_enrollment(self):
        # create file
        # ironic create node.json
        # https://docs.openstack.org/python-ironicclient/latest/user/create_command.html
        pass