import simplejson as json
import argparse

def counters(previous_counters, current_sprint):
    return {k: v + current_sprint[k] for k,v in previous_counters.items()}

def averages(counters, sprint_nr):
    return {k: v/sprint_nr for k, v in counters.items()}

def load_averages(previous_sprint, current_load, sprint_nr):
    #Not the cleanest way but it avoids retrieving all history
    previous_value_points_person_cum = previous_sprint["averages"]["points_person"] * previous_sprint["sprint_nr"]
    new_value_points_person = (current_load["points_person"] + previous_value_points_person_cum)/sprint_nr
    previous_value_points_person_day_cum = previous_sprint["averages"]["points_person_day"] * previous_sprint["sprint_nr"]
    new_value_points_person_day = (current_load["points_person_day"] + previous_value_points_person_day_cum)/sprint_nr
    return (new_value_points_person, new_value_points_person_day)

def load_on_current_sprint(current_sprint):
    load = {}
    load["points_person"] = current_sprint["validated_points"]/current_sprint["nr_team_members"]
    load["points_person_day"] = current_sprint["validated_points"]/current_sprint["working_days"]
    return load

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--previous_sprint_file", required=True)
    parser.add_argument("-c", "--current_sprint_file", required=True)
    args = parser.parse_args()
    with open(args.previous_sprint_file) as json_data_previous, open(args.current_sprint_file) as json_data_current:
        previous_sprint = json.load(json_data_previous)
        current_sprint = json.load(json_data_current)

    sprint_nr = current_sprint["sprint_nr"]
    current_sprint["load"] = load_on_current_sprint(current_sprint)
    current_sprint["counters"] = counters(previous_sprint["counters"], current_sprint)
    current_sprint["averages"] = averages(current_sprint["counters"], sprint_nr)
    new_points_person, new_points_person_day = load_averages(previous_sprint, current_sprint["load"], sprint_nr)
    current_sprint["averages"]["points_person"] = new_points_person
    current_sprint["averages"]["points_person_day"] = new_points_person_day

    with open(args.current_sprint_file, "w") as output:
        json.dump(current_sprint, output, indent=4 * ' ')    

if __name__ == "__main__":
    # execute only if run as a script
    main()    
