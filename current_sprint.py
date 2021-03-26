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

def counters(previous_counters, current_sprint, template):
    return {k: previous_counters.get(k,0) + current_sprint[k] for k in template.counters}

def averages(current_sprint, template):
    sprint_nr = current_sprint[template.sprint_nr_key]
    return {k: current_sprint[template.counters_key][k]/sprint_nr for k in template.averages}

def other_averages(previous_sprint, current_sprint, template):
    #Not the cleanest way but it avoids retrieving all history:
    #Calculate previous value as previous average * previous sprint nr
    # and then add the current value to finally calculate the new average 
    sprint_nr = current_sprint[template.sprint_nr_key]
    return {k: (previous_sprint[template.averages_key][k] * (sprint_nr - 1) + current_sprint[k])/sprint_nr for k in template.other_averages}

def custom(current_sprint, template):
    return {k: expression.evaluate(current_sprint) for k, expression in template.custom}

async def load_jsons(previous_sprint_file, current_sprint_file, template_file):
    async def load_json(file):
        async with aiofiles.open(file, 'r') as f:
            contents = await f.read()
        return json.loads(contents)
    
    previous_sprint = await load_json(previous_sprint_file)
    current_sprint = await load_json(current_sprint_file)
    template = await sprint_template.parse_template(template_file)

    return previous_sprint, current_sprint, template


def calculate_current_sprint_stats(previous_sprint, current_sprint, template):
    current_sprint.update(custom(current_sprint, template))
    current_sprint[template.counters_key] = counters(previous_sprint.get(template.counters_key,{}), current_sprint, template)
    current_sprint[template.averages_key] = averages(current_sprint, template)
    current_sprint[template.averages_key].update(other_averages(previous_sprint, current_sprint, template))
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
    
    if not check_sprint(current_sprint,template.keys_to_check_current()):
        return
    if not check_sprint(previous_sprint,template.keys_to_check_previous()):
        return

    current_sprint = calculate_current_sprint_stats(previous_sprint, current_sprint, template)

    if args.dry_run:
        print(json.dumps(current_sprint, indent=4 * ' '))
        return

    with open(args.current_sprint_file, "w") as output:
        json.dump(current_sprint, output, indent=4 * ' ')    

if __name__ == "__main__":
    # execute only if run as a script
    main()    