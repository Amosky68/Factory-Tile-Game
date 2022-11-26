from perlin_noise import PerlinNoise
import arcade
import random
import numpy
import time
import multiprocessing as mp
from numba import jit
import math
import os


class Generator():

    def __init__(self , func , paremeters = None ) :

        if paremeters is None :
            self.process = mp.Process(target = func)
        elif paremeters is not None :
            self.process = mp.Process(target = func , args = paremeters)

    def run(self):
        self.process.start()




class Buildings():

    def __init__(self , position , SpritesFolder , animationSpeed , spriteCoordinatesValue , chunksize , direction = "up"):
        self.position = position
        self.positionInChunk = position[0] // chunksize , position[1] // chunksize
        self.creationTime = time.perf_counter()

        # self.sprite = arcade.AnimatedTimeBasedSprite()

        self.animationList = []
        self.acctualTextureIndex = 0
        self.loadtextures(SpritesFolder)
        self.direction = {"up" : False , "right" : False , "down" : False , "left" : False}
        self.direction[direction] = True

        self.sprite = arcade.Sprite(scale = 5 , center_x=self.position[0] * spriteCoordinatesValue , center_y=self.position[1] * spriteCoordinatesValue , 
        angle = self.getangleFromDirection())
        self.animationSpeed = animationSpeed  # expressed in seconds per frame

        self.updateAnimation()



    def getangleFromDirection(self):
        for index,value in enumerate(self.direction.values()) :
            if value :
                return index * (-90) + 90   # math.pi / 180 



    def updateAnimation(self):
        self.acctualTextureIndex = (time.perf_counter()) // self.animationSpeed
        self.acctualTextureIndex %= len(self.animationList)
        self.sprite.texture = self.animationList[int(self.acctualTextureIndex)]



    def loadtextures(self, SpritesFolder):
        self.animationList = []
        files = os.listdir(SpritesFolder)
        basename = files[0][:-5]
        totaltextures = 0
        for file in os.listdir(SpritesFolder):
            if file[-4:] == '.png' :
                totaltextures += 1
                
        for index in range(totaltextures)  : 
            self.animationList.append( arcade.load_texture( SpritesFolder + '/' + basename + str(index+1) + '.png') )




class Chunk():

    def __init__(self , texturesLocation , seed = None ,chunk_size = 32 , position = (0,0) , neigthborschunks=None) :
        self.chunk_size = chunk_size
        self.position = position
        self.Tiles = None
        self.texturesLocations = texturesLocation
        self.spritelist = None
        self.seed = seed
        if seed is None :
            self.seed = 144
        self.neigthborschunks = neigthborschunks
        if neigthborschunks is None :
            self.neigthborschunks = []


        self.buildings = {}   # this variable is containing all of the buildings in the chunk
        self.buildingSpritelist = arcade.SpriteList()
        


    def absoluteChunkCoordinates(self, Tileposition) :
        # print(Tileposition)
        return ( self.position[0] + Tileposition[0]/self.chunk_size  ,  self.position[1] + Tileposition[1]/self.chunk_size  )



    def get_Tile(self,coordinates,noises,spriteCoordinatesValue) :
        noise = PerlinNoise( octaves = 1, seed = self.seed)
        # on parcours tout les noises pour crée la carte la plus détaillé possible
        value = 0
        for i , noise in enumerate(noises):
            value += noise(self.absoluteChunkCoordinates(coordinates)) * 0.5 ** i


        oreplacementNoise = PerlinNoise( octaves = 1, seed = self.seed+1)
        oreplacementvalue = oreplacementNoise(self.absoluteChunkCoordinates(coordinates))

        oretypeNoise = PerlinNoise( octaves = 0.2, seed = self.seed+2 )
        oretypevalue = oretypeNoise(self.absoluteChunkCoordinates(coordinates))

        # ore Generation rule

        if oreplacementvalue > 0.40 :
            if oretypevalue < -0.15 :
                oretype = "iron"

            elif oretypevalue < 0 :
                oretype = "coal"

            elif oretypevalue < 0.15 :
                oretype = "copper"

            else :
                oretype = None

        else :
            oretype = None


        # Generation rules

        tilecoordinates = (coordinates[0] + self.position[0] * self.chunk_size , coordinates[1] + self.position[1] * self.chunk_size)
        if value < 0 :      # water
            return Ground(self.texturesLocations[0]  , tilecoordinates , None , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.05 : # sand
            return Ground(self.texturesLocations[1]  , tilecoordinates , None , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.15 : # Grass
            return Ground(self.texturesLocations[2]  , tilecoordinates , oretype , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.20 : # Ligthdark Grass
            return Ground(self.texturesLocations[3]  , tilecoordinates , oretype , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.25 : # dark Grass
            return Ground(self.texturesLocations[4]  , tilecoordinates , oretype , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        elif value < 0.35 : # dark2 Grass
            return Ground(self.texturesLocations[5]  , tilecoordinates , oretype , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)
        else :              # rocks
            return Ground(self.texturesLocations[6]  , tilecoordinates , None , tilecoordinates[0] * spriteCoordinatesValue , tilecoordinates[1] * spriteCoordinatesValue , 5)



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
                temp[col][row] = self.get_Tile(Tiles[col][row] , Noises, spriteCoordinatesValue )
                
        self.Tiles = numpy.array(temp)

        # print(time.perf_counter()-timing)


    def getPositions(self):
        return self.position


    def getTileValue(self,coordinatesInsideChunk) :
        return self.Tiles[coordinatesInsideChunk[1][0]]


    def updateSpritelist(self):

        self.spritelist = arcade.SpriteList()
        for y in range(self.chunk_size) :
            for x in range( self.chunk_size) :
                self.spritelist.append(self.Tiles[y][x].sprite)
                if self.Tiles[y][x].oretype is not None :
                    self.spritelist.append(self.Tiles[y][x].oresprite)




class Ground(arcade.Sprite):

    def __init__(self, imageLocation , physicalpos , oretype=None , Spritepos_x = 0 , Spritepos_y = 0 , size = 1) :

        h , v = random.choice([True,False]) , random.choice([True,False])
        # h,v = False , False

        self.dirLocation = self.getDirectoryLocation()
        self.sprite = arcade.Sprite(imageLocation , scale=size , center_x=Spritepos_x , center_y=Spritepos_y , flipped_horizontally=h , flipped_vertically=v)
        
        self.oretype = oretype
        self.oresprite = None
        if oretype is not None :
            self.oresprite = arcade.Sprite(self.getOretexturelocation(oretype) , scale=size , center_x=Spritepos_x , center_y=Spritepos_y , flipped_horizontally=h , flipped_vertically=v )
        
        self.physicalPosition = physicalpos
        self.Inchunk = ()
        

    def move(self, x, y) :
        self.physicalPosition = (x , y)


    def resize(self,size) :
        self.sprite.scale = size


    def getOretexturelocation(self,oretype):

        Location = self.dirLocation
        ores = {"iron" : Location+"textures/ironOre.png"   ,   "copper" : Location+"textures/copperOre.png"   ,   "coal" : Location+"textures/coalOre.png"   }
        return ores[oretype]


    def getDirectoryLocation(self):
        Location = __file__ 
        for i in range(len(Location)-1 , 0 , -1):
            if Location[i] in '\/' :
                return Location[:i+1]




class Player(arcade.Sprite) :
    def __init__(self, imageLocation , physicalpos , chunksize ,Spritesize = 1 , spriteCoordinatesValue=100 , chunkRenderDistance=9) :

        self.chunksize = chunksize
        self.spriteCoordinatesValue = spriteCoordinatesValue
        self.sprite = arcade.Sprite(imageLocation , scale=Spritesize , center_x=physicalpos[0]*spriteCoordinatesValue , center_y=physicalpos[1]*spriteCoordinatesValue )
        self.positionMap = list(physicalpos)
        self.positionChunk = self.getChunkPosition()
        self.speed = 7   # tiles / sec

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

        self.DevMode = False

        self.beginTime = time.perf_counter()
        # self.set_fullscreen(True)

        
        self.version = "1.0.0"
        self.spriteCoordinatesValue = 100

        # Map generation
        self.ProcessQueue = mp.Queue()
        self.generationSeed = 0   # 1110 - 15 - 144 - 38230
        self.chunkSize = 32
        self.renderDistance = 7

        if self.generationSeed == 0 or self.generationSeed is None :
            self.generationSeed = random.randint(1,100_000)
            print("seed :" , self.generationSeed)

        self.generationQueue = []
        self.maxParallelProcess = mp.cpu_count() # 12
        self.Mapdata = {}
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

        self.Chunkscene = arcade.Scene()
        self.Chunkscene.add_sprite_list("Ground")    # on dessinera chaques chunks avec son propre nom (self.Chunkscene.add_sprite_list("ground-77158FF2"))
                                                # cela va permètre de (self.Chunkscene.remove_sprite_list_by_name("ground-77158FF2"))
        
        
        # size = 5 # 100 pixel square
        # choice = ['textures/water.png' , 'textures/grass.png' , 'textures/stone.png' , 'textures/sand.png']
        # self.totalSprite = 12000
        # for i in range(int(self.totalSprite)) :

        #     water = Ground(dirLocation + random.choice(choice) , (( i % 120 ),( i // 120 )) , size = size )

        #     water.sprite.center_x = ( i % 120 ) * 100
        #     water.sprite.center_y = ( i // 120 ) * 100

        #     self.Chunkscene.add_sprite("Ground", water.sprite)

            
        # [[ self.Chunkscene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunk.Tiles]
        size = 0
        for i in range(size*size) :

            self.generationQueue.append(( i%size , i//size))

        self.player = Player(dirLocation + 'textures/stone.png' , (0,0) , self.chunkSize , Spritesize =  1 , spriteCoordinatesValue=self.spriteCoordinatesValue 
        , chunkRenderDistance=self.renderDistance)


        self.updateMapdata()

    # Arcade fonctions

    def on_draw(self) :
        arcade.start_render()

        self.camera.use()
        self.Chunkscene.draw()

        self.player.sprite.draw()
        # arcade.draw_text(str(self.camera.scale) , 100 , 100 , font_size=20*self.camera.scale)


        for chunk in self.Mapdata.values() :
            chunk.buildingSpritelist.draw()

        #     for buildings in chunk.buildings.values() :
        #         buildings.sprite.draw()
        


    def on_update(self , deltaTime):

        # updating the render distance while in DevMode


        # updating buildings sprites 
        # total = 0
        # t = time.perf_counter()

        for chunk in self.Mapdata.values() :
            for buildings in chunk.buildings.values() :
                buildings.updateAnimation()
                # total += 1

        # print("updating" , time.perf_counter() - t , f" with {total} sprites in total")
        


        #fps and camera update

        fps = round((1/deltaTime),0)
        # print(round((1/deltaTime),0) , "fps" , end='\r') 
        # print(self.camera.scale , end='\r')
        self.center_camera_to_player( self.player.sprite )

        # player mouvement 
        devmodemultiplier = 1
        if self.DevMode :
            devmodemultiplier = 20

        if self.keys["Z"] :
            self.player.sprite.center_y += self.player.speed * deltaTime * self.spriteCoordinatesValue * devmodemultiplier
            self.player.positionMap[1]  += self.player.speed * deltaTime * devmodemultiplier
        if self.keys["S"] : 
            self.player.sprite.center_y -= self.player.speed * deltaTime * self.spriteCoordinatesValue * devmodemultiplier
            self.player.positionMap[1]  -= self.player.speed * deltaTime * devmodemultiplier
        if self.keys["Q"] : 
            self.player.sprite.center_x -= self.player.speed * deltaTime * self.spriteCoordinatesValue * devmodemultiplier
            self.player.positionMap[0]  -= self.player.speed * deltaTime * devmodemultiplier
        if self.keys["D"]: 
            self.player.sprite.center_x += self.player.speed * deltaTime * self.spriteCoordinatesValue * devmodemultiplier
            self.player.positionMap[0]  += self.player.speed * deltaTime * devmodemultiplier


        playerChunkCoordinates = self.player.getChunkPosition()
        if self.player.positionChunk != playerChunkCoordinates :  
            self.updateMapdata()
            self.player.updateChunkPosition()
            print("player chunk Coordinates :" ,self.player.getChunkPosition())



        # map Generation process

        # dessine les chunks déja généré 
        if not self.ProcessQueue.empty():
            chunk = self.ProcessQueue.get()
            self.Mapdata[self.getConcatinatedcoordinates(chunk.position,4)] = chunk
            # print(chunk)
            self.draw_single_chunk_from_spritelist(chunk , chunk.spritelist)
        

        # met a générer les chunks de la liste
        if len(self.generationQueue) > 0 and len(mp.active_children()) < self.maxParallelProcess:
            # si il y a des chunks a générer et qu'on ne dépasse pas la quantité max de processus alors on génrère un nouveau chunk
            coordinates = self.generationQueue.pop(0) 
            dirLocation = self.getDirectoryLocation()
            txtlist = [dirLocation + self.textures[i] for i in range(len(self.textures))] 
            neigthborschunks =  [] # self.getneighborschunks(coordinates)
            generator = Generator(Game.generate_single_chunk , (Game,coordinates , self.chunkSize , txtlist , self.generationSeed, self.spriteCoordinatesValue , neigthborschunks , self.ProcessQueue))
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
        
        maxzoom = 23
        minzoom = 1
        zoomspeed = 7
        
        if scroll_y < 0 :
            self.camera.scale *= 1 + zoomspeed/100
        else :
            self.camera.scale /= 1 + zoomspeed/100
        
        if not self.DevMode :
            self.camera.scale = min(maxzoom,max(self.camera.scale,minzoom))


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        dir_location = self.getDirectoryLocation()
        
        position = self.getTileCoordinatesFromScreen(x,y)
        chunkpos = position[0] // self.chunkSize , position[1] // self.chunkSize
        posinchunk = position[0] % self.chunkSize , position[1] % self.chunkSize
        Concatinatedpositions = self.getConcatinatedcoordinates(posinchunk,2)

        try :  chunk = self.Mapdata[self.getConcatinatedcoordinates(chunkpos,4)]  # on regarde lsi le chunk est généré ou non. si il l'est , on récupère ses données
        except KeyError : 
            chunk = None
            print(f"the {chunkpos} chunk isn't generated yet !")


        if chunk is not None :
            if Concatinatedpositions not in chunk.buildings :
                chunk.buildings[Concatinatedpositions] = Buildings(position , dir_location + 'textures/Conveyorbelt' , 0.1 , self.spriteCoordinatesValue , self.chunkSize , direction="down") 
                chunk.buildingSpritelist.append(chunk.buildings[Concatinatedpositions].sprite)

        # if self.Mapdata : # si la liste n'est pas vide
        #     self.Chunkscene.add_sprite_list_before("Ground" , "Map-" + str(self.Mapdata[-1].position))
       
        

    # Local fonctions

    def getConcatinatedcoordinates(self, coordinates , base):
        coordinatesLength = base
        hexaX = hex(coordinates[0])[2:]
        hexaY = hex(coordinates[1])[2:]
        return str(("0" * (coordinatesLength - len(hexaX))) + hexaX) + ',' + str(("0" * (coordinatesLength - len(hexaY))) + hexaY) 


    def getCoordinatesFromConcatination(self , concatinated):
        comma = len(concatinated)//2
        x , y = concatinated[:comma] , concatinated[comma+1:]
        return int(x,16) + int(y,16)


    # Terrain generation 


    def updateMapdata(self): 

        # read the Mapdata and store all the generated chunk coordinates

        alreadyGeneratedChunks = [] # contient les chunks et leur index dans la liste 
        for chunk in self.Mapdata.values() :
            alreadyGeneratedChunks.append(chunk)

        # kill all out of range chunks
            # return the x and y distance beetween the position of the chunk and the position of the player
        distance = lambda playerPosition, chunkcoordinates : (abs(chunkcoordinates[0] - playerPosition[0]) , abs(chunkcoordinates[1] - playerPosition[1]) )
        
        # reverse the list so that we can properly delete the chunk from the Mapdata
        alreadyGeneratedChunks.reverse()
        if not self.DevMode :
            for Gchunk in alreadyGeneratedChunks:
                # check if the chunk is to far or not
                dx , dy = distance(self.player.positionChunk , Gchunk.position) 
                if dx > self.player.chunkRenderDistance or dy > self.player.chunkRenderDistance :
                    # if it is, we delete it and remove it from the drawing screen
                    del self.Mapdata[self.getConcatinatedcoordinates(Gchunk.position,4)]
                    try :
                        self.Chunkscene.remove_sprite_list_by_name("Map-" + str(Gchunk.position))
                    except :
                        print(f"le chunk n°{Gchunk.position} n'a pas pu être décharger")



        alreadyGeneratedChunksCoordinates = [ i.position for i in self.Mapdata.values()]

        # add to the generation list, all the chunks that need to be generated
        x , y = self.player.getChunkPosition()
        # print(type(self.renderDistance +x) , type(self.renderDistance +y))
        for yChunk in range(int(y - self.renderDistance) , int(y + self.renderDistance + 1)) :
            for xChunk in range(int(x - self.renderDistance) , int(x + self.renderDistance + 1)) :

                if (xChunk,yChunk) not in alreadyGeneratedChunksCoordinates and (xChunk,yChunk) not in self.generationQueue:
                    self.generationQueue.append((xChunk,yChunk))
        

        
    def generate_single_chunk(self, Chunkposition , size , TextureList , seed , spriteCoordinatesValue , neigthborschunks , connector ):
        # generate a single chunk based on all the parameters

        chunk = Chunk( TextureList , seed = seed , chunk_size=size   , position = Chunkposition , neigthborschunks=neigthborschunks)
        chunk.generate(spriteCoordinatesValue)
        chunk.updateSpritelist()

        connector.put(chunk)



    def draw_single_chunk_from_rawdata(self, chunkdata) :
        # draw a chunk using it's data

        # [[ self.Chunkscene.add_sprite("Ground", tile.sprite) for tile in row] for row in chunkdata.Tiles]
        # print(f'it took {time.perf_counter() - t} seconds to draw this chunk')

        t = time.perf_counter()

        chunkName = chunkdata.getPositions()
        chunkName = "Map-" + str(chunkName)
        for row in chunkdata.Tiles :
            for tile in row :
                self.Chunkscene.add_sprite(chunkName, tile.sprite)
                if tile.oretype is not None :
                    self.Chunkscene.add_sprite(chunkName, tile.oresprite)

    

    def draw_single_chunk_from_spritelist(self, chunkdata , spritelist):


        chunkName = chunkdata.getPositions()
        chunkName = "Map-" + str(chunkName)
        self.Chunkscene.add_sprite_list(chunkName , sprite_list = spritelist) 



    def getneighborschunks(self, coordinates) : 
        neighbors = []
        neighbors.append(self.Mapdata[self.getConcatinatedcoordinates((coordinates[0]+1 , coordinates[1]  ),4)])
        neighbors.append(self.Mapdata[self.getConcatinatedcoordinates((coordinates[0]   , coordinates[1]-1),4)])
        neighbors.append(self.Mapdata[self.getConcatinatedcoordinates((coordinates[0]-1 , coordinates[1]  ),4)])
        neighbors.append(self.Mapdata[self.getConcatinatedcoordinates((coordinates[0]   , coordinates[1]+1),4)])
        return neighbors


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



    def getTileCoordinatesFromScreen(self , mouse_x , mouse_y) :

        screenZero = self.camera.position   # the Physical adaptation of the screen 0,0 
        # centertileX = (screenZero[0] + self.width/2) / self.spriteCoordinatesValue  # tile cordinates of the center of the screen
        # centertileY = (screenZero[1] + self.width/2) / self.spriteCoordinatesValue
        # lefttileX  = centertileX - (self.width/2) / self.spriteCoordinatesValue * self.camera.scale # tile coordinates of the screen 0,0 (bottom left)
        # lefttileY  = centertileY - (self.height/2) / self.spriteCoordinatesValue * self.camera.scale
        
        zerotileX = (screenZero[0] + self.width  /2 * (1-self.camera.scale))/self.spriteCoordinatesValue  # tile coordinates of the screen 0,0 (bottom left)
        zerotileY = (screenZero[1] + self.height /2 * (1-self.camera.scale))/self.spriteCoordinatesValue
        onetileX  = (screenZero[0] + self.width  /2 * (1+self.camera.scale))/self.spriteCoordinatesValue  # tile cordinates of the top right
        onetileY  = (screenZero[1] + self.height /2 * (1+self.camera.scale))/self.spriteCoordinatesValue

        mousetileX = arcade.lerp( zerotileX , onetileX , mouse_x/self.width) # get the linear interpolation of thoses values
        mousetileY = arcade.lerp( zerotileY , onetileY , mouse_y/self.height)

        return math.floor(mousetileX+0.5) , math.floor(mousetileY+0.5)  # return the actual tile coordinates the player was clicking




if __name__ == '__main__' : 

    game = Game((1280,920),"jeu")
    game.run()

    # clear every existing process

    childprocess = mp.active_children()
    for process in childprocess :
        process.terminate()

