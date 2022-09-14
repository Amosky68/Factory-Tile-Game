

class Physical_Screen():    # gere le changement de repère (physique a l'écran / écran a physique)

    """ Calcul de l'espace Physique -> Espace Ecrab 

    Xe: Coordonnées debut écran dans l'espace physique
    X : Coordonnées dans l'espace physique
    X': Coordonnées dans l'espace ecran


    Phy->Ecran : X'=(X-Xe)*Zoom
    Ecran->Phy : X=(X'/Zoom + Xe)
    """

    def __init__(self, zoom = 1) :

        
    #     self.center_x = center_x
    #     self.center_y = center_y
    #     self.zoom = zoom
    #     self.screen_width = screen_width
    #     self.screen_height = screen_height
        self.Xe = 0
        self.Ye = 0
        self.zoom = zoom



    # Calcul les coordonnées dans le repere ecran (depuis les coordonnées dans le repère physique)
    def to_screen(self , X,Y):
        return (X-self.Xe)*self.zoom, (Y-self.Ye)*self.zoom



    # Calcul les coordonnées dans le repere Physique (depuis les coordonnées dans le repère écran)
    def to_physic(self , X,Y):
        return X/self.zoom+self.Xe,Y/self.zoom+self.Ye



    # Calcul origine de l'écran connaissant les coordonnées physique du milieu et le zoom
    def calculate_orgin_from_center_phy(self , X,Y,bordure_x,bordure_y):
        self.Xe = X-bordure_x/(2*self.zoom)
        self.Ye = Y-bordure_y/(2*self.zoom)



    # def update_screen_dimensions(self, screen_width , screen_height ) :
    #     self.screen_width = screen_width
    #     self.screen_height = screen_height


    def update_zoom(self, zoom) :
        self.zoom = zoom


    # def update_center(self, center_x , center_y) :
    #     self.center_x = center_x
    #     self.center_y = center_y