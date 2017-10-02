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


class InstanceTest(BaseTest):

    def test_boot_instance(self):
        result = self.execute_cmd("nova boot --flavor tempest1 --image cirros test1")
        server = details_multiple(result)
        print server
        result = self.execute_cmd("nova list")
        server_list = listing(result)
        print server_list
