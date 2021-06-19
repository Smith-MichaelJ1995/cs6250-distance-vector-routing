import sys
from os import listdir
from os.path import isfile, join
from Topology import *
from output_validator_test import validateStudentOutput

topos_path = 'test/topos/'  # dir of test topologies
my_logs_path = 'test/my_logs/'  # dir for your logs
correct_logs_path = 'test/correct_logs/'  # dir for assumed correct logs

def run_topo_func(topo_name):
        # Start up the logfile
        open_log(my_logs_path + topo_name + '.log')

        # Populate the topology
        topo = Topology(topos_path + topo_name + '.txt')

        # Run the topology.
        topo.run_topo()

        # Close the logfile
        finish_log()

def get_read_limits(file):
    lines = file.readlines()
    num_lines = len(lines)

    dash_count = 0
    start_index = 0
    end_index = num_lines

    for i in range(num_lines - 1, -1, -1):
        if '-----' in lines[i]:
            dash_count += 1
        
        if dash_count == 2:
            start_index = i + 1
            break

    return lines, start_index, end_index

sys.path.insert(0, topos_path)
files = [f for f in listdir(topos_path) if isfile(join(topos_path, f))]

num_topos = len(files)
num_topos_correct = num_topos

for file in files:
    topo_name = file[:-4]

    # Process the topology
    run_topo_func(topo_name)

    # Validate formatting of student output
    validateStudentOutput(my_logs_path + topo_name + '.log')

    # Compare my final logs with the correct final logs
    with open(my_logs_path + topo_name + '.log') as my_logs, open(correct_logs_path + topo_name + '.log') as correct_logs:
        my_logs_lines, my_logs_start_index, my_logs_end_index = get_read_limits(my_logs)
        my_logs_lines_to_compare = my_logs_lines[my_logs_start_index : my_logs_end_index]
        
        correct_logs_lines, correct_logs_start_index, correct_logs_end_index = get_read_limits(correct_logs)
        correct_logs_lines_to_compare = correct_logs_lines[correct_logs_start_index : correct_logs_end_index]

        if my_logs_lines_to_compare != correct_logs_lines_to_compare:
            print(topo_name + ' = False')
            num_topos_correct -= 1

print('\n' + str(num_topos_correct) + '/' + str(num_topos) + ' correct topos!')
