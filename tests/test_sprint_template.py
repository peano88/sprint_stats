import pytest

from sprint_stats.sprint_template import Sprint_Template
import sprint_stats.expression_parser as expression_parser

@pytest.fixture
def json_dict():
    return {
        "counters": ["key_1", "key_2"],
        "averages": ["key_1", "key_3"],
        "other_averages": ["other_average_key_1"],
        "keys": {"sprint_nr": "nr"}
    }

@pytest.fixture
def json_dict_with_custom(json_dict):
    json_dict["custom"] = [{
        "key": "key_3",
        "expression": {
            "operation": '+',
            "expression_1": 2,
            "expression_2": "key_2"
        }
    }]
    return json_dict

def test_sprint_template(json_dict):
    sprint_template = Sprint_Template(json_dict)
    counters = sprint_template.counters
    assert len(counters) == 2
    averages = sprint_template.averages
    assert len(averages) == 2
    other_averages = sprint_template.other_averages
    assert len(other_averages) == 1
    assert sprint_template.sprint_nr_key == "nr" 
    assert sprint_template.counters_key == "counters" 
    assert sprint_template.averages_key == "averages" 
    assert len(sprint_template.custom) == 0

def test_sprint_template_with_custom(json_dict_with_custom):
    sprint_template = Sprint_Template(json_dict_with_custom)
    custom = sprint_template.custom
    assert len(custom) == 1
    #_, e = custom[0]
    #assert isinstance(e, expression_parser.Binary_Expression)
    #assert all([isinstance(e, expression_parser.Binary_Expression) for _,e in custom])

def test_keys_to_check_current(json_dict_with_custom):
    sprint_template = Sprint_Template(json_dict_with_custom)
    keys_to_check = sprint_template.keys_to_check_current()
    assert "nr" in keys_to_check
    assert "key_1" in keys_to_check
    assert "key_2" in keys_to_check
    assert "key_3" not in keys_to_check

def test_keys_to_check_current(json_dict):
    sprint_template = Sprint_Template(json_dict)
    keys_to_check = sprint_template.keys_to_check_previous()
    assert "nr" in keys_to_check
    