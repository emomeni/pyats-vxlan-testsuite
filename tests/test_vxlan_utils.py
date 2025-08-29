import os
import sys

# Add the path to the 'modular architecture' directory so modules can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODULE_DIR = os.path.join(PROJECT_ROOT, 'modular architecture')
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from vxlan_utils import (
    VXLANParser,
    VXLANValidator,
    safe_int_conversion,
    format_mac_address,
    calculate_percentage,
    extract_numbers_from_string,
    is_valid_ip,
)
from vxlan_config import CONFIG


def test_safe_int_conversion():
    assert safe_int_conversion('10') == 10
    assert safe_int_conversion('invalid', default=5) == 5


def test_format_mac_address():
    assert format_mac_address('AA:BB:CC:DD:EE:FF') == 'aabb.ccdd.eeff'


def test_calculate_percentage():
    assert calculate_percentage(50, 200) == 25.0
    assert calculate_percentage(5, 0) == 0.0


def test_extract_numbers_from_string():
    assert extract_numbers_from_string('abc123def45') == [123, 45]


def test_is_valid_ip():
    assert is_valid_ip('192.168.0.1') is True
    assert is_valid_ip('999.999.999.999') is False


def test_parse_nxos_version():
    sample_output = 'system:    version 9.3(5)'
    assert VXLANParser.parse_nxos_version(sample_output) == 9.3


def test_validate_required_features():
    features = {
        CONFIG.features.vn_segment_feature: 'enabled',
        CONFIG.features.nv_overlay_feature: 'enabled',
    }
    valid, missing = VXLANValidator.validate_required_features(features)
    assert valid is True
    assert missing == []

    features = {}
    valid, missing = VXLANValidator.validate_required_features(features)
    assert valid is False
    assert CONFIG.features.vn_segment_feature in missing
    assert CONFIG.features.nv_overlay_feature in missing
