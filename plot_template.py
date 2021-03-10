import aiofiles
import simplejson as json
import asyncio

class Axes_Template:

    def __init__(self, json_dict):
        self.x_label = json_dict["x_label"]
        self.y_label = json_dict["y_label"]
        self.plots = json_dict["plots"]
    
    def plot(self, label):
        matching = [plot for plot in self.plots if plot["label"] == label]
        return matching[0] if matching else None


class Plot_Template:

    def __init__(self, json_dict):
        self.title = json_dict["title"]
        self.rows = json_dict["rows"]
    
    def columns_subplots(self):
        return max(len(r["subplots"]) for r in self.rows)

    def labels(self):
        return [plot["label"] for r in self.rows for subplot in r["subplots"] for plot in subplot["plots"] ]

    def items(self):
        return [plot["item"] for r in self.rows for subplot in r["subplots"] for plot in subplot["plots"] ]

    def axes(self, y, x):
        axes_dict = self.rows[y]["subplots"][x]
        return Axes_Template(axes_dict) if axes_dict else None

async def parse_template(file):
    async with aiofiles.open(file, 'r') as f:
        contents = await f.read()
    template_dict = json.loads(contents)
    return Plot_Template(template_dict)


