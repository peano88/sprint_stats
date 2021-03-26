from expression_parser import parse_expression
import aiofiles
import simplejson as json

class Sprint_Template:

    def __init__(self, json_dict):
        self.counters = json_dict.get("counters",[])
        self.averages = json_dict.get("averages",[])
        self.other_averages = json_dict.get("other_averages",[])
        self.sprint_nr_key = json_dict["keys"].get("sprint_nr","sprint_nr")
        self.counters_key = json_dict["keys"].get("counters","counters")
        self.averages_key = json_dict["keys"].get("averages","averages")
        self.custom = [(c["key"], parse_expression(c["expression"]))  for c in json_dict.get("custom", [])]
    
    def keys_to_check_current(self):
        keys = {self.sprint_nr_key}
        keys.update(self.counters)
        keys.update(self.averages)
        keys = keys.difference({k for k,_ in self.custom})
        return keys

    def keys_to_check_previous(self):
        return {self.sprint_nr_key}

async def parse_template(file):
    async with aiofiles.open(file, 'r') as f:
        contents = await f.read()
    template_dict = json.loads(contents)
    return Sprint_Template(template_dict)