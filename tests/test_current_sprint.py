import pytest

from sprint_stats.current_sprint import check_sprint, counters, averages, load_averages

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
        "key_1": 1,
        "key_2": 2
    }

@pytest.fixture
def previous_sprint():
    return {
        "sprint_nr": 2,
        "averages": {
            "key_1": 5.0,
            "key_2": 10.0
        }
    }        

def test_check_sprint(nested_obj):
    assert check_sprint(nested_obj, nested_obj["path"])
    assert not check_sprint(nested_obj, ["not_existing", "not_existing.sublevel"]) 

def test_counters(counters_obj, current_obj):
    new_counters = counters(counters_obj, current_obj)
    assert new_counters["key_1"] == 11
    assert new_counters["key_2"] == 22

def test_averages(counters_obj):
    new_averages = averages(counters_obj, 2)
    assert new_averages["key_1"] == 5.0
    assert new_averages["key_2"] == 10.0

def test_load_averages(previous_sprint, current_obj):
    new_averages = load_averages(previous_sprint, current_obj, 3)
    assert new_averages["key_1"] == (11.0/3)
    assert new_averages["key_2"] == (22.0/3)

