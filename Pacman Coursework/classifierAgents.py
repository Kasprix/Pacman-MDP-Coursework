# classifierAgents.py
# parsons/07-oct-2017
#
# Version 1.0
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
import os
import csv
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

# class of a neural network
class NeuralNetwork:

    def __init__(self, data, target):
        # creates instances of the data and target into numpy arrays
        self.data = np.array(data)
        self.target = np.array(target)

    def train(self):
        # splits data into training and test data
        X_train, X_test, y_train, y_test = train_test_split(self.data, self.target, test_size=0.2)
        # creates classifier
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(10), random_state=1)
        # fits model to the data
        clf.fit(X_train, y_train)

        return clf

    # code to predict the move
    def predict(self, feature):
        guess = self.clf.predict(feature.reshape(1, -1))
        return guess


# ClassifierAgent
#
# An agent that runs a classifier to decide what to do.
class ClassifierAgent(Agent):

    # Constructor. This gets run when the agent starts up.
    def __init__(self):
        print "Initialising"


    # Take a string of digits and convert to an array of
    # numbers. Exploits the fact that we know the digits are in the
    # range 0-4.
    #
    # There are undoubtedly more elegant and general ways to do this,
    # exploiting ASCII codes.
    def convertToArray(self, numberString):
        numberArray = []
        for i in range(len(numberString) - 1):
            if numberString[i] == '0':
                numberArray.append(0)
            elif numberString[i] == '1':
                numberArray.append(1)
            elif numberString[i] == '2':
                numberArray.append(2)
            elif numberString[i] == '3':
                numberArray.append(3)
            elif numberString[i] == '4':
                numberArray.append(4)

        return numberArray

    # This gets run on startup. Has access to state information.
    #
    # Here we use it to load the training data.
    def registerInitialState(self, state):

        # open datafile, extract content into an array, and close.
        self.datafile = open('good-moves.txt', 'r')
        content = self.datafile.readlines()
        self.datafile.close()
        # if moves file exists then concatenate to good moves file
        if os.stat("moves.txt").st_size != 0:
            self.datafile = open('moves.txt', 'r')
            otherMoves = self.datafile.readlines()
            self.datafile.close()
            content = content + otherMoves

        # Now extract data, which is in the form of strings, into an
        # array of numbers, and separate into matched data and target
        # variables.
        self.data = []
        self.target = []
        # Turn content into nested lists
        for i in range(len(content)):
            lineAsArray = self.convertToArray(content[i])
            dataline = []
            for j in range(len(lineAsArray) - 1):
                dataline.append(lineAsArray[j])

            self.data.append(dataline)
            targetIndex = len(lineAsArray) - 1
            self.target.append(lineAsArray[targetIndex])

        # data and target are both arrays of arbitrary length.
        #
        # data is an array of arrays of integers (0 or 1) indicating state.
        #
        # target is an array of imtegers 0-3 indicating the action
        # taken in that state.

        # *********************************************
        #
        # Any other code you want to run on startup goes here.

        # creates instance of neural network with data from files
        classifier = NeuralNetwork(self.data, self.target)
        # utilises the train function on the data
        self.clf = classifier.train()

        #
        # You may wish to create your classifier here.
        #
        # *********************************************

    # Tidy up when Pacman dies
    def final(self, state):

        print "I'm done!"
        # *********************************************
        #
        # Any code you want to run at the end goes here.
        #
        # *********************************************

    # Turn the numbers from the feature set into actions:
    def convertNumberToMove(self, number):
        if number == 0:
            return Directions.NORTH
        elif number == 1:
            return Directions.EAST
        elif number == 2:
            return Directions.SOUTH
        elif number == 3:
            return Directions.WEST

    # Here we just run the classifier to decide what to do
    def getAction(self, state):

        # How we access the features.
        features = api.getFeatureVector(state)



        # *****************************************************
        #
        # Here you should insert code to call the classifier to
        # decide what to do based on features and use it to decide
        # what action to take.
        #
        # *******************************************************

        # Get the actions we can try.
        legal = api.legalActions(state)
        self.registerInitialState(state)
        # turns features into numpy array
        features = np.asarray(features)
        # guesses the move inferred from the network
        guess = (self.clf.predict(features.reshape(1, -1)))
        # converts prediction to number for move
        number = self.convertNumberToMove(guess)

        print
        print number
        print

        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are. We need to pass
        # the set of legal moves to teh API so it can do some safety
        # checking.
        # makes the move with the prediction
        return api.makeMove(number, legal)
