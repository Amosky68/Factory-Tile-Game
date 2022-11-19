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

    def __init__(self , texturesLocation , seed = None ,chunk_size = 32 , position = (0,0)) :
        self.chunk_size = chunk_size
        self.position = position
        self.Tiles = None
        self.texturesLocations = texturesLocation
        if seed is None :
            self.seed = 0
        else :
            self.seed = seed


    def absoluteChunkCoordinates(self, Tileposition) :
        # print(Tileposition)
        return ( self.position[0] + Tileposition[0]/self.chunk_size  ,  self.position[1] + Tileposition[1]/self.chunk_size  )


    def get_Tile(self,coordinates,noises) :
        noise = PerlinNoise( octaves = 1, seed = self.seed)
        # on parcours tout les noises pour crée la carte la plus détaillé possible
        value = 0
        for i , noise in enumerate(noises):
            value += noise(self.absoluteChunkCoordinates(coordinates)) * 0.5 ** i


        # Generation rules

        tilecoordinates = (coordinates[0] + self.position[0] * self.chunk_size , coordinates[1] + self.position[1] * self.chunk_size)
        if value < 0 :
            return Ground(self.texturesLocations[0] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)
        elif value < 0.05 :
            return Ground(self.texturesLocations[1] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)
        elif value < 0.35 :
            return Ground(self.texturesLocations[2] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)
        else :
            return Ground(self.texturesLocations[3] , tilecoordinates , tilecoordinates[0] * 100 , tilecoordinates[1] * 100 , 5)





    def generate(self) :
        timing = time.perf_counter()

        zoom = 0.35 
        zoom *= self.chunk_size / 32
        Noises = []
        # Noises.append(PerlinNoise(octaves=zoom*0.25  ,seed=self.seed))
        for i in range(6) :
            Noises.append(PerlinNoise(octaves=zoom*0.5 * 2**i  ,seed=self.seed)) 
        # Noises.append(PerlinNoise(octaves=zoom*1  ,seed=self.seed))
        # Noises.append(PerlinNoise(octaves=zoom*2  ,seed=self.seed))
        # Noises.append(PerlinNoise(octaves=zoom*4  ,seed=self.seed))
        # Noises.append(PerlinNoise(octaves=zoom*8 ,seed=self.seed))
        # Noises.append(PerlinNoise(octaves=zoom*16 ,seed=self.seed))


        Tiles =  [[(i,j) for i in range(self.chunk_size)] for j in range(self.chunk_size)] 
        # print(Tiles)
        temp = Tiles[:]
        Tiles = numpy.array(Tiles)
        # print(Tiles)

        for row in range(self.chunk_size):
            for col in range(self.chunk_size) :
                temp[col][row] = self.get_Tile(Tiles[col][row] , Noises)
                
        self.Tiles = numpy.array(temp)

        # print(time.perf_counter()-timing)


    def getPositions(self):
        return self.position




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
        self.version = "1.0.0"

        self.ProcessQueue = mp.Queue()
        self.generationSeed = 144
        self.generationQueue = []
        self.maxParallelProcess = 8
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

        size = 20
        for i in range(size*size) :

            self.generationQueue.append((i%size - size//2 , i//size - size//2))

            
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
            self.player.center_y += 4000 * deltaTime
        if self.keys["S"] :
            self.player.center_y -= 4000 * deltaTime
        if self.keys["Q"] :
            self.player.center_x -= 4000 * deltaTime
        if self.keys["D"]:
            self.player.center_x += 4000 * deltaTime

        # map Generation process

        if not self.ProcessQueue.empty():
            chunk = self.ProcessQueue.get()
            # print(chunk)
            self.draw_single_chunk(chunk)



        if len(self.generationQueue) > 0 and len(mp.active_children()) < self.maxParallelProcess:
            # si il y a des chunks a générer et qu'on ne dépasse pas la quantité max de processus alors on génrère un nouveau chunk
            coordinates = self.generationQueue.pop(0) 
            dirLocation = self.getDirectoryLocation()
            txtlist = [dirLocation +'textures/water.png' , dirLocation +'textures/sand.png' , dirLocation +'textures/grass.png' , dirLocation +'textures/stone.png'] 
            
            generator = Generator(Game.generate_single_chunk , (Game,coordinates , 32 , txtlist , self.generationSeed , self.ProcessQueue))
            # self.generate_single_chunk((i%size , i//size) , 128 , txtlist)
            generator.run()


            



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


    def generate_single_chunk(self, Chunkposition , size , TextureList , seed ,connector ):
        # generate a single chunk based on all the parameters

        chunk = Chunk( TextureList , seed = seed , chunk_size=size   , position = Chunkposition )
        chunk.generate()
    
        connector.put(chunk)



    def draw_single_chunk(self, chunkdata) :
        # draw a chunk using it's data

        t = time.perf_counter()

        chunkName = chunkdata.getPositions()
        chunkName = "Map-" + str(chunkName)
        for row in chunkdata.Tiles :
            for tile in row :
                self.scene.add_sprite(chunkName, tile.sprite)

        # [[ self.scene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunkdata.Tiles]
        # print(f'it took {time.perf_counter() - t} seconds to draw this chunk')



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

    game = Game((1600,1200),"jeu")
    game.run()

    # clear every existing process

    childprocess = mp.active_children()
    for process in childprocess :
        process.terminate()
