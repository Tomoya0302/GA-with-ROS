import random
import numpy as np
from evaluate import Robot
import time

class GA():

    def __init__(self):
        # 問題設定
        self.pick_pos = np.array([4, 4, 4]) # pick-up位置は固定
        self.place_pos_z = 0 # place位置のz座標は固定
        # 決定変数（ロボットの配置座標，姿勢，プレース位置座標）の範囲
        # robot_x[0:4], robot_y[0:4], robot_z[0:4], robot_posture[0:23], place_x[0:4], place_y[0:4]
        self.lower_bounds = [0, 0, 0, 0, 0, 0]
        self.upper_bounds = [4, 4, 4, 23, 4, 4]

        # 遺伝子の長さ
        self.chromosome_length = len(self.lower_bounds)

        # GAのパラメータ
        self.population_size = 100
        self.generations = 100
        self.crossover_rate = 0.9
        self.mutation_rate = 0.05

        # 最大化問題(True) or 最小化問題(False)
        self.maximization_problem = False

        # 評価関数
        self.eval = Robot()

    # 評価関数
    def evaluate(self, individual):
        x1, x2, x3, x4, x5, x6 = individual
        # l = np.linalg.norm(self.pick_pos - np.array([x5, x6, self.place_pos_z])) # pick-up位置からplace位置までの距離
        return self.eval.evaluate(pick = self.pick_pos,
                                  place = np.array([x5, x6, 0]), 
                                  robot_position = np.array([x1, x2, x3]), 
                                  robot_posture = x4)[0]
    
    # 初期個体を生成
    def generate_individual(self):
        return [random.randint(self.lower_bounds[i], self.upper_bounds[i]) for i in range(self.chromosome_length)]

    # 交叉
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, self.chromosome_length - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    # 突然変異
    def mutate(self, individual):
        for i in range(self.chromosome_length):
            if random.random() < self.mutation_rate:
                individual[i] = random.randint(self.lower_bounds[i], self.upper_bounds[i])
        return individual

    # GA
    def genetic_algorithm(self, population_size, generations, crossover_rate, mutation_rate):
        population = [self.generate_individual() for i in range(population_size)]
        for i in range(generations):
            print('Gen.: ', i)
            population = sorted(population, key=self.evaluate, reverse=self.maximization_problem)
            # エリート選択
            new_population = population[:int(population_size/2)]
            # 交叉
            for j in range(int(population_size/2)):
                parent1 = random.choice(population[:int(population_size/2)])
                parent2 = random.choice(population[:int(population_size/2)])
                if random.random() < crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                    new_population.append(child1)
                    new_population.append(child2)
            # 突然変異
            for j in range(len(new_population)):
                new_population[j] = self.mutate(new_population[j])
            population = new_population
        return sorted(population, key=self.evaluate, reverse=self.maximization_problem)[0]

    def main(self):
        # 最適解を探索
        start_time = time.time()
        best_individual = self.genetic_algorithm(self.population_size, self.generations, self.crossover_rate, self.mutation_rate)
        elapsed_time = time.time() - start_time

        # 結果を出力
        print("Best fitness: ", self.evaluate(best_individual))

        robot_position = [best_individual[:3]]
        robot_posture = best_individual[3]
        place_position = [best_individual[4:]]

        print('Robot position (x, y, z) :', robot_position)
        print('Robot posture :', robot_posture) 
        print('Place position (x, y) :', place_position)
        print('-'*30)
        print('Elapsed time :', elapsed_time)

if __name__ == '__main__':
    ga = GA()
    ga.main()
