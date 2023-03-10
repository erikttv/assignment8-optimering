from math import floor
from random import randrange
from Container import Container


class Solution:

	def __init__(self, n_bays, n_stacks, n_tiers):
		self.n_bays = n_bays
		self.n_stacks = n_stacks
		self.n_tiers = n_tiers

		self.flow_x = [[[0 for _ in range(n_tiers)] for _ in range(n_stacks)] for _ in range(n_bays)]
		self.objective = float("inf")
		self.cog = [0, 0]
		self.total_weight_containers = 0

	def copy(self):
		"""
		Make a copy of the Solution object
		:return: Copy of the object
		"""
		new_solution = Solution(self.n_bays, self.n_stacks, self.n_tiers)

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					new_solution.flow_x[bay][stack][tier] = self.flow_x[bay][stack][tier]

		new_solution.objective = self.objective
		new_solution.cog = self.cog
		new_solution.total_weight_containers = self.total_weight_containers

		return new_solution

	def construct(self):
		"""
		Simple construction heuristic.
		Takes the first container in the list, and places it in the
		first location. The next is placed in the second location and
		so on.
		"""

		i = 0

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					self.flow_x[bay][stack][tier] = i
					i += 1

	def calculate_objective(self, containers):
		"""
		Denne metoden regner ut og oppdaterer målfunksjonsverdien til Solution-objektet.
		:param containers: list of Container objects
		"""

		# Her vil vi at cog (centre of gravity) skal ligge
		gravity_goal = [self.n_bays/2.0, self.n_stacks/2.0]

		# Lager en liste som brukes til å regne ut den aktuelle cog-en
		gravity_this = [0.0, 0.0]

		sum_container_weight = 0

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):

				sum_tier = 0

				for tier in range(self.n_tiers):
					container_weight = containers[self.flow_x[bay][stack][tier]].weight
					sum_tier += container_weight
					sum_container_weight += container_weight

				gravity_this[0] += (bay - 0.5) * sum_tier
				gravity_this[1] += (stack - 0.5) * sum_tier

		gravity_this[0] /= sum_container_weight
		gravity_this[1] /= sum_container_weight

		evaluation = (gravity_goal[0] - gravity_this[0])**2 + (gravity_goal[1] - gravity_this[1])**2

		self.objective = evaluation
		self.cog = gravity_this
		self.total_weight_containers = sum_container_weight

	def print_solution(self):
		print("Current solution:")

		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					print(f"Bay: {bay}, stack: {stack}, tier: {tier}, container: {self.flow_x[bay][stack][tier]}")

	def swap_two_random_containers(self):
		bay1 = randrange(self.n_bays)
		stack1 = randrange(self.n_stacks)
		tier1 = randrange(self.n_tiers)

		bay2 = randrange(self.n_bays)
		stack2 = randrange(self.n_stacks)
		tier2 = randrange(self.n_tiers)

		while bay1 == bay2 and stack1 == stack2 and tier1 == tier2:
			bay2 = randrange(self.n_bays)
			stack2 = randrange(self.n_stacks)
			tier2 = randrange(self.n_tiers)

		self.flow_x[bay1][stack1][tier1], self.flow_x[bay2][stack2][tier2] = self.flow_x[bay2][stack2][tier2], self.flow_x[bay1][stack1][tier1]

	def construction_improved(self, containers):
		"""
		This construction heuristic is coded explicitly for instance1.txt.
		containers have to be sorted descending in terms of weight
		"""
		sorted_containers = Container.sort_array_weight_descending(containers)

		counter = 0

		centre_bay = self.n_bays // 2
		centre_stack = self.n_stacks // 2 + 1

		for tier in range(self.n_tiers):

			oscillator = 1
			iterator = 0

			for bay in range(self.n_bays):
				self.flow_x[centre_bay + floor(iterator)*oscillator][centre_stack][tier] = sorted_containers[counter].container_id
				iterator += 0.5
				counter += 1
				oscillator *= -1

		counter += 1

		for tier in range(self.n_tiers):

			iterator = 0
			bin = 1
			o_b = 1
			for o_s in range(self.n_stacks // 2):
				for bay in range(self.n_bays):
					self.flow_x[centre_bay + floor(iterator) * o_b][centre_stack + o_s][tier] = sorted_containers[counter - 3*bin].container_id
					self.flow_x[centre_bay + floor(iterator) * o_b][centre_stack - o_s][tier] = sorted_containers[counter + bin].container_id
					counter += 2

					o_b *= -1
					bin += o_b
					iterator += 0.5

				iterator = 0

	def local_search_two_swap(self, containers):

		# Lagrer verdien på max(self.n_bays, self.n_stacks, self.n_tiers). Brukes til å
		# redusere antall evalueringer i nabolaget
		max_index = max(self.n_bays, self.n_stacks, self.n_tiers)

		# Lagrer centre of gravity som cog_current, og multipliserer med vekten av alle containere
		# for å forenkle evalueringen.
		cog_current = [self.cog[0] * self.total_weight_containers, self.cog[1] * self.total_weight_containers]

		#Brukes til å lagre ny verdi av cog etter bytte
		cog_temp = [0, 0]

		# Målet er å få cog så nær midten av skipet som mulig, derav:
		cog_goal = [self.n_bays/2, self.n_stacks/2]

		# Lagrer beste funne målfunksjonsverdi
		best_objective = self.objective

		# Lager en liste for å lagre indeksene til containeren vi vil swappe
		location_of_container1 = [0, 0, 0]
		location_of_container2 = [0, 0, 0]

		# Stopper while-løkken hvis målfunksjonsverdien ikke forbedres
		is_improving = True

		while is_improving:
			is_improving = False

			cog_best = [0, 0]

			for bay1 in range(self.n_bays):
				for stack1 in range(self.n_stacks):
					for tier1 in range(self.n_tiers):
						for bay2 in range(self.n_bays):
							for stack2 in range(self.n_stacks):
								for tier2 in range(self.n_tiers):
									if bay1 * max_index**2 + stack1 * max_index + tier1 < bay2 * max_index**2 + stack2 * max_index + tier2:
										# If-setningen sørger for at vi kun evaluerer hvert kontainerpar én gang

										# Subtract the old contribution to the objective
										cog_temp[0] = cog_current[0] - (bay1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (bay2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight
										cog_temp[1] = cog_current[1] - (stack1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (stack2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight

										# Add the new contribution to the objective after the swap
										cog_temp[0] = cog_temp[0] + (bay2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (bay1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight
										cog_temp[1] = cog_temp[1] + (stack2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (stack1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight

										# Divide on the total weight of the containers to get the cog
										cog_temp[0] /= self.total_weight_containers
										cog_temp[1] /= self.total_weight_containers

										# Calculate the objective

										evaluation = (cog_goal[0] - cog_temp[1])**2 + (cog_goal[1] - cog_temp[1])**2

										if evaluation < best_objective:
											best_objective = evaluation
											location_of_container1 = [bay1, stack1, tier1]
											location_of_container2 = [bay2, stack2, tier2]

											cog_best = cog_temp

											is_improving = True

			if is_improving:
				# Do the swap
				temp_cont = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
				self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]] = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]
				self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]] = temp_cont

				# Update objective and cog
				self.objective = best_objective
				self.cog = cog_best

				cog_current[0] = self.cog[0] * self.total_weight_containers
				cog_current[1] = self.cog[1] * self.total_weight_containers

	def local_search_three_swap(self, containers):
		# Lagrer verdiem på max(self.n_bays, self.n_stacks, self.n_tiers). Brukes til å
		# redusere antall evalueringer i nabolaget
		max_index = max(self.n_bays, self.n_stacks, self.n_tiers)

		# Lagrer centre of gravity som cog_current, og multipliserer med vekten av alle
		# containere for å forenkle evalueringen
		cog_current = [self.cog[0] * self.total_weight_containers, self.cog[1] * self.total_weight_containers]

		# Brukes til å lagre ny verdi av cog etter bytte
		cog_temp = [0, 0]

		# Målet er å få cog så nær midten av skipet som mulig, derav:
		cog_goal = [self.n_bays/2, self.n_stacks/2]

		# Lagrer beste funne målfunksjonsverdi
		best_objective = self.objective

		# Lager en liste for å lagre indeksene til containeren vi vil swappe
		location_of_container1 = [0, 0, 0]
		location_of_container2 = [0, 0, 0]
		location_of_container3 = [0, 0, 0]

		# Stopper while-løkken hvis målfunksjonsverdien ikke forbedres
		is_improving = True

		while is_improving:
			is_improving = False

			cog_best = [0, 0]

			swap_possibility = -1

			for bay1 in range(self.n_bays):
				for stack1 in range(self.n_stacks):
					for tier1 in range(self.n_tiers):
						for bay2 in range(self.n_bays):
							for stack2 in range(self.n_stacks):
								for tier2 in range(self.n_tiers):
									for bay3 in range(self.n_bays):
										for stack3 in range(self.n_stacks):
											for tier3 in range(self.n_tiers):
												if bay1*max_index**2 + stack1*max_index + tier1 < bay2*max_index**2 + stack2*max_index + tier2 and bay2*max_index**2 + stack2*max_index + tier2 < bay3*max_index**2 + stack3*max_index + tier3:
													# Vi har 2 mulige swaps som er rene 3-swaps, dvs. alle containere
													# får en ny plassering. Sjekker disse

													# First possible (c1, c2, c3) -> (c3, c1, c2):
													# Subtract the old contribution to the objective
													cog_temp[0] = cog_current[0] - (bay1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (bay2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight - (bay3 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight
													cog_temp[1] = cog_current[1] - (stack1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (stack2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight - (stack3 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight

													# Add new contribution to the objective after the swap
													cog_temp[0] = cog_temp[0] + (bay2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (bay3 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight + (bay1 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight
													cog_temp[1] = cog_temp[1] + (stack2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (stack3 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight + (stack1 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight

													# Divide on the total weight of the containers to get the cog
													cog_temp[0] /= self.total_weight_containers
													cog_temp[1] /= self.total_weight_containers

													# Calculate the objective
													evaluation = (cog_goal[0] - cog_temp[0])**2 + (cog_goal[1] - cog_temp[1])**2

													if evaluation < best_objective:
														best_objective = evaluation
														location_of_container1 = [bay1, stack1, tier1]
														location_of_container2 = [bay2, stack2, tier2]
														location_of_container3 = [bay3, stack3, tier3]

														swap_possibility = 1
														cog_best = cog_temp
														is_improving = True

													# Second possible (c1, c2, c3) -> (c2, c3, c1)
													# Subtract the old contribution to the objective
													cog_temp[0] = cog_current[0] - (bay1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (bay2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight - (bay3 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight
													cog_temp[1] = cog_current[1] - (stack1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (stack2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight - (stack3 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight

													# Add the new contribution to the objective after the swap
													cog_temp[0] = cog_temp[0] + (bay3 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (bay1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight + (bay2 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight
													cog_temp[1] = cog_temp[1] + (stack3 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (stack1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight + (stack2 - 0.5)*containers[self.flow_x[bay3][stack3][tier3]].weight

													# Divide on the total weight of the containers to get the cog
													cog_temp[0] /= self.total_weight_containers
													cog_temp[1] /= self.total_weight_containers

													# Calculate the objective
													evaluation = (cog_goal[0] - cog_temp[0])**2 + (cog_goal[1] - cog_temp[1])**2

													if evaluation < best_objective:
														best_objective = evaluation
														location_of_container1 = [bay1, stack1, tier1]
														location_of_container2 = [bay2, stack2, tier2]
														location_of_container3 = [bay3, stack3, tier3]

														swap_possibility = 2
														cog_best = cog_temp
														is_improving = True
			if is_improving:
				# Do the swap
				temp_cont1 = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
				temp_cont2 = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]
				temp_cont3 = self.flow_x[location_of_container3[0]][location_of_container3[1]][location_of_container3[2]]

				if swap_possibility == 1:
					# First possible (c1, c2, c3) -> (c3, c1, c2)
					self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]] = temp_cont3
					self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]] = temp_cont1
					self.flow_x[location_of_container3[0]][location_of_container3[1]][location_of_container3[2]] = temp_cont2

				elif swap_possibility == 2:
					# Second possible (c1, c2, c3) -> (c2, c3, c1)
					self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]] = temp_cont2
					self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]] = temp_cont3
					self.flow_x[location_of_container3[0]][location_of_container3[1]][location_of_container3[2]] = temp_cont1

				# Update objective and cog
				self.objective = best_objective
				self.cog = cog_best
				cog_current[0] = self.cog[0] * self.total_weight_containers
				cog_current[1] = self.cog[1] * self.total_weight_containers

	def tabu_search_heuristic(self, containers, n_iterations):
		# Vi lagrer en best solution
		best_solution = self.copy()

		# Lagrer verdien på max(self.n_bays, self.n_stacks, self.n_tiers). Brukes til å
		# redusere antall evalueringer i nabolaget.

		max_index = max(self.n_bays, self.n_stacks, self.n_tiers)

		# Lagrer centre of gravity som cog_current, og multipliserer med vekten av alle containere for å forenkle evalueringen
		cog_current = [self.cog[0] * self.total_weight_containers, self.cog[1], self.total_weight_containers]

		# Brukes til å lagre ny verdi av cog etter bytte
		cog_temp = [0, 0]

		# Målet er å få cog så nær midten av skipet som mulig, derav:
		cog_goal = [self.n_bays/2, self.n_stacks/2]

		# Lager en liste for å lagre indeksene til containeren vi vil swappe
		location_of_container1 = [0, 0, 0]
		location_of_container2 = [0, 0, 0]

		# Lager en liste hvor vi lagrer containere som er tabu. Siden vi har satt at containere
		# som er swappet skal være ulovlige å swappe i 3 iterasjoner, vil vi få max 6 elementer i listen,
		# det er 2 containere for hver gang man swapper
		tabu = [0, 0, 0, 0, 0, 0]

		i = 0  # iteration counter

		while i < n_iterations:
			# print(i)

			i += 1

			cog_this = [0, 0]
			this_objective = self.n_bays**2 + self.n_stacks**2  # big M

			for bay1 in range(self.n_bays):
				for stack1 in range(self.n_stacks):
					for tier1 in range(self.n_tiers):
						for bay2 in range(self.n_bays):
							for stack2 in range(self.n_stacks):
								for tier2 in range(self.n_tiers):
									if bay1*max_index**2 + stack1*max_index + tier1 < bay2*max_index**2 + stack2*max_index + tier2:
										# Sjekker om noen av containerne er tabu. Hvis ja, så evaluerer vi ikke denne swappen
										evaluate_this = True

										if self.flow_x[bay1][stack1][tier1] in tabu or self.flow_x[bay2][stack2][tier2] in tabu:
											evaluate_this = False

										if bay1 == bay2 and stack1 == stack2:
											evaluate_this = False

										if evaluate_this:
											# Subtract the old contribution to the objective
											cog_temp[0] = cog_current[0] - (bay1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (bay2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight
											cog_temp[1] = cog_current[1] - (bay1 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight - (bay2 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight

											# Add the new contribution to the objective after the swap
											cog_temp[0] = cog_temp[0] + (bay2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (bay1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight
											cog_temp[1] = cog_temp[1] + (stack2 - 0.5)*containers[self.flow_x[bay1][stack1][tier1]].weight + (stack1 - 0.5)*containers[self.flow_x[bay2][stack2][tier2]].weight

											# Divide on the total weight of the containers to get the cog
											cog_temp[0] /= self.total_weight_containers
											cog_temp[1] /= self.total_weight_containers

											# Calculate the objective
											evaluation = (cog_goal[0] - cog_temp[0])**2 + (cog_goal[1] - cog_temp[1])**2

											if evaluation < this_objective:
												this_objective = evaluation
												location_of_container1 = [bay1, stack1, tier1]
												location_of_container2 = [bay2, stack2, tier2]
												cog_this = cog_temp

			# Make the swap
			temp_cont = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
			self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]] = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]
			self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]] = temp_cont

			# Update objective and cog
			self.objective = this_objective
			self.cog = cog_this
			cog_current[0] = self.cog[0] * self.total_weight_containers
			cog_current[1] = self.cog[1] * self.total_weight_containers

			# print(self.objective)
			# Hvis vi har funnet en ny best solution, så lagrer vi
			if self.objective < best_solution.objective:
				best_solution = self.copy()

			# Oppdaterer tabulisten
			b = i % len(tabu)//2

			if b == 1:
				tabu[0] = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
				tabu[1] = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]
			elif b == 2:
				tabu[2] = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
				tabu[3] = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]
			else:
				tabu[4] = self.flow_x[location_of_container1[0]][location_of_container1[1]][location_of_container1[2]]
				tabu[5] = self.flow_x[location_of_container2[0]][location_of_container2[1]][location_of_container2[2]]

			if i % 20 == 0:

				for g in range(randrange(10)):
					self.swap_two_random_containers()

				self.calculate_objective(containers)
				cog_current[0] = self.cog[0] * self.total_weight_containers
				cog_current[1] = self.cog[1] * self.total_weight_containers

		# Kopierer den beste løsningen tilbake til løsningsobjektet
		for bay in range(self.n_bays):
			for stack in range(self.n_stacks):
				for tier in range(self.n_tiers):
					self.flow_x[bay][stack][tier] = best_solution.flow_x[bay][stack][tier]

		self.objective = best_solution.objective
		self.cog = best_solution.cog
		self.total_weight_containers = best_solution.total_weight_containers
