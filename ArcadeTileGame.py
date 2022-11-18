import arcade
import random
from perlin_noise import PerlinNoise
import numpy
import time
import multiprocessing as mp


class Generator():

    def __init__(self , func , paremeters = None ) :

        if paremeters is None :
            self.process = mp.Process(target = func)
        elif paremeters is not None :
            self.process = mp.Process(target = func , args = paremeters)

    def run(self):
        self.process.start()





class Chunk():

    def __init__(self , texturesLocation , chunk_size = 32 , position = (0,0)) :
        self.chunk_size = chunk_size
        self.position = position
        self.Tiles = None
        self.texturesLocations = texturesLocation


    def absoluteChunkCoordinates(self, Tileposition) :
        # print(Tileposition)
        return ( self.position[0] + Tileposition[0]/self.chunk_size  ,  self.position[1] + Tileposition[1]/self.chunk_size  )


    def get_Tile(self,coordinates) :
        seed = 15
        noise = PerlinNoise( octaves = 1, seed = seed)
        value = noise( self.absoluteChunkCoordinates(coordinates))

        tilecoordinates = (coordinates[0] + self.position[0] * self.chunk_size , coordinates[1] + self.position[1] * self.chunk_size)
        if value < 0 :
            return Ground(self.texturesLocations[0] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)
        elif value < 0.05 :
            return Ground(self.texturesLocations[1] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)
        else :
            return Ground(self.texturesLocations[2] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)


    def generate(self) :
        timing = time.perf_counter()

        Tiles =  [[(i,j) for i in range(self.chunk_size)] for j in range(self.chunk_size)] 
        # print(Tiles)
        Tiles = numpy.array(Tiles)
        # print(Tiles)


        self.Tiles = numpy.array([list(map( self.get_Tile , row )) for row in Tiles])
        print(time.perf_counter()-timing)






class Ground(arcade.Sprite):

    def __init__(self, imageLocation , physicalpos , Spritepos_x = 0 , Spritepos_y = 0 , size = 1) :

        self.sprite = arcade.Sprite(imageLocation , scale=size , center_x=Spritepos_x , center_y=Spritepos_y)
        self.physicalPosition = physicalpos
        self.Inchunk = ()


    def move(self, x, y) :
        self.physicalPosition = (x , y)


    def resize(self,size) :
        self.sprite.scale = size










class Game(arcade.Window) :
    def __init__(self , screen , title):

        super().__init__(screen[0], screen[1], title)

        self.ProcessQueue = mp.Queue()
        self.setup()

        self.set_update_rate(1/200)
        self.keys = {"Z" : False , "Q" : False , "S" : False, "D" : False }

        



    def getDirectoryLocation(self):
        Location = __file__ 
        for i in range(len(Location)-1 , 0 , -1):
            if Location[i] in '\/' :
                return Location[:i+1]



    def setup(self):

        dirLocation = self.getDirectoryLocation()
        self.spriteList = arcade.SpriteList()

        self.camera = arcade.Camera(self.width, self.height)
        self.camera.scale = 20

        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Ground")    # on dessinera chaques chunks avec son propre nom (self.scene.add_sprite_list("ground-77158FF2"))
                                                # cela va permètre de (self.scene.remove_sprite_list_by_name("ground-77158FF2"))
        
        
        # size = 5 # 100 pixel square
        # choice = ['textures/water.png' , 'textures/grass.png' , 'textures/stone.png' , 'textures/sand.png']
        # self.totalSprite = 12000
        # for i in range(int(self.totalSprite)) :

        #     water = Ground(dirLocation + random.choice(choice) , (( i % 120 ),( i // 120 )) , size = size )

        #     water.sprite.center_x = ( i % 120 ) * 100
        #     water.sprite.center_y = ( i // 120 ) * 100

        #     self.scene.add_sprite("Ground", water.sprite)

        size = 5
        for i in range(25) :

            txtlist = [dirLocation +'textures/water.png' , dirLocation +'textures/sand.png' , dirLocation +'textures/grass.png' , dirLocation +'textures/stone.png'] 
            
            generator = Generator(Game.generate_single_chunk , (Game,(i%size , i//size) , 32 , txtlist , self.ProcessQueue))
            # self.generate_single_chunk((i%size , i//size) , 128 , txtlist)
            generator.run()

            # [[ self.scene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunk.Tiles]



        self.player = arcade.Sprite(dirLocation + 'textures/stone.png' , scale=1 , center_x=6000 , center_y=6000)


    # Arcade 


    def on_draw(self) :
        arcade.start_render()

        self.camera.use()
        self.scene.draw()

        # self.player.draw()


    def on_update(self , deltaTime):

        print(round((1/deltaTime),0) , "fps" , end='\r') 
        self.center_camera_to_player( self.player )

        if self.keys["Z"] :
            self.player.center_y += 1000 * deltaTime
        if self.keys["S"] :
            self.player.center_y -= 1000 * deltaTime
        if self.keys["Q"] :
            self.player.center_x -= 1000 * deltaTime
        if self.keys["D"]:
            self.player.center_x += 1000 * deltaTime


        if not self.ProcessQueue.empty():

            chunk = self.ProcessQueue.get()
            self.draw_single_chunk(chunk)




    def on_key_press(self, symbol: int, modifiers: int):
        
        if symbol == arcade.key.Z :
            self.keys["Z"] = True
        if symbol == arcade.key.S :
            self.keys["S"] = True
        if symbol == arcade.key.Q :
            self.keys["Q"] = True
        if symbol == arcade.key.D :
            self.keys["D"] = True


    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Z :
            self.keys["Z"] = False
        if symbol == arcade.key.S :
            self.keys["S"] = False
        if symbol == arcade.key.Q :
            self.keys["Q"] = False
        if symbol == arcade.key.D :
            self.keys["D"] = False


    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        
        if scroll_y < 0 :
            self.camera.scale *= 1.05
        else :
            self.camera.scale /= 1.05


    # Terrain generation 


    def generate_single_chunk(self, Chunkposition , size , TextureList , connector):

        chunk = Chunk( TextureList , chunk_size=size   , position = Chunkposition )
        chunk.generate()
    
        connector.put(chunk)



    def draw_single_chunk(self, chunkdata) :

        t = time.perf_counter()

        for row in chunkdata.Tiles :
            for tile in row :
                self.scene.add_sprite("Ground", tile.sprite)

        # [[ self.scene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunkdata.Tiles]
        print(f' i took {time.perf_counter() - t} seconds to draw this chunk')



    # camera 

    def center_camera_to_player(self , player):
        screen_center_x = player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = player.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        # if screen_center_x < 0:
        #     screen_center_x = 0
        # if screen_center_y < 0:
        #     screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        # print(player_centered)

        self.camera.move_to(player_centered)






if __name__ == '__main__' : 

    game = Game((800,600),"jeu")
    game.run()