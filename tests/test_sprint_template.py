import pytest

from sprint_stats.sprint_template import Sprint_Template

@pytest.fixture
def json_dict():
    return {
        "counters": ["counter_key_1", "counter_key_2"],
        "averages": ["average_key_1"],
        "other_averages": ["other_average_key_1"],
        "keys": {"sprint_nr": "nr"}
    }

@pytest.fixture
def json_dict_with_custom(json_dict):
    json_dict["keys"]["custom"] = {
        "key": "custom_key_1",
        "expression": {
            "operation": '+',
            "expression_1": 2,
            "expression_2": "key_2"
        }
    }

def test_sprint_template(json_dict):
    sprint_template = Sprint_Template(json_dict)
    counters = sprint_template.counters
    assert len(counters) == 2
    averages = sprint_template.averages
    assert len(averages) == 1 
    other_averages = sprint_template.other_averages
    assert len(other_averages) == 1
    assert sprint_template.sprint_nr_key == "nr" 
    assert len(sprint_template.custom) == 0

def test_sprint_template_with_custom(json_dict_with_custom):
    sprint_template = Sprint_Template(json_dict_with_custom)
    custom = sprint_template.custom
    assert len(custom) == 0
    assert all(isinstance(e, Expression) for _,e in custom)