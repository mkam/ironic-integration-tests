# Ironic Integration Tests
This repository contains integration tests designed to run in a lab environment.

## Prerequisites
The python package requirements for running tests can be installed with:

```
pip install -r requirements.txt
```

Each test has different prerequisites, but in general, the lab environment should
 have the following:
 
- At least one ironic node enrolled
- All ironic images and flavors created and uploaded

Additional requirements for the "bolt-on," multihypervisor scenario:
- A virtual image and flavor created and uploaded

The ironic only requirements should be met as part of the deployment process.
For the virtual image and flavor, these can be created manually or by running
the setup for tempest.
```
$ cd /opt/rpc/openstack
$ openstack-ansible --tags tempest_install scripts/run_tempest.yml
```

## Running Tests
The tests can be run using any test runner, but these instructions will use 
[nose](http://nose.readthedocs.io/en/latest/). Nose is installed by default
with tempest, so the version being used will be the same as the one in tempest.

The tests utilize the environment variables for authentication and assume the 
user has admin permissions. This can be set by running the following command 
before executing the tests. To run all tests:
```
$ source ~/openrc
$ source /openstack/venvs/tempest-*/bin/activate
$ nosetests -sv ironic_integration_tests.tests
```
Example of running a specific test:
```
$ source ~/openrc
$ source /openstack/venvs/tempest-*/bin/activate
$ nosetests -sv ironic_integration_tests.tests.test_create_instance.py:InstanceTests.test_boot_instance_centos7
```

To create logs, run `nosetests -sv --nologcapture`. To run without cleanup, use `export SKIP_CLEANUP=true`.