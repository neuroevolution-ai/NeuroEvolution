from deap import base
from deap import creator
from deap import tools
from deap import cma
# from deap import algorithms
from Others import algorithms
import pickle
import random


class TrainerCmaEs(object):
    def __init__(self, evalFitness, individual_size, conf, map_func=map, hof=tools.HallOfFame(5),
                 trainer_parameters=None, checkpoint=None):

        self.toolbox = toolbox = base.Toolbox()
        self.conf = conf
        self.hof = hof
        if checkpoint:
            with open(checkpoint, "rb") as cp_file:
                cp = pickle.load(cp_file)
            toolbox.strategy = strategy = cp["strategy"]
        else:
            toolbox.strategy = strategy = cma.Strategy(centroid=[0.0] * individual_size, sigma=conf["sigma"],
                                    lambda_=conf["population_size"])
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, typecode='b', fitness=creator.FitnessMax)
        toolbox.register("map", map_func)
        toolbox.register("evaluate", evalFitness)
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

    def train(self, stats, number_generations, checkpoint):
        return algorithms.eaGenerateUpdate(self.toolbox, ngen=number_generations,
                                           stats=stats, halloffame=self.hof, checkpoint=checkpoint)
