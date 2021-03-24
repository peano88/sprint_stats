from expression_parser import parse_expression
import aiofiles
import simplejson as json

class Sprint_Template:

    def __init__(self, json_dict):
        self.counters = json_dict["counters"]
        self.averages = json_dict["averages"]
        self.other_averages = json_dict["other_averages"]
        self.sprint_nr_key = json_dict["keys"]["sprint_nr"]
        self.custom = [(c["key"], parse_expression(c["expression"]) ) for c in json_dict.get("custom", [])]


async def parse_template(file):
    async with aiofiles.open(file, 'r') as f:
        contents = await f.read()
    template_dict = json.loads(contents)
    return Sprint_Template(template_dict)