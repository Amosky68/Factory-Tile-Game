from perlin_noise import PerlinNoise
import arcade
import random
import Tileclass
import Chunkclass
import math
import Camera2D 
from Player import player
import pickle 
import os
import time

screen_x = 720
screen_y = 720

"""
Notes :

le nombre maximum de chunk sera limité a 65535 (FFFF en hexa) soit une map de 2.000.000+ blocs 



"""


class MyWindow(arcade.Window):


    def __init__(self):
        super().__init__(screen_x, screen_y, "Tile Game", resizable=True )

        self.player = player(16,16,"texture")
        self.camera = Camera2D.Physical_Screen(zoom = 10)
        self.seed = 15
        
        self.fps = 0
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.details = 1

        self.loading_distance = 2

        self.color_list = [(0,50,143) , (220,250,0) , (20,180,26) , (90,90,90)]
        self.texture_list = [ arcade.load_texture("textures/Water.png" , hit_box_algorithm='None') , arcade.load_texture("textures/Sand.png" , hit_box_algorithm='None')  , 
                              arcade.load_texture("textures/Grass.png" , hit_box_algorithm='None') , arcade.load_texture("textures/stone.png" , hit_box_algorithm='None')  ]

        self.chunk_size = 32
        self.map_data = []    

        self.key = [False , False , False , False]   # z , q , s , d


        self.enable_textures = False
        self.save_name = "test4"

        self.see_chunk_border = False
        self.chunks_corner = ()
        self.calculate_new_frame = True
        
        #  fonctions à executer :

        self.create_save_file()     #  les données seront stockée de la manière suivante : "<chunk_x+32767><chunk_y+32767>.pickle"  ( les coordonées étant en hexa)
        self.player.update_player_chunk_coordinates(self.chunk_size)
        self.Update_map()
        self.update_chunk_corner(self.player.x_chunk , self.player.y_chunk)
        



    def create_save_file(self) :

        existing_saves = os.listdir("Saves")

        if self.save_name == "" :
            default_name = "world"

            for i in range(len(existing_saves) + 1) :
                self.save_name = default_name + str(i)
                if self.save_name not in existing_saves :

                    os.mkdir("Saves/" + self.save_name)
                    break

        else :
            if self.save_name not in existing_saves :
                os.mkdir("Saves/" + self.save_name)

            

    def on_draw(self) :
        arcade.start_render()

        screen_center = ( self.player.x , self.player.y )


        self.camera.calculate_orgin_from_center_phy(screen_center[0] , screen_center[1] , self.screen_x , self.screen_y)

        # for chunk in self.map_data :
        #     for y in range(self.chunk_size) :
        #         for x in range(self.chunk_size) :

        #             absolute_coordinates = chunk.get_absolutes_tile_coordinates(x,y)
        #             tile_x , tile_y = self.camera.to_screen( absolute_coordinates[0] , absolute_coordinates[1] )


        #             if self.enable_textures :
        #                 arcade.draw_texture_rectangle(tile_x , tile_y , self.camera.zoom  , self.camera.zoom  , chunk.get_tile_from_chunk_coordinates(x,y).texture , 0)
        #             else :
                
        #                 arcade.draw_point( tile_x , tile_y , chunk.get_tile_from_chunk_coordinates(x,y).color , self.camera.zoom )


        all_color_tiles = [ [] for i in range(len(self.color_list))]
        for i , color in enumerate(self.color_list ) :
            all_color_tiles[i].append(color)

        total_chunk = (self.loading_distance * 2 - 1) ** 2
        chunk_rendered = 0
        self.details = int((1/self.camera.zoom + 1.1)**4)
        for chunk in self.map_data :        #  cette boucle prend du temps 0.01 s

            if self.need_to_be_shown(chunk , self.get_chunk_coordonates(screen_center[0] , screen_center[1] , self.chunk_size)) :
                chunk_rendered += 1

                for y in range(self.chunk_size) :
                    if y % self.details == 0 :
                        for x in range(self.chunk_size) :

                            if x % self.details == 0 :
                                absolute_coordinates = chunk.get_absolutes_tile_coordinates(x,y)
                                tile_x , tile_y = self.camera.to_screen( absolute_coordinates[0] , absolute_coordinates[1] )

                                

                                all_color_tiles[self.color_list.index(chunk.get_tile_from_chunk_coordinates(x,y).color)].append((tile_x , tile_y))


        print("chunk rendred : " , chunk_rendered/total_chunk * 100 , " %")


        for i , color in enumerate(self.color_list ) :
            arcade.draw_points(all_color_tiles[i][1:] , color , self.camera.zoom * self.details)

        self.calculate_new_frame = False


        # dessine la bordure des chunks

        if self.see_chunk_border :
            for point in range(4) :

                line_x1 , line_y1 = self.camera.to_screen( self.chunks_corner[point-1][0] ,  self.chunks_corner[point-1][1] )
                line_x2 , line_y2 = self.camera.to_screen( self.chunks_corner[point][0] ,  self.chunks_corner[point][1] )
                arcade.draw_line(line_x1 , line_y1 , line_x2 , line_y2 , (255 , 0 , 0) , 2)




        arcade.draw_text(str(round(self.fps,1)) , 100 , 100)
        arcade.draw_text(str(self.camera.zoom) , 100 , 150)
        # arcade.draw_points(tile_type[1:] , tile_type[0] , size = int(self.screen_x/50))  

        arcade.draw_circle_filled(self.screen_x/2, self.screen_y/2 , 5 , (0,255,255))  
            


    def on_update(self, delta_time):

        self.fps = 1/delta_time

        # mouvement du joueur :
        

        if self.key[0] :
            self.player.y += self.player.max_speed * delta_time
        if self.key[1] :
            self.player.x -= self.player.max_speed * delta_time
        if self.key[2] :
            self.player.y -= self.player.max_speed * delta_time
        if self.key[3] :
            self.player.x += self.player.max_speed * delta_time

        previous_chunk_coordinates = (self.player.x_chunk , self.player.y_chunk)
        self.player.update_player_chunk_coordinates(self.chunk_size)

        if previous_chunk_coordinates[0] != self.player.x_chunk or  previous_chunk_coordinates[1] != self.player.y_chunk :
            self.Update_map()

            #  update la variable chunk corner :

            self.update_chunk_corner(self.player.x_chunk , self.player.y_chunk)
            self.calculate_new_frame = True




    def on_key_press(self, symbol: int, modifiers: int):
        
        if symbol == arcade.key.Z :
            self.key[0] = True
        if symbol == arcade.key.Q :
            self.key[1] = True
        if symbol == arcade.key.S :
            self.key[2] = True
        if symbol == arcade.key.D :
            self.key[3] = True


    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Z :
            self.key[0] = False
        if symbol == arcade.key.Q :
            self.key[1] = False
        if symbol == arcade.key.S :
            self.key[2] = False
        if symbol == arcade.key.D :
            self.key[3] = False


    def get_chunk_coordonates(self , player_x , player_y, chunk_size = 32) :

        x = math.floor(player_x / chunk_size) 
        y = math.floor(player_y / chunk_size)
        return x,y


    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        mini = 3.75
        maxi = 30

        value =  max( self.camera.zoom * (1 + scroll_y/20) , mini)
        value =  min( value , maxi  )
        self.camera.update_zoom(value)



    def Update_map (self) : 

        loaded_chunk = []
        for chunk_index in range(len(self.map_data) -1 , -1 , -1) :     #  supprime les chunks a ne plus charger 

            chunks = self.map_data[chunk_index]
            dx = chunks.chunk_x - self.player.x_chunk  
            dy = chunks.chunk_y - self.player.y_chunk 


            if abs(dx) > self.loading_distance - 1 or abs(dy) > self.loading_distance - 1 :
                self.unload_chunk(chunks)
                del self.map_data[chunk_index]
            else :
                loaded_chunk.append((chunks.chunk_x , chunks.chunk_y))

        z = time.time()

        for cy in range(self.loading_distance - 1     , - self.loading_distance , -1) :     # charge les nouveaux chunks 
            for cx in range(self.loading_distance - 1 , - self.loading_distance , -1) :

                lx = cx + self.player.x_chunk
                ly = cy + self.player.y_chunk

                if (lx , ly) not in loaded_chunk :

                    self.load_chunk(lx , ly)
                    

        print(time.time() - z , " sec")



    def load_chunk(self, x , y):

        chunk_saving_path = "Saves/" + self.save_name
        existing_chunk_saves = os.listdir(chunk_saving_path)

        chunk_save_name = self.get_chunk_save_name(x, y)
        if chunk_save_name in existing_chunk_saves :

            input = open(self.get_chunk_save_path(x,y) , "rb")
            self.map_data.append( pickle.load(input))
            input.close()

        else :


            self.map_data.append(Chunkclass.Chunk(x , y , self.texture_list , self.color_list , self.chunk_size))
            self.map_data[-1].generate_chunk(seed=self.seed , zoom=4)
        

    def unload_chunk(self , chunk) :

        get_chunk_save_path = self.get_chunk_save_path(chunk.chunk_x, chunk.chunk_y)
        print(get_chunk_save_path)

        output = open(get_chunk_save_path , "wb")
        pickle.dump(chunk , output)
        output.close()


    def get_chunk_save_path(self , x , y) :

        return "Saves/"   +  self.save_name  +   "/"   +  self.get_chunk_save_name(x,y)


    def get_chunk_save_name(self , x , y) :

        return self.four_digit_hexa(x + 32767) + self.four_digit_hexa(y + 32767) + "chunk.pickle"


    def four_digit_hexa(self , number) :
    
        hexa = hex(number)[2:]
        return ("0" * (4 - len(hexa))) + hexa


    def on_close(self):
        
        for chunk_index in range(len(self.map_data) -1 , -1 , -1) :   #  enregistre les chunks encore chargée

            chunks = self.map_data[chunk_index]
            self.unload_chunk(chunks)
            del self.map_data[chunk_index]


    def update_chunk_corner(self, chunk_x, chunk_y) :

        corner = []
        corner.append( (  chunk_x * self.chunk_size , chunk_y * self.chunk_size ) )
        corner.append( (  chunk_x * self.chunk_size , (chunk_y + 1) * self.chunk_size ) )
        corner.append( (  (chunk_x  + 1)* self.chunk_size , (chunk_y + 1) * self.chunk_size ) )
        corner.append( (  (chunk_x  + 1)* self.chunk_size , chunk_y * self.chunk_size ) )

        self.chunks_corner =  corner[:]


    def need_to_be_shown(self , chunk , screen_center = ( 0 , 0 )) :

        d = ( self.camera.zoom * self.chunk_size )
        window_cux = self.screen_x / d 
        window_cuy = self.screen_y / d 

        x_distance = window_cux/2 + 0.5
        y_distance = window_cuy/2 + 0.5

        return abs( chunk.chunk_x - screen_center[0] ) < x_distance  and  abs( chunk.chunk_y - screen_center[1] ) < y_distance 
        




# mer < -0.1 
# sable < -0.07
# plaine < 0.25
# pierre > 0.25



window = MyWindow()
arcade.run()  
