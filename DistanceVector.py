# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *


class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        
        # TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data
        self.distanceVector = {
            "{}".format(self.name): 0,
        }

        # detect negative loops
        self.negativeCycleMonitor = []

    # given vector & proposedCost, check for negative loop
    def check_negative_cycle(self, vector_name, proposedCost):

        # traverse through datastructure
        return True if (vector_name in self.negativeCycleMonitor) and (self.negativeCycleMonitor[vector_name]['cost'] == proposedCost) else False



    # deliver initial messages to neighboring distance vectors
    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py
        for incoming_link in self.incoming_links:
            self.send_msg(
                msg = {
                    "origin_node": self.name,
                    "origin_node_distance_vector": self.distanceVector
                },
                dest = incoming_link.name
            )

    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages  
        # data-structure to track change of internal distance vector components 
        hasChangeOccured = False   

        for index, msg in enumerate(self.messages):
            
            # extrapolate local variables
            origin_node = msg['origin_node']
            origin_node_distance_vector = msg['origin_node_distance_vector']

            # traverse through all nodes in messages distance vector
            for vector_name, vector_weight in origin_node_distance_vector.items():

                # only process a vector if it's not the current node,
                # a node will always reach itself at length zero
                if self.name != vector_name:

                    # use builtin function to get weight for origin node
                    costToOrigin = self.get_outgoing_neighbor_weight(origin_node)

                    # adding sum of distance vector 
                    proposedCost = int(vector_weight) + int(costToOrigin)

                    # handle case where we need to add a new vector to our DV
                    if vector_name not in self.distanceVector:
                        
                        # add the new vector at the proposed cost
                        self.distanceVector[vector_name] = proposedCost

                        # regardless, send message if change occurs
                        hasChangeOccured = True

                    else:

                        # in situation of self.distanceVector[vector_name] == -99, 
                        # we know that no changes need to be made at this vector in the distance vector 
                        if self.distanceVector[vector_name] != -99:

                            # handle case if cost drops below -99, this is our base case..
                            if proposedCost <= -99:

                                # set to negative infinity
                                self.distanceVector[vector_name] = -99

                                # regardless, send message if change occurs
                                hasChangeOccured = True

                            elif proposedCost < self.distanceVector[vector_name] and self.check_negative_cycle(vector_name, proposedCost):

                                # add the new vector at the proposed cost
                                self.distanceVector[vector_name] = proposedCost

                                # record change for future negative cycle detection
                                self.negativeCycleMonitor.append({
                                    "vector": vector_name,
                                    "cost": proposedCost
                                })

                                # regardless, send message if change occurs
                                hasChangeOccured = True
                                

        
        # Empty queue
        self.messages = []

        # TODO 2. Send neighbors updated distances  
        if hasChangeOccured:   
            for incoming_link in self.incoming_links:
                self.send_msg(
                    msg = {
                        "origin_node": self.name,
                        "origin_node_distance_vector": self.distanceVector
                    },
                    dest = incoming_link.name
                )

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:A0,B1,C2
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided.

        # Create String To Reflect Distance Vector Entry: will always start with them reaching themselves at cost 0
        # distanceVectorString = "{}0".format(self.name)
        distanceVectorString = ""

        # traverse through distance vector to build out distance vector string
        for name, weight in sorted(self.distanceVector.items()):

            # adjust weights to reflect infinity
            if weight <= -100:
                weight = -99

            # append current vector to distanceVectorString
            distanceVectorString += "{}{},".format(name, weight)

        # remove final comma from distance vector string
        distanceVectorString = distanceVectorString[:-1]
            
        # publish entry now that distanceVectorString is finalized
        add_entry(self.name, distanceVectorString)        
