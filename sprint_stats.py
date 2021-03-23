import simplejson as json
import argparse
import functools

def check_sprint(sprint, keys):
    def multi_level_check(sprint, key):
        try:
            key_path = key.split('.')
            functools.reduce(lambda obj, path: obj[path], key_path, sprint)
        except KeyError:
            print("Key {} not found in object".format(key))

    [multi_level_check(sprint, k) for k in keys]

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--previous_sprint_file", required=True)
    parser.add_argument("-c", "--current_sprint_file", required=True)
    parser.add_argument("-d", "--dry-run", dest="dry_run", action="store_true")
    parser.set_defaults(dry_run=False)
    args = parser.parse_args()

    with open(args.previous_sprint_file) as json_data_previous, open(args.current_sprint_file) as json_data_current:
        previous_sprint = json.load(json_data_previous)
        current_sprint = json.load(json_data_current)
    
    check_sprint(current_sprint,["sprint_nr","validated_points", "nr_team_members", "working_days"])
    check_sprint(previous_sprint, ["counters","averages"])

    sprint_nr = current_sprint["sprint_nr"]
    current_sprint["load"] = load_on_current_sprint(current_sprint)
    current_sprint["counters"] = counters(previous_sprint["counters"], current_sprint)
    current_sprint["averages"] = averages(current_sprint["counters"], sprint_nr)
    current_sprint["averages"].update(load_averages(previous_sprint, current_sprint["load"], sprint_nr))

    if args.dry_run:
        print(json.dumps(current_sprint, indent=4 * ' '))
        return

    with open(args.current_sprint_file, "w") as output:
        json.dump(current_sprint, output, indent=4 * ' ')    

if __name__ == "__main__":
    # execute only if run as a script
    main()    