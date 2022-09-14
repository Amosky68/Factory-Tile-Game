import arcade


class Sprite() :

    def __init__ (self , x , y , screen_x = 0 , screen_y = 0 , texture = "") :


        self.x = x
        self.y = y
        self.center_x = screen_x 
        self.center_y = screen_y
        self.texture = texture

        self.sprite = arcade.Sprite( center_x=self.x, center_y=self.y , texture=self.texture , hit_box_algorithm = "None" , scale = 0.05)