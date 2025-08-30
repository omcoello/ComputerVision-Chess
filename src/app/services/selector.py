class Selector:
    def __init__(self):
        self.time_in_position = {}

    def init_time_in_position(self, board_range):
        self.time_in_position = {key: 0 for key in board_range.keys()}

    def update_positions(self, centroids, board_range, fps):
        activated = []
        for cx, cy in centroids:
            for key, p in board_range.items():
                # Usar siempre el primer y último punto de la lista para definir límites
                print("These are the points", p)
                x_min, y_min = p[0][0], p[0][1]
                x_max, y_max = p[1][0], p[2][1]

                if x_min <= cx <= x_max and y_min <= cy <= y_max:
                    self.time_in_position[key] += 1
                    if self.time_in_position[key] >= 2 * fps:  # 2 seconds
                        activated.append(key)
                else:
                    self.time_in_position[key] = 0
        return activated
