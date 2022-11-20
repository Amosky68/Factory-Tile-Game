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
            self.seed = 144
        else :
            self.seed = seed


    def absoluteChunkCoordinates(self, Tileposition) :
        # print(Tileposition)
        return ( self.position[0] + Tileposition[0]/self.chunk_size  ,  self.position[1] + Tileposition[1]/self.chunk_size  )


    def get_Tile(self,coordinates,noises,spriteCoordinatesValue) :
        noise = PerlinNoise( octaves = 1, seed = self.seed)
        # on parcours tout les noises pour crée la carte la plus détaillé possible
        value = 0
        for i , noise in enumerate(noises):
            value += noise(self.absoluteChunkCoordinates(coordinates)) * 0.5 ** i


        # Generation rules

        tilecoordinates = (coordinates[0] + self.position[0] * self.chunk_size , coordinates[1] + self.position[1] * self.chunk_size)
        if value < 0 :      # water
            return Ground(self.texturesLocations[0] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.05 : # sand
            return Ground(self.texturesLocations[1] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.15 : # Grass
            return Ground(self.texturesLocations[2] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.20 : # Ligthdark Grass
            return Ground(self.texturesLocations[3] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.25 : # dark Grass
            return Ground(self.texturesLocations[4] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.35 : # dark2 Grass
            return Ground(self.texturesLocations[5] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        else :              # rock
            return Ground(self.texturesLocations[6] , tilecoordinates , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)



    def generate(self,spriteCoordinatesValue) :
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
                temp[col][row] = self.get_Tile(Tiles[col][row] , Noises, spriteCoordinatesValue)
                
        self.Tiles = numpy.array(temp)

        # print(time.perf_counter()-timing)


    def getPositions(self):
        return self.position


    def getTileValue(self,coordinatesInsideChunk) :
        return self.Tiles[coordinatesInsideChunk[1][0]]




class Ground(arcade.Sprite):

    def __init__(self, imageLocation , physicalpos , Spritepos_x = 0 , Spritepos_y = 0 , size = 1) :

        h , v = random.choice([True,False]) , random.choice([True,False])
        # h,v = False , False
        self.sprite = arcade.Sprite(imageLocation , scale=size , center_x=Spritepos_x , center_y=Spritepos_y , flipped_horizontally=h , flipped_vertically=v)
        self.physicalPosition = physicalpos
        self.Inchunk = ()


    def move(self, x, y) :
        self.physicalPosition = (x , y)


    def resize(self,size) :
        self.sprite.scale = size




class Player(arcade.Sprite) :
    def __init__(self, imageLocation , physicalpos , chunksize ,Spritesize = 1 , spriteCoordinatesValue=100 , chunkRenderDistance=9) :

        self.chunksize = chunksize
        self.spriteCoordinatesValue = spriteCoordinatesValue
        self.sprite = arcade.Sprite(imageLocation , scale=Spritesize , center_x=physicalpos[0]*spriteCoordinatesValue , center_y=physicalpos[1]*spriteCoordinatesValue )
        self.positionMap = list(physicalpos)
        self.positionChunk = self.getChunkPosition()
        self.speed = 20   # tiles / sec

        self.chunkRenderDistance = chunkRenderDistance 


    def getChunkPosition(self) :
        return [self.positionMap[0] // self.chunksize , self.positionMap[1] // self.chunksize]


    def getPosition(self) :
        return self.positionMap

    
    def updateChunkPosition(self) :
        self.positionChunk = list(self.getChunkPosition())




class Game(arcade.Window) :
    """
    ### dans ce jeu, il y a deux types de coordonées:
        - coordonées physique : une case = 1 valeurs 
        - coordonées de sprite : une case = 100 valeurs
    
    """
    def __init__(self , screen , title):

        super().__init__(screen[0], screen[1], title)
        self.version = "1.0.0"
        self.spriteCoordinatesValue = 100

        # Map generation
        self.ProcessQueue = mp.Queue()
        self.generationSeed = 38230   # 15 - 144 - 38230
        self.chunkSize = 32
        self.renderDistance = 7

        if self.generationSeed == 0 or self.generationSeed is None :
            self.generationSeed = random.randint(1,100_000)
            print("seed :" , self.generationSeed)

        self.generationQueue = []
        self.maxParallelProcess = 8
        self.Mapdata = []
        self.textures = ['textures/water.png' , 'textures/sand2.png' ,'textures/grass.png' , 'textures/LigthdarkGrass.png',
        'textures/darkGrass.png' , 'textures/dark2Grass.png' , 'textures/stone.png']

        # Screen setup and other stuff
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

            
        # [[ self.scene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunk.Tiles]
        size = 0
        for i in range(size*size) :

            self.generationQueue.append(( i%size , i//size))

        self.player = Player(dirLocation + 'textures/stone.png' , (0,0) , self.chunkSize , Spritesize =  1 , spriteCoordinatesValue=self.spriteCoordinatesValue 
        , chunkRenderDistance=self.renderDistance)


        self.updateMapdata()


    # Arcade 


    def on_draw(self) :
        arcade.start_render()

        self.camera.use()
        self.scene.draw()

        self.player.sprite.draw()


    def on_update(self , deltaTime):

        #fps and camera update

        print(round((1/deltaTime),0) , "fps" , end='\r') 
        self.center_camera_to_player( self.player.sprite )

        # player mouvement 

        if self.keys["Z"] :
            self.player.sprite.center_y += self.player.speed * deltaTime * self.spriteCoordinatesValue
            self.player.positionMap[1]  += self.player.speed * deltaTime
        if self.keys["S"] :
            self.player.sprite.center_y -= self.player.speed * deltaTime * self.spriteCoordinatesValue
            self.player.positionMap[1]  -= self.player.speed * deltaTime
        if self.keys["Q"] :
            self.player.sprite.center_x -= self.player.speed * deltaTime * self.spriteCoordinatesValue
            self.player.positionMap[0]  -= self.player.speed * deltaTime
        if self.keys["D"]:
            self.player.sprite.center_x += self.player.speed * deltaTime * self.spriteCoordinatesValue
            self.player.positionMap[0]  += self.player.speed * deltaTime


        playerChunkCoordinates = self.player.getChunkPosition()
        if self.player.positionChunk != playerChunkCoordinates :  
            self.updateMapdata()
            self.player.updateChunkPosition()
            print("player chunk Coordinates :" ,self.player.getChunkPosition())



        # map Generation process

        # dessine les chunks déja généré 
        if not self.ProcessQueue.empty():
            chunk = self.ProcessQueue.get()
            self.Mapdata.append(chunk)
            # print(chunk)
            self.draw_single_chunk(chunk)


        # met a générer les chunks de la liste
        if len(self.generationQueue) > 0 and len(mp.active_children()) < self.maxParallelProcess:
            # si il y a des chunks a générer et qu'on ne dépasse pas la quantité max de processus alors on génrère un nouveau chunk
            coordinates = self.generationQueue.pop(0) 
            dirLocation = self.getDirectoryLocation()
            txtlist = [dirLocation + self.textures[i] for i in range(len(self.textures))] 
            
            generator = Generator(Game.generate_single_chunk , (Game,coordinates , self.chunkSize , txtlist , self.generationSeed, self.spriteCoordinatesValue , self.ProcessQueue))
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
        
        maxzoom = 35
        minzoom = 1
        
        if scroll_y < 0 :
            self.camera.scale *= 1.05
        else :
            self.camera.scale /= 1.05
        
        self.camera.scale = min(maxzoom,max(self.camera.scale,minzoom))


    # Terrain generation 


    def updateMapdata(self): 

        # read the Mapdata and store all the generated chunk coordinates

        alreadyGeneratedChunks = [] # contient les chunks et leur index dans la liste 
        for index,chunk in enumerate(self.Mapdata) :
            alreadyGeneratedChunks.append((chunk,index))

        # kill all out of range chunks
            # return the x and y distance beetween the position of the chunk and the position of the player
        distance = lambda playerPosition, chunkcoordinates : (abs(chunkcoordinates[0] - playerPosition[0]) , abs(chunkcoordinates[1] - playerPosition[1]) )
        
        # reverse the list so that we can properly delet the chunk from the Mapdata
        alreadyGeneratedChunks.reverse()
        for Gchunk in alreadyGeneratedChunks:
            # check if the chunk is to far or not
            dx , dy = distance(self.player.positionChunk , Gchunk[0].position) 
            if dx > self.player.chunkRenderDistance or dy > self.player.chunkRenderDistance :
                # if it is, we delete it and remove it from the drawing screen
                del self.Mapdata[Gchunk[1]]
                try :
                    self.scene.remove_sprite_list_by_name("Map-" + str(Gchunk[0].position))
                except :
                    print(f"le chunk n°{Gchunk[0].position} n'a pas pu être décharger")



        alreadyGeneratedChunksCoordinates = [ self.Mapdata[i].position for i in range(len(self.Mapdata))]

        # add to the generation list, all the chunks that need to be generated
        x , y = self.player.getChunkPosition()
        # print(type(self.renderDistance +x) , type(self.renderDistance +y))
        for yChunk in range(int(y - self.renderDistance) , int(y + self.renderDistance + 1)) :
            for xChunk in range(int(x - self.renderDistance) , int(x + self.renderDistance + 1)) :

                if (xChunk,yChunk) not in alreadyGeneratedChunksCoordinates and (xChunk,yChunk) not in self.generationQueue:
                    self.generationQueue.append((xChunk,yChunk))
        # for ChunkY 

    
    
        




    def generate_single_chunk(self, Chunkposition , size , TextureList , seed , spriteCoordinatesValue ,connector ):
        # generate a single chunk based on all the parameters

        chunk = Chunk( TextureList , seed = seed , chunk_size=size   , position = Chunkposition )
        chunk.generate(spriteCoordinatesValue)
    
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

    game = Game((1280,920),"jeu")
    game.run()

    # clear every existing process

    childprocess = mp.active_children()
    for process in childprocess :
        process.terminate()
