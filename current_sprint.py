import simplejson as json
import argparse
import functools
import aiofiles
import sprint_template
import asyncio

def check_sprint(sprint, keys):
    def multi_level_check(sprint, key):
        try:
            key_path = key.split('.')
            functools.reduce(lambda obj, path: obj[path], key_path, sprint)
            return True
        except KeyError:
            print("Key {} not found in object".format(key))
            return False

    return all([multi_level_check(sprint, k) for k in keys])

def counters(previous_counters, current_sprint):
    return {k: v + current_sprint[k] for k,v in previous_counters.items()}

def averages(counters, sprint_nr):
    return {k: v/sprint_nr for k, v in counters.items()}

def load_averages(previous_sprint, current_load, sprint_nr):
    #Not the cleanest way but it avoids retrieving all history:
    #Calculate previous value as previous average * previous sprint nr
    # and then add the current value to finally calculate the new average 
    return {k: (previous_sprint["averages"][k] * (sprint_nr - 1) + v)/sprint_nr for k,v in current_load.items()}

def load_on_current_sprint(current_sprint):
    load = {}
    load["points_person"] = current_sprint["validated_points"]/current_sprint["nr_team_members"]
    load["points_person_day"] = current_sprint["validated_points"]/current_sprint["working_days"]
    return load

async def load_jsons(previous_sprint_file, current_sprint_file, template_file):
    async def load_json(file):
        async with aiofiles.open(file, 'r') as f:
            contents = await f.read()
        return json.loads(contents)
    
    previous_sprint = await load_json(previous_sprint_file)
    current_sprint = await load_json(current_sprint_file)
    template = await sprint_template.parse_template(template_file)

    return previous_sprint, current_sprint, template


def calculate_current_sprint_stats(previous_sprint, current_sprint):
    sprint_nr = current_sprint["sprint_nr"]
    current_sprint["load"] = load_on_current_sprint(current_sprint)
    current_sprint["counters"] = counters(previous_sprint["counters"], current_sprint)
    current_sprint["averages"] = averages(current_sprint["counters"], sprint_nr)
    current_sprint["averages"].update(load_averages(previous_sprint, current_sprint["load"], sprint_nr))
    return current_sprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--previous_sprint_file", required=True)
    parser.add_argument("-c", "--current_sprint_file", required=True)
    parser.add_argument("-t", "--template-file", required=True)
    parser.add_argument("-d", "--dry-run", dest="dry_run", action="store_true")
    parser.set_defaults(dry_run=False)
    args = parser.parse_args()

    previous_sprint, current_sprint, template = asyncio.run(load_jsons(args.previous_sprint_file, args.current_sprint_file, args.template_file))
    
    if not check_sprint(current_sprint,["sprint_nr","validated_points", "nr_team_members", "working_days"]):
        return
    if not check_sprint(previous_sprint, ["counters","averages"]):
        return

    current_sprint = calculate_current_sprint_stats(previous_sprint, current_sprint)

    if args.dry_run:
        print(json.dumps(current_sprint, indent=4 * ' '))
        return

    with open(args.current_sprint_file, "w") as output:
        json.dump(current_sprint, output, indent=4 * ' ')    

if __name__ == "__main__":
    # execute only if run as a script
    main()    