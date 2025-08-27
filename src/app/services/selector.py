class Selector:
    def __init__(self):
        self.time_in_position = {}

    def init_time_in_position(self, board_range):
        self.time_in_position = {key: 0 for key in board_range.keys()}

    def update_positions(self, centroids, board_range, fps):
        activated = []
        for cx, cy in centroids:
            for key, p in board_range.items():
                if p[0][0] <= cx <= p[1][0] and p[0][1] <= cy <= p[2][1]:
                    self.time_in_position[key] += 1
                    if self.time_in_position[key] >= 2 * fps:  # 2 seconds
                        activated.append(key)
                else:
                    self.time_in_position[key] = 0
        return activated
