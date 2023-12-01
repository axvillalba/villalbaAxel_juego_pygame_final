import pygame
from auxiliar.auxiliar import SurfaceManager as sf
from auxiliar.constantes import *
from models.Bullet import *
from models.barra_vida import Barra_vida


class Player(pygame.sprite.Sprite):
    
    def __init__(self, coord_x, coord_y, constraint, frame_rate, speed, jump, gravity, stage_dict_configs: dict):
        super().__init__()
        
        #Cargar del json el diccionario del player
        self.__player_configs = stage_dict_configs.get('player')
        # Mostrar sprite del jugador / Solo la figura estatica / probar con eso, despues le damos movimiento a la imagen.
        
        
        # self.image = pygame.image.load(self.__player_configs['player_stand']).convert_alpha()
        # #En este caso lo que hago es darle el rectangulo al sprite de la linea anterior. ahora self.rect tendrá los metodos de rectangulos. 
        #self.__rect = self.image.get_rect(midbottom=(coord_x, coord_y))
        
        
        self.__iddle_r = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/stand.png',4,1)
        self.__iddle_l = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/stand.png',4,1, flip=True)        
        self.__walk_r = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/walk.png', 3,1)
        self.__walk_l = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/walk.png', 3,1, flip=True)
        # self.__attack_melee_r = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/attack_melee.png',7,1)
        # self.__attack_melee_l = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/attack_melee.png',7,1, flip=True)
        self.__attack_laser_r = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/attack_3.png',4,1)
        self.__attack_laser_l = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/attack_3.png',4,1, flip = True)
        self.__jump_r = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/player_jump.png',8,1)
        self.__jump_l = sf.get_surface_from_spritesheet('./assets/graphics/player_allen/player_jump.png',8,1, flip = True)
        #self.__fall_r = sf.get_surface_from_spritesheet('./assets/graphics/fall.png', 4,1)
        
        #self.__image_shot = sf.get_surface_from_spritesheet('./assets\graphics\player_allen\power_attack.png',8,1)
        #self.__rect_disparo = self.__rect
        
        self.__player_animation_time = 0
        self.__actual_frame_index = 0
        self.__frame_rate = frame_rate
        self.__actual_animation = self.__iddle_r
        self.__actual_img_animation = self.__actual_animation[self.__actual_frame_index]
        self.__rect = self.__actual_img_animation.get_rect(midbottom=(coord_x, coord_y))
        self.rect_ground_collition_floor = pygame.Rect(self.__rect.x, self.__rect.y + self.__rect.h - altura_rect, self.__rect.w, altura_rect)
        self.rect_ground_collition_top = pygame.Rect(self.__rect.x, self.__rect.y, self.__rect.w, altura_rect)
        
        # Atributos de movimiento / speed=movimientos de pixeles que se mueve el personaje (recibe el valor por parametro) / constrait = restriccion de mov en el eje x
        self.__speed = speed 
        self.max_x_constraint = constraint
        self.__jump = jump
        self.gravity = gravity


        # #Vida
        self.vida = self.__player_configs['life_points']
        # self.barra_vida = Barra_vida(self.vida, 200,10)
        # self.barra_vida.rect.x = self.__rect.x
        # self.barra_vida.rect.y = self.__rect.y


        #tiempo
        self.__update_time = pygame.time.get_ticks()
        
        #Booleanos de movimientos
        self.__is_jumping = False
        self.__is_looking_right = True
        #self.__is_fallen = False
        
        #coordenadas
        self.coord_x = coord_x
        self.coord_y = coord_y
        
        # # Atributos para disparar y recargar
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        self.bullet_group = pygame.sprite.Group()
        self.puntaje = 0
        self.is_shooting = False
        
    # Comienzo a crear todas los metodos correspondientes a Player
    
    #Metodos para la animacion
    
    def __set_x_animations_preset(self,animation_list: list[pygame.surface.Surface], look_r: bool):
        self.__actual_animation = animation_list
        self.__is_looking_right = look_r

    def get_actividad(self):
        #Esta funcion va a determinar los movimientos del Player 
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:  # movimiento sobre eje x
            self.agregar_x(self.__speed)
            self.__is_looking_right = True
            self.__set_x_animations_preset(self.__walk_r, self.__is_looking_right)
        elif keys[pygame.K_LEFT]:
            self.agregar_x(-self.__speed)
            self.__is_looking_right = False
            self.__set_x_animations_preset(self.__walk_l, self.__is_looking_right)
        # elif keys [pygame.K_DOWN]: #Solo va a quedar ahora para probar movimientos
        #     self.agregar_y(5)
        elif keys[pygame.K_SPACE] and not self.__is_jumping:
            self.saltar()
            #self.stay()   
        elif keys [pygame.K_j] and not self.is_shooting:
            if self.__is_looking_right == True:
                self.__set_x_animations_preset(self.__attack_laser_r,self.__is_looking_right)
                self.disparar()
            elif self.__is_looking_right == False:                
                self.__set_x_animations_preset(self.__attack_laser_l, self.__is_looking_right)
                self.disparar()
        else:
            self.stay()
            

    @property
    def get_bullets(self) -> list[Bullet]:
        return self.bullet_group
        
    def disparar(self):
        
        if self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            
    def create_bullet(self):
        if self.__is_looking_right == True:
            direccion = 'right'
        else:
            direccion = 'left'
        return Bullet(self.__rect.x, self.__rect.y, direccion, True)

    def shoot_laser(self):  # disparar laser
        self.bullet_group.add(self.create_bullet())
    
    def recharge (self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def saltar(self):
        
        if self.__is_looking_right == True:
            self.__actual_animation = self.__jump_r 
            self.agregar_y(-self.__jump)
            self.agregar_y(self.gravity)                    
            self.agregar_x(self.__speed-3)       
        else:
            self.__actual_animation = self.__jump_l
            self.agregar_y(-self.__jump)
            self.agregar_y(self.gravity)                    
            self.agregar_x(-self.__speed+3)

        
    def stay(self):
        if self.__is_looking_right == True:
            self.__actual_animation = self.__iddle_r
        else:
            self.__actual_animation = self.__iddle_l
        self.__actual_frame_index = 0


    def constraint(self):  # Ajusta al jugador a los limites de la pantalla
        if self.__rect.left<= 12:
            self.__rect.left = 12
            self.rect_ground_collition_floor.left = 12
            self.rect_ground_collition_top.left = 12
        if self.__rect.right >= self.max_x_constraint:
            self.__rect.right = self.max_x_constraint
            self.rect_ground_collition_floor.right = self.max_x_constraint
            self.rect_ground_collition_top.right = self.max_x_constraint
        if self.__rect.top <= 100:
            self.__rect.top = 100
            self.rect_ground_collition_floor.top
            self.rect_ground_collition_top.top= 100
        if self.__rect.bottom >= 555:
            self.__rect.bottom = 555
            self.rect_ground_collition_floor.bottom = 555
            self.rect_ground_collition_top.bottom = 555
            
    def do_animation(self, delta_ms,lista_plataformas):
        # deberia de agregarle un current time para evitar el exceso de superar limite de lista
        self.__player_animation_time += delta_ms

        # current_time = pygame.time.get_ticks()
        # if current_time - self.__update_time > self.__frame_rate:
        #     self.__update_time = current_time
        #     self.__actual_frame_index +=1



        if self.__player_animation_time >= self.__frame_rate:
            self.__player_animation_time = 0
            if self.__actual_frame_index < len(self.__actual_animation) - 1:
                self.__actual_frame_index += 1
            else:
                self.__actual_frame_index = 0
                # if self.__is_jumping:     no entiendo bien esta parte del codigo
                #     self.__is_jumping = False
                #     self.__rect.y = 0
                    
            if self.toca_plataforma(lista_plataformas) == False:
                    self.agregar_y(self.gravity+10)        
            # elif self.__is_jumping:     #no entiendo esta parte del codigo
            #     self.__is_jumping = False
                
                
    def toca_plataforma(self, list_plataformas : list):
        retorno = False
        if self.__rect.y >= 500:
            retorno = True
        else:
            for plataforma in list_plataformas:
                if self.rect_ground_collition_floor.colliderect(plataforma.rect_ground_collition_top):
                    retorno = True
                elif self.rect_ground_collition_top.colliderect(plataforma.rect_ground_collition_bottom):
                    retorno = False
        return retorno
    

    def agregar_x(self,movimiento_x):
        self.__rect.x += movimiento_x
        self.rect_ground_collition_floor.x += movimiento_x
        self.rect_ground_collition_top.x += movimiento_x
    def agregar_y(self,movimiento_y):
        self.__rect.y += movimiento_y 
        self.rect_ground_collition_floor.y += movimiento_y
        self.rect_ground_collition_top.y += movimiento_y


    def update(self, screen: pygame.surface.Surface, delta_ms, lista_plataformas):
        
        self.do_animation(delta_ms, lista_plataformas)    
        self.get_actividad()
        self.constraint()
        self.recharge()
        self.bullet_group.draw(screen)
        self.bullet_group.update(screen)

    def draw(self, screen: pygame.surface.Surface):
        
        if (DEBUG):
            pygame.draw.rect(screen,ROJO,self.__rect)
            pygame.draw.rect(screen,VERDE,self.rect_ground_collition_floor)
            pygame.draw.rect(screen,VERDE,self.rect_ground_collition_top)
        
            
        self.__actual_img_animation = self.__actual_animation[self.__actual_frame_index]
        screen.blit(self.__actual_img_animation, self.__rect)
        
