import random
import math


class player () :

    def __init__(self , x_spawn, y_spawn,  texture , max_speed = 10) :

        self.x = x_spawn
        self.y = y_spawn
        self.x_chunk = 0
        self.y_chunk = 0
        self.texture = texture

        self.max_speed = max_speed
        
        
        # fonctions :


    def get_coords(self) :

        return self.x, self.y


    def update_player_chunk_coordinates(self, chunk_size = 32) :

        self.x_chunk = math.floor(self.x / chunk_size) 
        self.y_chunk = math.floor(self.y / chunk_size)
