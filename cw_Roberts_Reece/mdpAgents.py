# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state): 
        # Returns all legal states available to Pacman
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Current x, y location of Pacman
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman
        
        # Initialises list to store ghosts that are not in a scared state
        ghostie = []

        # Get extreme x and y values for the grid to create the mapping
        corners = api.corners(state)

        # Setup variable to hold the values
        minX = 100
        minY = 100
        maxX = 0
        maxY = 0
        
        # Goes through corner values to determine the max & min coordinates
        for i in range(len(corners)):
            cornerX = corners[i][0]
            cornerY = corners[i][1]
            
            if cornerX < minX:
                minX = cornerX
            if cornerY < minY:
                minY = cornerY
            if cornerX > maxX:
                maxX = cornerX
            if cornerY > maxY:
                maxY = cornerY
           
        # Initialises list to store all coordinates in between min and max values
        mapping = []  
        
        # Counter to populate mapping list with all coordinates within the map
        count = 0
        for i in range((minX+1),(maxX)):
            for j in range((minY+1),(maxY)):
                mapping.append((i, j))
                count = count+1
                
        
        # Where is the food?
        hungry = api.food(state)
        

        # Where are the walls?
        walls = api.walls(state)
        
        # Only stores coordinates that are not the walls on the map
        freespaces = [x for x in mapping if x not in walls]
        
        # Stores all coordinates that are not food on the map
        nofood = [x for x in freespaces if x not in hungry]
        
        # Stores all coordinates that are food on the map
        food = [x for x in freespaces if x in hungry]
        
        # Returns the coordinates of the ghosts and whether they're scared or not
        ghostState = api.ghostStates(state)
        
        # loop that seperates scared and not scared ghosts, scared ghosts are added to food list, deadly ghosts are stored in ghost list
        count = 0
        for g in ghostState:
            # for ghosts that are aggresive
            if g[1] == 0:
                cords = ghostState[count][0]
                x = int(cords[0])
                y = int(cords[1])
                ghostie.append((x, y))
                count += 1
            elif g[1] == 1:
            # for ghosts that are hungry
                cords = ghostState[count][0]
                x = int(cords[0])
                y = int(cords[1])
                food.append((x, y))
                count += 1
                

        # Updates no food and food to remove any values that might be in ghost list   
        nofood = [x for x in nofood if x not in ghostie]
        food = [x for x in food if x not in ghostie]
    
        # Initialises dictionary to store values for coordinates
        mapDic = {}
        
        # Initialises list to store coordinates of areas 1 value away from the aggressive ghosts
        perimeterCords = []
        
        # Loops to apply initial values to dictionary
        for f in food:
            mapDic[str(f)] = 0  
        for n in nofood:
            mapDic[str(n)] = 0
        
        # Loops to find coordinates that are not walls and are 1 x or y coordinate away from the aggressive ghost
        for m in ghostie:
            # Finds values left, right, up and down from ghost
            leftCoValue = ((m[0]-1), m[1])
            if str(leftCoValue) in food or nofood:
                perimeterCords.append(leftCoValue)
            rightCoValue = ((m[0]+1), m[1])
            if str(rightCoValue) in food or nofood:
                perimeterCords.append(rightCoValue)
            downCoValue = ((m[0]), m[1]-1)
            if str(downCoValue) in food or nofood:
                perimeterCords.append(downCoValue)
            upCoValue = ((m[0]), m[1]+1)
            if str(upCoValue) in food or nofood:
                perimeterCords.append(upCoValue)
                
        # Updates values for food and no food list to ommit perimiter values from their lists
        nofood = [x for x in nofood if x not in perimeterCords]
        food = [x for x in food if x not in perimeterCords]
          
        # Loops to assign initial values to dictionary
        for g in ghostie:
            mapDic[str(g)] = 0
            
        for p in perimeterCords:
            mapDic[str(p)] = 0
            
        # Initialise list to store all coordinates, stores all key values from dictionary
        mapList = []
        
        # Update map list
        for f in food:
            mapList.append(f)    
        for n in nofood:
            mapList.append(n)   
        for g in ghostie:
            mapList.append(g) 
        for p in perimeterCords:
            mapList.append(p)
        
        # Variables and different reward values for different parts of the map, negative values for ghost and perimeter
        # Positive values for the food values
        gamma = 0.8
        reward = -0.04
        foodReward = 2
        ghostReward = -2
        perimeterReward = -1.5
        
        #Value Iteration loop
        for i in range(100):
            # Copy current state of map dictionary to mimic coordinates solving the equations simultaneously 
            valueCopy = mapDic
            for m in mapList:
                # If direction isn't a legal move for the coordinate then that value is assigned to the current coordinate
                leftCoValue = ((m[0]-1), m[1])
                if str(leftCoValue) not in mapDic:
                    leftCoValue = m
                rightCoValue = ((m[0]+1), m[1])
                if str(rightCoValue) not in mapDic:
                    rightCoValue = m
                downCoValue = ((m[0]), m[1]-1)
                if str(downCoValue) not in mapDic:
                    downCoValue = m
                upCoValue = ((m[0]), m[1]+1)
                if str(upCoValue) not in mapDic:
                    upCoValue = m
            
                # Calculate the values for moves in all directions
                upcalc = ((0.8*valueCopy[str(upCoValue)])+(0.1*valueCopy[str(leftCoValue)])+(0.1*valueCopy[str(rightCoValue)]))
                downcalc = ((0.8*valueCopy[str(downCoValue)])+(0.1*valueCopy[str(leftCoValue)])+(0.1*valueCopy[str(rightCoValue)]))
                rightcalc = ((0.8*valueCopy[str(rightCoValue)])+(0.1*valueCopy[str(upCoValue)])+(0.1*valueCopy[str(downCoValue)]))
                leftcalc = ((0.8*valueCopy[str(leftCoValue)])+(0.1*valueCopy[str(upCoValue)])+(0.1*valueCopy[str(downCoValue)]))
                
                # Storing the sums into a dictionary
                var = {'upcalc':upcalc,'downcalc':downcalc,'rightcalc':rightcalc,'leftcalc':leftcalc}
                # Assign max value to the winner variable and the name to the winnerName Variable
                winner = max(var, key=var.get)
                winnerName = var.get(max(var))
                
                # For whatever move was most successful the value iteration formula is then applied to the current state and updates its value
                count = 0
                
                if winner == 'upcalc':
                    if m in ghostie:
                        mapDic[str(m)] = ghostReward + (gamma * upcalc)
                    elif m in food:
                        mapDic[str(m)] = foodReward + (gamma * upcalc)
                    elif m in nofood:
                        mapDic[str(m)] = reward + (gamma * upcalc) 
                    elif m in perimeterCords:
                        mapDic[str(m)] = perimeterReward + (gamma * upcalc) 

                        
                elif winner == 'downcalc':
                    if m in ghostie:
                        mapDic[str(m)] = ghostReward + (gamma * downcalc)
                    elif m in food:
                        mapDic[str(m)] = foodReward + (gamma * downcalc)
                    elif m in nofood:
                        mapDic[str(m)] = reward + (gamma * downcalc) 
                    elif m in perimeterCords:
                        mapDic[str(m)] = perimeterReward + (gamma * downcalc) 
                        
                elif winner == 'leftcalc':
                    if m in ghostie:
                        mapDic[str(m)] = ghostReward + (gamma * leftcalc)
                    elif m in food:
                        mapDic[str(m)] = foodReward + (gamma * leftcalc)
                    elif m in nofood:
                        mapDic[str(m)] = reward + (gamma * leftcalc)  
                    elif m in perimeterCords:
                        mapDic[str(m)] = perimeterReward + (gamma * leftcalc)
                        
                elif winner == 'rightcalc':
                    if m in ghostie:
                        mapDic[str(m)] = ghostReward + (gamma * rightcalc)
                    elif m in food:
                        mapDic[str(m)] = foodReward + (gamma * rightcalc)
                    elif m in nofood:
                        mapDic[str(m)] = reward + (gamma * rightcalc)
                    elif m in perimeterCords:
                        mapDic[str(m)] = perimeterReward + (gamma * rightcalc) 
                        
        
        # Assign variables that are the coordinate values for choices pacman can make
        leftVal = '('+str(int(pacman[0])-1) + ', ' + str(int(pacman[1])) + ')'
        rightVal = '('+str(int(pacman[0])+1) + ', ' + str(int(pacman[1])) + ')'
        downVal = '('+str(int(pacman[0])) + ', ' + str(int(pacman[1]-1)) + ')'
        upVal = '('+str(int(pacman[0])) + ', ' + str(int(pacman[1]+1)) + ')'
        
        
        # loop to add utility to all available moves that have already been through value iteration
        utilityDic = {}
        for l in legal:
            # finding the utility values for each move with respect to the probability of executing that move
            if l == 'West':
                utility = 0
                utility = mapDic[leftVal]*0.8
                if 'North' in legal:
                    utility = utility + (mapDic[upVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                if 'South' in legal:
                    utility = utility + (mapDic[downVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                # Value is then stored in utility Dictionary 
                utilityDic["West"] = utility    
                
            if l == 'East':
                utility = 0
                utility = mapDic[rightVal]*0.8
                if 'North' in legal:
                    utility = utility + (mapDic[upVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                if 'South' in legal:
                    utility = utility + (mapDic[downVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                    
                utilityDic["East"] = utility 
                
            if l == 'South':
                utility = 0
                utility = mapDic[downVal]*0.8
                if 'East' in legal:
                    utility = utility + (mapDic[rightVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                if 'West' in legal:
                    utility = utility + (mapDic[leftVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                    
                utilityDic["South"] = utility 
                
            if l == 'North':
                utility = 0
                utility = mapDic[upVal]*0.8
                if 'East' in legal:
                    utility = utility + (mapDic[rightVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                if 'West' in legal:
                    utility = utility + (mapDic[leftVal]*0.1)
                else:
                    utility = utility + (mapDic[str(pacman)]*0.1)
                    
                utilityDic["North"] = utility 
                
        # Storing the value with the higheest utility as the move to be made     
        maxone = max(utilityDic, key=utilityDic.get)    
        print utilityDic
        
        # Making the movement for the Pacman
        pick = maxone
        print maxone
        return api.makeMove(pick, legal)
        
        
                
                
        #for l in legal:
        #    if 
        
        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.