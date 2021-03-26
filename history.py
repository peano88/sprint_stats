import aiofiles
import simplejson as json
import asyncio
import matplotlib.pyplot as pyplot
import plot_template

from argparse import ArgumentParser
from pathlib import Path

async def open_and_parse_file(file):
    async with aiofiles.open(file, 'r') as f:
        contents = await f.read()
    return json.loads(contents)

def extract_points(sprint, items):
    sprint_nr = sprint["sprint_nr"]
    def value(label_path):
        json_path = label_path.split('.')
        obj = sprint
        for path in json_path:
            obj = obj[path]
        return obj

    return {l: (sprint_nr, value(l)) for l in items}

async def analyze_file(file, items):
    fileParsed = await open_and_parse_file(file)
    return extract_points(fileParsed, items)


def create_point_list(sprint_points, item):
    item_points = [p[item] for p in sprint_points]
    item_points.sort(key=lambda elem: elem[0]) # sort based on sprint nr
    sprints, values = zip(*item_points)
    return (sprints, values)

def plot(points, pl_template):
    raws_subplots = len(pl_template.rows)
    columns_subplots = pl_template.columns_subplots()
    #fig, axs = pyplot.subplots(raws_subplots, columns_subplots)
    fig = pyplot.figure()
    for i,r in enumerate(pl_template.rows):
        for j,p in enumerate(r["subplots"]):
            print('position: {}'.format(1 + i * columns_subplots + j))
            ax = fig.add_subplot(raws_subplots, columns_subplots, 1 + i * columns_subplots + j)
            print(ax)
            axes = pl_template.axes(i,j)
            ax.set_xlabel(axes.x_label)
            ax.set_ylabel(axes.y_label)
            for pl in axes.plots:
                xs, ys = points[pl["item"]]
                ax.plot(xs,ys, label=pl["label"])
            ax.legend()

    fig.savefig("test1.png")    


async def analyze_files(files, template):
    pl_template = await plot_template.parse_template(template)
    items = pl_template.items()
    tasks = []
    for f in files:
        tasks.append(
            analyze_file(f, items)
        )
    
    points = await asyncio.gather(*tasks)

    tasks.clear()
    points_for_plot = {}
    for item in items:
        points_for_plot[item] = create_point_list(points, item)
    
    plot(points_for_plot, pl_template)

def list_json_files(path):
    json_folder = Path(path).rglob('*.json')
    return [x for x in json_folder]

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--data-directory", "-d", dest="data_directory", required=True)
    arg_parser.add_argument("--template", "-t", required=True)
    args = arg_parser.parse_args()
    files = list_json_files(args.data_directory)
     
    asyncio.run(analyze_files(files, args.template))

if __name__ == "__main__":
    # execute only if run as a script
    main()    



