import pytest

from sprint_stats.current_sprint import check_sprint, counters, averages, other_averages, custom
from sprint_stats.sprint_template import Sprint_Template

@pytest.fixture
def nested_obj():
    return {
        "level_1" : {
            "level_2": "not relevant"
        },
        "path": ["level_1.level_2"]
    }

@pytest.fixture
def counters_obj():
    return {
        "key_1": 10,
        "key_2": 20
    }

@pytest.fixture
def current_obj():
    return {
        "sprint_nr": 3,
        "key_1": 1,
        "key_2": 2,
        "key_3": 3,
        "another_counter_key":4
    }

@pytest.fixture
def current_obj_with_counters(current_obj, counters_obj):
    current_obj["counters"] = counters_obj
    return current_obj

@pytest.fixture
def previous_sprint():
    return {
        "sprint_nr": 2,
        "averages": {
            "key_1": 5.0,
            "key_2": 10.0,
            "key_3": 15.0
        }
    }        

@pytest.fixture
def previous_obj_with_counters(previous_sprint, counters_obj):
    previous_sprint["counters"] = counters_obj
    return previous_sprint

@pytest.fixture
def template():
    json_dict = {
        "counters": ["key_1","key_2", "another_counter_key"],
        "averages": ["key_1", "key_2"],
        "other_averages": ["key_3"],
        "keys": {
            "sprint_nr": "sprint_nr"
        },
        "custom": [
            {
                "key": "key_4",
                "expression": {
                    "operation": '-',
                    "expression_1": 5,
                    "expression_2": "key_1"
                }
            }
        ]
    }
    return Sprint_Template(json_dict)

def test_check_sprint(nested_obj):
    assert check_sprint(nested_obj, nested_obj["path"])
    assert not check_sprint(nested_obj, ["not_existing", "not_existing.sublevel"]) 

def test_counters(counters_obj, current_obj, template):
    new_counters = counters(counters_obj, current_obj, template)
    assert new_counters["key_1"] == 11
    assert new_counters["key_2"] == 22
    assert new_counters["another_counter_key"] == 4

def test_averages(current_obj_with_counters, template):
    new_averages = averages(current_obj_with_counters, template)
    assert new_averages["key_1"] == 10.0/3
    assert new_averages["key_2"] == 20.0/3

def test_other_averages(previous_sprint, current_obj, template):
    new_averages = other_averages(previous_sprint, current_obj, template)
    assert new_averages["key_3"] == (33.0/3)

def test_custom(current_obj, template):
    new_custom = custom(current_obj, template)
    print(new_custom)
    assert new_custom["key_4"] == 4
