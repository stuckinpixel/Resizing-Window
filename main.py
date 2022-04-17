
import pygame, sys, time, random, json, math
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 1000, 600
surface=pygame.display.set_mode((WIDTH, HEIGHT),0,32)
fps=64
ft=pygame.time.Clock()
pygame.display.set_caption('Resize Window')


"""

CREDITS:

downloaded the image from the below page
https://gmunk.com/Windows-10-Desktop

"""

background = pygame.image.load("Windows.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


class Window:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.width = 600
        self.height = 400
        self.menu_bar_height = 20
        self.resize_hotspot_cover = 10
        self.cornor_grabbed = None
        self.edge_and_mouse_offset = None
        self.min_width = 200
        self.min_height = 100
    def adjust_cornors(self, mouse):
        if self.cornor_grabbed is not None:
            if self.cornor_grabbed==(1, 1):
                self.width = max(self.min_width, mouse[0]-(self.x+self.edge_and_mouse_offset[0]))
                self.height = max(self.min_height, mouse[1]-(self.y+self.edge_and_mouse_offset[1]))
            elif self.cornor_grabbed==(0, 1):
                self.height = max(self.min_height, mouse[1]-(self.y+self.edge_and_mouse_offset[1]))
                diff_x = self.x-(mouse[0]+self.edge_and_mouse_offset[0])
                new_width = self.width+diff_x
                if new_width>=self.min_width:
                    self.width = new_width
                    self.x = mouse[0]+self.edge_and_mouse_offset[0]
            elif self.cornor_grabbed==(1, 0):
                self.width = max(self.min_width, mouse[0]-(self.x+self.edge_and_mouse_offset[0]))
                diff_y = self.y-(mouse[1]+self.edge_and_mouse_offset[1])
                new_height = self.height+diff_y
                if new_height>=self.min_height:
                    self.height = new_height
                    self.y = mouse[1]+self.edge_and_mouse_offset[1]
            elif self.cornor_grabbed==(0, 0):
                diff_x = self.x-(mouse[0]+self.edge_and_mouse_offset[0])
                new_width = self.width+diff_x
                if new_width>=self.min_width:
                    self.width = new_width
                    self.x = mouse[0]+self.edge_and_mouse_offset[0]
                diff_y = self.y-(mouse[1]+self.edge_and_mouse_offset[1])
                new_height = self.height+diff_y
                if new_height>=self.min_height:
                    self.height = new_height
                    self.y = mouse[1]+self.edge_and_mouse_offset[1]


class App:
    def __init__(self, surface):
        self.surface = surface
        self.play = True
        self.mouse=pygame.mouse.get_pos()
        self.click=pygame.mouse.get_pressed()
        self.color = {
            "background": (80, 141, 180),
            "alpha": (20, 180, 210),
            "window_background": (250, 250, 250),
            "menu_bar": (100, 100, 100),
            "close": (200, 0, 0),
            "resize": (0, 200, 0),
            "minimize": (0, 0, 200)
        }
        self.window = Window()
        self.dragging_enabled = False
    def draw_window(self):
        # drawing full window with white background
        pygame.draw.rect(self.surface, self.color["window_background"], (self.window.x, self.window.y, self.window.width, self.window.height))
        # drawing menu bar
        pygame.draw.rect(self.surface, self.color["menu_bar"], (self.window.x, self.window.y, self.window.width, self.window.menu_bar_height))
        menu_bar_button_size = self.window.menu_bar_height
        y = self.window.y + (menu_bar_button_size//2)
        button_gap = 2
        # drawing close button
        x = self.window.x + self.window.width - (menu_bar_button_size*1)+(menu_bar_button_size//2)
        pygame.draw.circle(self.surface, self.color["close"], (x, y), (menu_bar_button_size//2)-button_gap)
        # drawing resize button
        x = self.window.x + self.window.width - (menu_bar_button_size*2)+(menu_bar_button_size//2)
        pygame.draw.circle(self.surface, self.color["resize"], (x, y), (menu_bar_button_size//2)-button_gap)
        # drawing minimize button
        x = self.window.x + self.window.width - (menu_bar_button_size*3)+(menu_bar_button_size//2)
        pygame.draw.circle(self.surface, self.color["minimize"], (x, y), (menu_bar_button_size//2)-button_gap)
    def render(self):
        self.draw_window()
    def distance_between_two_points(self, x1, y1, x2, y2):
        return math.sqrt(((x1-x2)**2)+((y1-y2)**2))
    def check_whether_resizable_can_be_activated(self):
        mx, my = self.mouse
        if not (((self.window.x)<=mx<=(self.window.x+self.window.width)) and ((self.window.y)<=my<=(self.window.y+self.window.height))):
            # left top cornor
            if self.distance_between_two_points(self.window.x, self.window.y, mx, my)<=self.window.resize_hotspot_cover:
                edge_and_mouse_offset = (mx-self.window.x, my-self.window.y)
                return (0, 0), edge_and_mouse_offset
            # right top cornor
            if self.distance_between_two_points(self.window.x+self.window.width, self.window.y, mx, my)<=self.window.resize_hotspot_cover:
                edge_and_mouse_offset = (mx-(self.window.x+self.window.width), my-self.window.y)
                return (1, 0), edge_and_mouse_offset
            # left bottom cornor
            if self.distance_between_two_points(self.window.x, self.window.y+self.window.height, mx, my)<=self.window.resize_hotspot_cover:
                edge_and_mouse_offset = (mx-self.window.x, my-(self.window.y+self.window.height))
                return (0, 1), edge_and_mouse_offset
            # right bottom cornor
            if self.distance_between_two_points(self.window.x+self.window.width, self.window.y+self.window.height, mx, my)<=self.window.resize_hotspot_cover:
                edge_and_mouse_offset = (mx-(self.window.x+self.window.width), my-(self.window.y+self.window.height))
                return (1, 1), edge_and_mouse_offset
        return None, None
    def check_dragging(self):
        if self.click[0]==1:
            if not self.dragging_enabled:
                cornor, edge_and_mouse_offset = self.check_whether_resizable_can_be_activated()
                if cornor is not None:
                    self.dragging_enabled = True
                    self.window.cornor_grabbed = cornor
                    self.window.edge_and_mouse_offset = edge_and_mouse_offset
        else:
            self.dragging_enabled = False
            self.window.cornor_grabbed = None
    def action(self):
        self.check_dragging()
        self.window.adjust_cornors(self.mouse)
    def run(self):
        while self.play:
            self.surface.fill(self.color["background"])
            self.surface.blit(background, (0, 0))
            self.mouse=pygame.mouse.get_pos()
            self.click=pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==KEYDOWN:
                    if event.key==K_TAB:
                        self.play=False
            #--------------------------------------------------------------
            self.render()
            self.action()
            # -------------------------------------------------------------
            pygame.display.update()
            ft.tick(fps)



if  __name__ == "__main__":
    app = App(surface)
    app.run()


