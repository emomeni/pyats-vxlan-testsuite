#!/usr/bin/env python3
"""VXLAN Configuration Validation Test Suite."""
import logging
import argparse
from pyats import aetest
from pyats.topology import loader

from tests.common import CommonSetup, CommonCleanup
from tests.feature import VxlanFeatureValidation
from tests.interface import VxlanInterfaceValidation
from tests.vni import VxlanVniValidation
from tests.l3vni import VxlanL3VniValidation
from tests.bgp import VxlanBgpValidation
from tests.mac import VxlanMacAddressValidation
from tests.multicast import VxlanMulticastValidation
from tests.health import VxlanHealthCheck

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VXLAN Validation Test Suite')
    parser.add_argument('--testbed', required=True, help='Testbed YAML file')
    args = parser.parse_args()

    testbed = loader.load(args.testbed)

    aetest.main(testbed=testbed)
