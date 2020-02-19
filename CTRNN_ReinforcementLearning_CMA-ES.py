import mujoco_py
import random
import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
import gym, pybullet_envs
import json
from datetime import datetime
import os

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import cma
from scoop import futures


def continuous_time_rnn(y, alpha, V, W, u):

    u2 = u[:, np.newaxis]

    # Differential equation
    dydt = np.dot(W, np.tanh(y)) + np.dot(V, u2)

    return dydt


def evalFitness(individual):

    V_size = input_size * number_neurons
    W_size = number_neurons * number_neurons

    # Get weight matrizes of current individual
    V = np.array([[element] for element in individual[0:V_size]])
    W = np.array([[element] for element in individual[V_size:V_size+W_size]])
    T = np.array([[element] for element in individual[V_size+W_size:]])

    V = V.reshape([number_neurons, input_size])
    W = W.reshape([number_neurons, number_neurons])
    T = T.reshape([number_neurons, output_size])

    # Set elements of main diagonal to less than 0
    for j in range(number_neurons):
        W[j][j] = -abs(W[j][j])

    fitness_current = 0

    for i in range(configuration_data["number_fitness_runs"]):

        # Anfangswerte
        y = np.zeros(number_neurons)
        y = y[:, np.newaxis]

        ob = env.reset()
        done = False

        # Test fitness through simulation
        while not done:
            dy = continuous_time_rnn(y, alpha, V, W, ob)
            y = y + delta_t * dy

            # Clip to state boundaries
            y = np.clip(y, configuration_data["clipping_range_min"], configuration_data["clipping_range_max"])

            o = np.tanh(np.dot(y.T, T))
            action = o[0]

            # Perform simulation step of the environment
            ob, rew, done, info = env.step(action)

            fitness_current += rew

    return fitness_current,


# Load configuration file
with open("Configuration.json", "r") as read_file:
    configuration_data = json.load(read_file)

env = gym.make(configuration_data["environment"])

# Number of neurons
number_neurons = configuration_data["number_neurons"]
input_size = env.observation_space.shape[0]
output_size = env.action_space.shape[0]

# Alpha
alpha = 0.01

delta_t = configuration_data["delta_t"]

# Size of Individual
IND_SIZE = input_size * number_neurons + number_neurons * number_neurons + number_neurons * output_size

print(IND_SIZE)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, typecode='b', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Multiprocessing
toolbox.register("map", futures.map)

toolbox.register("evaluate", evalFitness)

population_size = configuration_data["population_size"]

if population_size == 'default':
    strategy = cma.Strategy(centroid=[0.0] * IND_SIZE, sigma=configuration_data["sigma"])
else:
    strategy = cma.Strategy(centroid=[0.0] * IND_SIZE, sigma=configuration_data["sigma"], lambda_=population_size)

toolbox.register("generate", strategy.generate, creator.Individual)
toolbox.register("update", strategy.update)

if __name__ == "__main__":

    startTime = time.time()

    hof = tools.HallOfFame(5)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaGenerateUpdate(toolbox, ngen=configuration_data["number_generations"], stats=stats, halloffame=hof)

    # print elapsed time
    print("Time elapsed: %s" % (time.time() - startTime))

    # Create new directory to store data of current simulation run
    directory = os.path.join('Simulation_Results','CTRNN', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(directory)

    # Save Configuration file as json
    with open(os.path.join(directory, 'Configuration.json'), 'w') as outfile:
        json.dump(configuration_data, outfile)

    # Save Weights of hall of fame individuals
    with open(os.path.join(directory, 'HallOfFame.pickle'), "wb") as fp:
        pickle.dump(hof, fp)

    # Save Log
    with open(os.path.join(directory, 'Log.json'), 'w') as outfile:
        json.dump(log, outfile)

    # Get statistics from log
    generations = [i for i in range(len(log))]
    avg = [generation["avg"] for generation in log]
    high = [generation["avg"] + generation["std"] for generation in log]
    low = [generation["avg"] - generation["std"] for generation in log]

    # Plot results
    plt.plot(generations, avg, 'r-')
    plt.plot(generations, high, 'y--')
    plt.plot(generations, low, 'b--')
    plt.xlabel('Generations')
    plt.legend(['avg', 'std high', 'std low'])
    plt.grid()
    plt.show()
