import csv

import src.Tour.TourManager as tManager
from argsConfig import getParams
from src.Aco.AntManager import AntManager
from src.Mdp.VRPEnvironment import VRPEnvironment
from src.RL.Policy.PolicyManager import PolicyManager
from src.RL.VRPAgent import VRPAgent
from src.Tour.Stop import Stop
from src.Utils import plotting
from src.Utils.helper import normalize_df
from src.Utils.plotter import plotCoordinatesWithCoordinatesLabel, plotCoordinatesWithStopNrLabel, plotTourWithStopNrLabel


def loadStopData(dataSet):
    with open('data/stops/' + dataSet + '.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            tManager.addStop(
                Stop(float(row[0]), int(row[1]), float(row[2]), float(row[3]), int(row[4]), int(row[5])))
    tManager.calculateDistanceMatrix()
    tManager.initCapacityDemands()


def main(args):
    # --------------------
    # ARGSPARSE
    # define parameters
    learning_rate = args['learning_rate']
    discount_factor = args['discount_factor']
    exploration_factor = args['exploration_factor']
    num_episodes = args['num_episodes']
    max_steps = args['max_steps']
    # aco settings
    aco_alpha_factor = args['aco_alpha_factor']
    aco_beta_factor = args['aco_beta_factor']
    pheromone_evaporation_coefficient = args['pheromone_evaporation_coefficient']
    pheromone_constant = args['pheromone_constant']
    aco_iterations = args['aco_iterations']

    # --------------------
    # INPUT
    # define meta data
    print("---------System menu---------")
    print("Below please specify the configuration options of the program")
    dataSet = input("Please specify the data source of the stops to be processed:")
    amountVehicles = int(input("How many vehicles will be used:"))
    capacityWeight = float(input("What is the maximum weight that the vehicle can carry:"))
    capacityVolume = float(input("What is the maximum volume that the vehicle can hold:"))

    # --------------------
    # SETTING UP TOUR MANAGER
    # Load Stop Data
    tManager.clear()
    loadStopData(dataSet)

    # Setup Distance Matrix for later use
    distanceMatrix = tManager.getDistances()

    # --------------------
    # PLOT COORDINATES
    # overview of problem space (input)
    plotCoordinatesWithCoordinatesLabel()
    plotCoordinatesWithStopNrLabel()

    if args['train']:
        # --------------------TRAINING MODE--------------------
        print("-Entered Training Mode-")

        # --------------------
        # ANT COLONY OPTIMIZATION
        # setting up and running ACO
        print("-Starting up Ant Colony Optimization to get Probability Matrix-")
        antManager = AntManager(
            stops=tManager.getListOfStops(),
            start_stop=tManager.getStop(0),
            vehicleWeight=capacityWeight,
            vehicleVolume=capacityVolume,
            vehicleCount=amountVehicles,
            discountAlpha=aco_alpha_factor,
            discountBeta=aco_beta_factor,
            pheromone_evaporation_coefficient=pheromone_evaporation_coefficient,
            pheromone_constant=pheromone_constant,
            iterations=aco_iterations
        )

        # --------------------
        # ACO RESULTS
        # retrieving solution from ACO and preparing further transformation
        resultACO = antManager.runACO()
        ant_shortest_distance = resultACO[0]
        ant_shortest_path = resultACO[1]
        aco_probability_Matrix = resultACO[2]

        # --------------------
        # NORMALIZING PROBABILITIES
        # normalize the ant probability Matrix
        normalized_probability_Matrix = normalize_df(aco_probability_Matrix)

        # --------------------
        # ENVIRONMENT
        # setting up MDP-Environment
        environment = VRPEnvironment(
            states=tManager.getListOfStops(),
            # actions:
            # 0 = select microhub if tour full and possible Stops != null
            # 1 = select unvisited Node from possible Stops
            # 2 = select microhub if tour full and possible Stops = null
            actions=[0, 1, 2],
            probabilityMatrix=normalized_probability_Matrix,
            distanceMatrix=distanceMatrix,
            microHub=tManager.getMicrohub(),
            capacityDemands=tManager.getCapacityDemands(),
            vehicles=amountVehicles,
            vehicleWeight=capacityWeight,
            vehicleVolume=capacityVolume
        )

        # --------------------
        # POLICY NETWORK
        policyManager = PolicyManager(environment.getStateHashes(),
                                      normalized_probability_Matrix,
                                      learning_rate,
                                      discount_factor,
                                      exploration_factor
                                      )

        # --------------------
        # AGENT
        agent = VRPAgent(env=environment,
                         policyManager=policyManager,
                         num_episodes=num_episodes,
                         max_steps=max_steps,
                         discount_factor=discount_factor
                         )

        # --------------------
        # TRAINING RESULTS
        episodeStatistics, policy_action_space, best_policy_reward, last_policy_reward = agent.train_model()
        current_policy_reward, final_tours = policyManager.construct_policy(policyManager.get_current_policy(), environment, max_steps)

        print("----------------------------------------")
        print("Best_policy_reward: ", best_policy_reward)
        print("Final_policy_reward: ", last_policy_reward)

        # --------------------
        # PLOTTING TRAINING RESULTS
        plotting.plot_episode_stats(episodeStatistics, smoothing_window=25)
        plotTourWithStopNrLabel(final_tours)


        if args['test']:
            # --------------------TESTING MODE--------------------
            print("Testig")


if __name__ == "__main__":
    args = getParams()
    main(args)
