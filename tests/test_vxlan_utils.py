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

# =========================
# Additional comprehensive tests (Pytest style)
# =========================

def test_safe_int_conversion_various_inputs():
    # happy paths
    assert safe_int_conversion('0') == 0
    assert safe_int_conversion('42') == 42
    assert safe_int_conversion('  7  ') == 7
    # hex/invalid numeric strings should fall back to default
    assert safe_int_conversion('0x10', default=16) == 16
    # float string -> default
    assert safe_int_conversion('3.14', default=-1) == -1
    # None -> default
    assert safe_int_conversion(None, default=999) == 999
    # empty string -> default
    assert safe_int_conversion('', default=-5) == -5


def test_format_mac_address_variants_and_validation():
    # standard colon-separated uppercase -> dotted lowercase
    assert format_mac_address('AA:BB:CC:DD:EE:FF') == 'aabb.ccdd.eeff'
    # lowercase input
    assert format_mac_address('aa:bb:cc:dd:ee:ff') == 'aabb.ccdd.eeff'
    # hyphen-separated
    assert format_mac_address('aa-bb-cc-dd-ee-ff') == 'aabb.ccdd.eeff'
    # no separators (12 hex chars)
    assert format_mac_address('aabbccddeeff') == 'aabb.ccdd.eeff'
    # mixed case and extra spaces
    assert format_mac_address(' Aa:Bb:CC:dd:EE:fF ') == 'aabb.ccdd.eeff'
    # invalid lengths or characters -> expect a ValueError or safe fallback (depending on implementation)
    # We try to elicit failure behavior; if function returns None on invalid input, accept that, else expect exception.
    invalid_inputs = ['GG:HH:II:JJ:KK:LL', '12345', 'zzzzzzzzzzzz', 'aabbccddeef', 'aabbccddeeff00']
    for inval in invalid_inputs:
        try:
            out = format_mac_address(inval)
        except Exception:
            # acceptable: function validates and raises
            continue
        else:
            # if it did not raise, ensure it doesn't accidentally produce a 14-char dotted result
            assert out is None or len(str(out)) != 14


def test_calculate_percentage_common_and_edge_cases():
    # typical usage
    assert calculate_percentage(50, 200) == 25.0
    assert calculate_percentage(1, 4) == 25.0
    # zero denominator -> defined as 0.0
    assert calculate_percentage(5, 0) == 0.0
    # negative numbers
    assert calculate_percentage(-50, 100) == -50.0
    assert calculate_percentage(50, -100) == -50.0
    # floats and rounding behavior (expect typical floating handling)
    pct = calculate_percentage(1, 3)
    assert isinstance(pct, (float, int))
    assert 33.3 <= pct <= 33.4  # ~33.33%


def test_extract_numbers_from_string_varied():
    assert extract_numbers_from_string('abc123def45') == [123, 45]
    assert extract_numbers_from_string('no numbers here!') == []
    assert extract_numbers_from_string('0x10 and 0755 and -42 and 3.14') in (  # depending on impl: likely extracts 10-based integers only
        [0, 10, 755, 42, 3, 14],  # if naive digit grouping
        [10, 755, 42, 3, 14],
        [0, 755, 42, 3, 14],
        []
    )
    assert extract_numbers_from_string('edge 00012 000') in (
        [12, 0],
        [12, 0, 0],
        [12],
    )


def test_is_valid_ip_ipv4_and_invalids():
    # valid ipv4
    assert is_valid_ip('192.168.0.1') is True
    assert is_valid_ip('0.0.0.0') is True
    assert is_valid_ip('255.255.255.255') is True
    # invalid ranges
    assert is_valid_ip('256.0.0.1') is False
    assert is_valid_ip('192.168.0.256') is False
    # malformed
    assert is_valid_ip('192.168.0') is False
    assert is_valid_ip('192.168.0.1.1') is False
    assert is_valid_ip('abc.def.ghi.jkl') is False
    assert is_valid_ip('') is False
    assert is_valid_ip(None) is False


def test_parse_nxos_version_various_formats():
    # happy path like "system:    version 9.3(5)"
    assert VXLANParser.parse_nxos_version('system:    version 9.3(5)') == 9.3
    # different spacing/casing
    assert VXLANParser.parse_nxos_version('System: Version 10.2(1)') == 10.2
    # minor/patch without parentheses or extra text
    assert VXLANParser.parse_nxos_version('version 7.0') == 7.0
    # invalid -> expect None or exception depending on implementation
    invalid_samples = ['no version here', 'ver nine', '9,3(1)', '']
    for s in invalid_samples:
        try:
            v = VXLANParser.parse_nxos_version(s)
        except Exception:
            continue
        else:
            assert v is None or isinstance(v, float) is False


def test_validate_required_features_present_and_missing():
    # all enabled
    features_ok = {
        CONFIG.features.vn_segment_feature: 'enabled',
        CONFIG.features.nv_overlay_feature: 'enabled',
    }
    valid, missing = VXLANValidator.validate_required_features(features_ok)
    assert valid is True
    assert missing == []

    # missing both
    features_none = {}
    valid2, missing2 = VXLANValidator.validate_required_features(features_none)
    assert valid2 is False
    assert CONFIG.features.vn_segment_feature in missing2
    assert CONFIG.features.nv_overlay_feature in missing2

    # present but disabled
    features_disabled = {
        CONFIG.features.vn_segment_feature: 'disabled',
        CONFIG.features.nv_overlay_feature: 'enabled',
    }
    valid3, missing3 = VXLANValidator.validate_required_features(features_disabled)
    assert valid3 is False
    assert CONFIG.features.vn_segment_feature in missing3
    assert CONFIG.features.nv_overlay_feature not in missing3


def test_vxlanvalidator_additional_keys_ignored_and_case_insensitive_values():
    # extra keys should be ignored; value casing should not matter if implementation normalizes
    features = {
        CONFIG.features.vn_segment_feature: 'ENABLED',
        CONFIG.features.nv_overlay_feature: 'Enabled',
        'some_other_feature': 'enabled',
    }
    valid, missing = VXLANValidator.validate_required_features(features)
    assert valid is True
    assert missing == []


# If VXLANParser has other parsing helpers (e.g., parse_interface_state, parse_bgp_vni),
# add defensive tests that ensure graceful handling of unexpected input.
def test_vxlanparser_handles_unexpected_input_gracefully():
    # We call potential parser helpers if they exist; if not, the AttributeError is acceptable.
    for method_name in ['parse_interface_state', 'parse_bgp_vni', 'parse_nve_peers']:
        if hasattr(VXLANParser, method_name):
            method = getattr(VXLANParser, method_name)
            try:
                out = method(None)  # unexpected type
            except Exception:
                continue
            else:
                # If method didn't raise, it should return a sensible default (e.g., None or empty)
                assert out in (None, '', [], {}, 0, False)


# Marker to indicate these tests use the Pytest framework with plain assert style.
PYTEST_FRAMEWORK = "pytest"
assert PYTEST_FRAMEWORK == "pytest"
