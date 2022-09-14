import Tileclass
from perlin_noise import PerlinNoise
import random
import Tileclass
import time
import py_compile



class Chunk () :

    def __init__(self , chunk_x , chunk_y ,  texture_list , color_list   ,chunk_size = 32) :

        self.Tiles_list = None      
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.chunk_size = chunk_size
        self.texture_list = texture_list
        self.color_list = color_list
        
        
    

    def generate_chunk(self , seed = 0 , zoom = 1) :

        

        noise1 = PerlinNoise(octaves=1/zoom  ,seed=seed)    # génère touts les bruits de perlin 
        noise2 = PerlinNoise(octaves=2/zoom  ,seed=seed)
        noise3 = PerlinNoise(octaves=4/zoom  ,seed=seed)
        noise4 = PerlinNoise(octaves=8/zoom  ,seed=seed)
        noise5 = PerlinNoise(octaves=16/zoom ,seed=seed)
        noise6 = PerlinNoise(octaves=32/zoom ,seed=seed)


        self.Tiles_list = [ [] for x in range(self.chunk_size)]

        
        

        for y in range( self.chunk_size):
            for x in range( self.chunk_size):


                a =  x/ self.chunk_size  +  self.chunk_x   
                b =  y/ self.chunk_size  +  self.chunk_y
                noise_val =             noise1([ a , b ])
                noise_val += 0.5 *      noise2([ a , b ])
                noise_val += 0.25 *     noise3([ a , b ])
                noise_val += 0.125 *    noise4([ a , b ])
                noise_val += 0.0625 *   noise5([ a , b ])
                noise_val += 0.03125 *  noise6([ a , b ])

                

                absolute_x , absolute_y = self.get_absolutes_tile_coordinates(x , y)

                if noise_val < -0.35 :
                    self.Tiles_list[y].append(Tileclass.Tile(absolute_x , absolute_y  , self.color_list[0] , self.texture_list[0]))
                elif noise_val < -0.25 :
                    self.Tiles_list[y].append(Tileclass.Tile(absolute_x , absolute_y  , self.color_list[1] , self.texture_list[1]))
                elif noise_val < 0.25 :
                    self.Tiles_list[y].append(Tileclass.Tile(absolute_x , absolute_y  , self.color_list[2] , self.texture_list[2]))
                else :
                    self.Tiles_list[y].append(Tileclass.Tile(absolute_x , absolute_y  , self.color_list[3] , self.texture_list[3]))

                
    
        
    def get_tile_from_chunk_coordinates(self, x , y):
        return self.Tiles_list[y][x]


    def get_absolutes_tile_coordinates(self , chunk_x , chunk_y) :
        return  self.chunk_size*self.chunk_x  + chunk_x   ,    self.chunk_size*self.chunk_y  + chunk_y


# a = Chunk(0, 0 , [(0,50,143) , (220,250,0) , (20,180,26) , (90,90,90)] , [(0,50,143) , (220,250,0) , (20,180,26) , (90,90,90)] ,  chunk_size=32)

# print(a.Tiles_list)