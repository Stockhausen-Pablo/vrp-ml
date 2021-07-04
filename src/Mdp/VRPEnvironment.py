class VRPEnvironment:
    """
    MDP-Model" is provided inside code for the environment
        a predictive model of the env that resolves probabilities of next reward and next state following an action from a state
    """

    def __init__(self, states, actions, distanceMatrix, microHub, capacityDemands,
                 vehicles, vehicleWeight, vehicleVolume):
        self.states = states
        self.actions = actions
        self.distanceMatrix = distanceMatrix
        self.microHub = microHub
        self.microhub_counter = 0

        # demands
        self.vehicles = vehicles
        self.capacityDemands = capacityDemands
        self.vehicleWeight = vehicleWeight
        self.vehicleVolume = vehicleVolume

        # current
        self.current_state = None
        self.current_state = [self.microHub if self.current_state is None else self.current_state]
        self.possibleStops = []
        self.done = False

        # current Tours
        self.allTours = []
        self.current_tour = []
        self.current_tour.append(self.current_state)
        self.current_tour_weight = 0.0
        self.current_tour_volume = 0.0

        # init
        self.resetPossibleStops()

    def reset(self):
        self.done = False
        self.resetPossibleStops()
        self.resetTours()
        self.microhub_counter = 0
        return self.current_state

    def step(self, action, suggested_next_state):
        if action == 0:
            return self.evaluate_action_0()

        if action == 1:
            return self.evaluate_action_1(suggested_next_state)

        if action == 2:
            return self.evaluate_action_2()

    def evaluate_action_0(self):
        next_state = self.getMicrohub()
        reward = self.reward_func(self.current_state, next_state)
        self.current_tour.append(next_state)
        self.current_state = next_state
        self.resetTour()
        return next_state, reward, self.done, self.current_tour, self.allTours

    def evaluate_action_1(self, suggested_next_state):
        next_state = self.getStateByHash(suggested_next_state)
        reward = self.reward_func(self.current_state, next_state)
        self.current_state = next_state
        self.updateTourMeta(next_state)
        return next_state, reward, self.done, self.current_tour, self.allTours

    def evaluate_action_2(self):
        next_state = self.getMicrohub()
        reward = self.reward_func(self.current_state, next_state)
        self.current_tour.append(next_state)
        self.current_state = next_state
        self.done = True
        self.resetTour()
        return next_state, reward, self.done, self.current_tour, self.allTours

    def resetPossibleStops(self):
        copyStates = self.states.copy()
        copyStates.remove(self.microHub)
        self.current_state = self.microHub
        self.possibleStops = copyStates

    def resetTours(self):
        self.allTours = []
        self.current_tour = []
        self.current_tour.append(self.current_state)
        self.current_tour_weight = 0.0
        self.current_tour_volume = 0.0

    def resetTour(self):
        self.allTours.append(self.current_tour)
        self.current_tour = []
        self.current_tour.append(self.current_state)
        self.current_tour_weight = 0.0
        self.current_tour_volume = 0.0

    def updateTourMeta(self, next_state):
        self.possibleStops.remove(next_state)
        self.current_tour.append(next_state)
        self.current_tour_weight += next_state.demandWeight
        self.current_tour_volume += next_state.demandVolume

    def reward_func(self, current_stop, next_stop):
        reward = self.distanceMatrix.at[current_stop.hashIdentifier, next_stop.hashIdentifier]
        return reward

    def reward_func_hash(self, current_stop, next_stop):
        return self.distanceMatrix.at[current_stop, next_stop]

    def getCapacityDemandOfStop(self, stop_hash):
        return list(self.capacityDemands[stop_hash].values())

    def getMicrohub(self):
        return self.microHub

    def get_microhub_hash(self):
        return self.microHub.hashIdentifier

    def getStateByHash(self, hashIdentifier):
        return next((state for state in self.states if state.hashIdentifier == hashIdentifier), None)

    def getStateHashes(self):
        return [state.hashIdentifier for state in self.states]

    def possible_rewards(self, state, action_space_list):
        possible_rewards = self.distanceMatrix.loc[state, action_space_list]
        return possible_rewards

    def getLegalAction(self):
        legal_next_states = []
        legal_next_states_hubs_ignored = []
        legal_next_states_local_search_distance = dict()
        legal_next_states_bin_packing_capacities = dict()
        for stop in self.possibleStops:
            possible_tour_weight = float(stop.demandWeight) + self.current_tour_weight
            possible_tour_volume = float(stop.demandVolume) + self.current_tour_volume
            if possible_tour_weight <= self.vehicleWeight and possible_tour_volume <= self.vehicleVolume:
                if stop.hashIdentifier == self.microHub.hashIdentifier:
                    continue
                else:
                    legal_next_states.append(stop.hashIdentifier)
                    legal_next_states_hubs_ignored.append(stop.hashIdentifier)
                    legal_next_states_local_search_distance[stop.hashIdentifier] = self.reward_func(
                        self.current_state, stop)
                    legal_next_states_bin_packing_capacities[stop.hashIdentifier] = [
                        possible_tour_weight / self.vehicleWeight, possible_tour_volume / self.vehicleVolume]

        legal_next_states_local_search_distance = {k: v for k, v in
                                                   sorted(legal_next_states_local_search_distance.items(),
                                                          key=lambda x: x[1])}
        legal_next_states_bin_packing_capacities = {k: v for k, v in
                                                     sorted(legal_next_states_bin_packing_capacities.items(),
                                                            key=lambda x: x[1], reverse=True)}

        if legal_next_states:
            action = 1
            return action, legal_next_states, legal_next_states_hubs_ignored, legal_next_states_local_search_distance, legal_next_states_bin_packing_capacities, self.microhub_counter

        if not legal_next_states and not self.possibleStops:
            microhub_counter = self.microhub_counter + 1
            legal_next_states.append('{}/{}'.format(self.microHub.hashIdentifier, microhub_counter))
            legal_next_states_hubs_ignored.append(self.microHub.hashIdentifier)
            action = 2
            self.microhub_counter += 1
            # shuffle(legal_next_states)
            return action, legal_next_states, legal_next_states_hubs_ignored, legal_next_states_local_search_distance, legal_next_states_bin_packing_capacities, self.microhub_counter

        if not legal_next_states and self.possibleStops:
            microhub_counter = self.microhub_counter + 1
            legal_next_states.append('{}/{}'.format(self.microHub.hashIdentifier, microhub_counter))
            legal_next_states_hubs_ignored.append(self.microHub.hashIdentifier)
            action = 0
            self.microhub_counter += 1
            return action, legal_next_states, legal_next_states_hubs_ignored, legal_next_states_local_search_distance, legal_next_states_bin_packing_capacities, self.microhub_counter
