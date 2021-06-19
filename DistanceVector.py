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

        # Create Placeholders to prevent against negative cycles
        self.negativeCycles = []

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
            for vector, cost in origin_node_distance_vector.items():

                # use distance vector to find cost for origin node
                # cost_to_origin = origin_node_distance_vector[origin_node]

                # use builtin function to get weight for origin node
                weight = self.get_outgoing_neighbor_weight(origin_node)

                # adding sum of distance vector 
                proposedCost = int(cost) + int(weight)

                # handle case where we need to add a new vector to our DV
                if vector not in self.distanceVector:

                    # add the new vector at the proposed cost
                    self.distanceVector[vector] = proposedCost

                    # note that a distance vector link was updated
                    hasChangeOccured = True

                elif self.name != vector and proposedCost < self.distanceVector[vector]:

                    # make sure to test against negative cycle
                    if vector in self.negativeCycles:
                        # add the new vector at the proposed cost
                        self.distanceVector[vector] = -99
                    else:

                        # record vector for possible loop
                        self.negativeCycles.append(vector)

                        # add the new vector at the proposed cost
                        self.distanceVector[vector] = proposedCost

                        # note that a distance vector link was updated
                        hasChangeOccured = True

                else:
                    # print("##### Doing Nothing #####")
                    pass

        
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
        for name, weight in self.distanceVector.items():
            
            # append current vector to distanceVectorString
            distanceVectorString += "{}{},".format(name, weight)

        # remove final comma from distance vector string
        distanceVectorString = distanceVectorString[:-1]
            
        # publish entry now that distanceVectorString is finalized
        add_entry(self.name, distanceVectorString)        
