from __future__ import division
from operator import itemgetter
from math import log10
from random import randint, uniform, shuffle
import pygame as pg


def make_color(color):
    try:
        return pg.Color(color)
    except ValueError:
        return pg.Color(*color)

def make_filled_surface(rect, color):
    surf = pg.Surface(rect.size)
    surf.fill(color)
    if color.a != 255:
        surf.set_alpha(color.a)
        return surf.convert_alpha()
    else:
        return surf.convert()


class DataPoint(object):
    def __init__(self, x_value, y_value, color,  text="", radius=2):
        self.color = make_color(color)
        self.x_val = x_value
        self.y_val = y_value
        self.graph_x = self.x_val
        self.graph_y = self.y_val
        self.dot = pg.Surface((radius*2, radius*2))
        self.dot_rect = self.dot.get_rect()
        self.radius = radius
        pg.draw.circle(self.dot, self.color, self.dot_rect.center,  radius)
        self.dot.set_alpha(self.color.a)
        self.hovered = False
        self.text = ""

    def scale(self, x_zero, y_zero, x_scale, y_scale):
        self.graph_x =  x_zero + (self.x_val * x_scale)
        self.graph_y = y_zero - (self.y_val * y_scale)
        try:
            self.dot_rect.center = (self.graph_x, self.graph_y)
        except:
            print "scale fail: ", self.graph_x, self.graph_y
    def update(self, graph_mouse_pos):
        self.hovered = False
        if self.dot_rect.collidepoint(graph_mouse_pos):
            self.hovered = True

    def draw(self, surface):
        surface.blit(self.dot, self.dot_rect)
        

class DataLine(object):
    """
    A line on a graph.

    data_points: a sequence of DataPoint objects or (x, y) tuples
    color: colorname string, RGB or RGBA tuple, not needed if passing DataPoints
    """
    def __init__(self, data_points, color=None, text="", point_radius=2):
        if isinstance(data_points[0], DataPoint):
            self.data_points = data_points
        else:
            self.data_points = [DataPoint(point[0], point[1], color, text, point_radius)
                                       for point in data_points]
        self.color = self.data_points[0].color
        self.calc_lows_highs()
        self.text=text
        self.active = True
        
    def calc_lows_highs(self):
        x_vals = [x.x_val for x in self.data_points]
        y_vals = [x.y_val for x in self.data_points]
        self.max_x_val = max(x_vals)
        self.min_x_val = min(x_vals)
        self.max_y_val = max(y_vals)
        self.min_y_val = min(y_vals)

    def calc_graph_points(self, x_scale, y_scale, x_zero, y_zero):
        graph_points = [(p.graph_x, p.graph_y) for p in self.data_points]
        self.graph_points = sorted(graph_points, key=itemgetter(0))

    def scale_points(self, x_zero, y_zero, x_scale, y_scale):
        for point in self.data_points:
            point.scale(x_zero, y_zero, x_scale, y_scale)
    
    def update(self, graph_mouse_pos):
        for point in self.data_points:
                point.update(graph_mouse_pos)
                
    def draw(self, surface):
        if self.active:
            pg.draw.lines(surface, self.color, self.graph_points)


class GraduationLine(object):
    def __init__(self, points, value, line_color, font, text_color, line_weight=1):
        left, right = points
        self.value = value
        self.label = font.render("{}".format(value), True, text_color)
        self.label_rect = self.label.get_rect(topright=left)
        self.line_color = line_color

        if left[0] == right[0]:
            width = line_weight
            height = left[1] - right[1]
            tl = right
        else:
            width = right[0] - left[0]
            height = line_weight
            tl = left
        self.rect = pg.Rect(tl, (width, height))
        self.surface = make_filled_surface(self.rect, self.line_color)
               
    def draw(self, surface):
        surface.blit(self.surface, self.rect)  
        surface.blit(self.label, self.label_rect)
        
        
class LineToggler(object):
    def __init__(self, topleft, tickbox_size, font, line, tickbox_color):
        self.line = line
        self.tickbox = pg.Rect(topleft, tickbox_size)
        self.color = line.color
        self.tickbox_color = tickbox_color
        self.label = font.render(self.line.text, True, self.color)
        self.label_rect = self.label.get_rect(midleft=(self.tickbox.right + 5, self.tickbox.centery))        
        self.hovered = False
        
    def update(self, graph_mouse_pos):
        self.hovered = False
        if self.tickbox.collidepoint(graph_mouse_pos):
            self.hovered = True        
    
    def get_event(self, event):     
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.hovered:
                self.toggle()
                return True
    
    def toggle(self, boolean=None):
        if boolean is not None:
            self.line.active = boolean
        else:
            self.line.active = not self.line.active
            
    def draw(self, surface):
        if self.line.active:
            pg.draw.line(surface, self.color, self.tickbox.topleft, (self.tickbox.right, self.tickbox.bottom - 1))
            pg.draw.line(surface, self.color, self.tickbox.topright, self.tickbox.bottomleft)
        pg.draw.rect(surface, self.tickbox_color, self.tickbox, 3)
        surface.blit(self.label, self.label_rect)
    

class _Graph(object):
    def __init__(self, topleft, size, style_dict):
        s = style_dict     
        self.bg_color = make_color(s["bg_color"])
        self.graduation_lines_color = make_color(s["graduation_lines_color"])
        self.frame_color = make_color(s["frame_color"])              
        self.hover_label_text_color = make_color(s["hover_label_text_color"])
        if s["hover_label_bg_color"]:
            self.hover_label_bg_color = make_color(s["hover_label_bg_color"])
        else:
            self.hover_label_bg_color = None
        self.title_text_color = make_color(s["title_text_color"])    
        self.graduation_text_color = make_color(s["graduation_text_color"])
        self.alpha = s["alpha"]
        
        self.frame = pg.Rect(topleft, size)
        self.surface = pg.Surface(size).convert()
        w, h = size
        left_size = int(w * s["left_margin"])
        b_size = int(h * s["bottom_margin"])
        top_height = int(h * s["top_margin"])        
        self.left_rect = pg.Rect((0, 0), (left_size, h - b_size))
        self.bottom_rect = pg.Rect(0, self.left_rect.bottom,
                                              w, b_size)
        self.title_rect = pg.Rect(self.left_rect.right, 0, w - left_size, top_height) 
        self.rect = pg.Rect(self.left_rect.right, self.title_rect.bottom, w - left_size, h - (b_size + top_height))
        self.top_frame = make_filled_surface(self.title_rect, self.frame_color)
        self.left_frame = make_filled_surface(self.left_rect, self.frame_color)
        self.bottom_frame = make_filled_surface(self.bottom_rect, self.frame_color)
        self.frame_rects = [self.left_rect, self.bottom_rect]
        self.background = make_filled_surface(self.rect, self.bg_color)        

        self.typeface = s["font"]
        self.hover_label_font = pg.font.Font(self.typeface, s["hover_label_text_size"])
        self.graduation_font = pg.font.Font(self.typeface, s["graduation_text_size"])
        self.title_font = pg.font.Font(self.typeface, s["title_text_size"])
        self.vert_title_font = pg.font.Font(self.typeface, s["vert_title_text_size"])
        self.bottom_title_font = pg.font.Font(self.typeface, s["bottom_title_text_size"])
        self.title = self.make_graph_title(s["title_text"], self.title_rect)
        self.vert_title = self.make_vert_title(s["vert_title_text"],
                                                           (int(self.left_rect.width * .1), int(self.frame.height * .2)),
                                                            make_color(s["vert_title_text_color"]))   
        self.hover_label = None
        self.moveable= s["moveable"]
        self.grabbed = False
        self.hovered = False

    def get_yscale_yzero(self, min_y, max_y, y_graduation_size, rect):
        total = max_y - min_y
        scale = rect.height / total
        zero = rect.bottom + (min_y * scale)
        return scale, zero
        
    def get_xscale_xzero(self, min_x, max_x, x_graduation_size, rect):
        total = max_x - min_x
        scale = rect.width / total
        zero = rect.left - (min_x * scale)
        return scale, zero
        
    def get_graduation_range(self, low, high, padded=True):
        if high <= 0:
            high = 1
        power = int(log10(high))
        max_ = (10**power)
        for i in range(1, 10):
            if high > (10**power) * i:
                max_ = (10**power) * (i + 1)
        if low >= 0:
            min_ = 0
            power_ = 0
        else:
            power_ = int(log10(abs(low)))
            min_ = 10**power_ * -1
            for x in range(0, -10, -1):
                if low < 10**power_ * x:
                    min_ = 10**power_ * (x - 1)
        graduation_size = 10**max(power, power_)
        if not padded:
            max_ = int(high)
        return min_, max_, graduation_size
        
    def make_vert_title(self, text, midtop, color):
        centerx, top = midtop
        vert_title = []
        for char in list(text):
            label = self.vert_title_font.render(char, True, color)
            rect = label.get_rect(midtop=(centerx, top))
            vert_title.append((label, rect))
            top = rect.bottom
        return vert_title
    
    def make_graph_title(self, text, title_rect):
        center = title_rect.center
        title = self.title_font.render(text, True, self.title_text_color)
        title_rect = title.get_rect(center=center)
        return (title, title_rect)
        
    def draw_frame(self):
        self.surface.blit(self.left_frame, self.left_rect)
        self.surface.blit(self.bottom_frame, self.bottom_rect)
        self.surface.blit(self.top_frame, self.title_rect)
        for v in self.vert_title:
            self.surface.blit(v[0], v[1])
        self.surface.blit(self.title[0], self.title[1])
            
 
class LineGraph(_Graph):
    def __init__(self, topleft, size, data_lines, style_dict):
        super(LineGraph, self).__init__(topleft, size, style_dict)                        
        s = style_dict
        self.data_lines = data_lines
        self.show_points = s["show_points"]
        self.show_lines = s["show_lines"]    
        self.toggler_font = pg.font.Font(self.typeface, s["toggler_text_size"])
        
        self.togglers = self.make_togglers(s["tickbox_size"], s["toggler_width"], 
                                                         s["togglers_top_margin"],
                                                         s["togglers_bottom_margin"])
        self.make_graph()
        
    def make_graph(self):    
        active_lines = [x for x in self.data_lines if x.active]
        if not active_lines:
            return
        low_x, high_x, low_y, high_y = self.get_highs_lows(active_lines)
        min_x, max_x, x_grad_size = self.get_graduation_range(low_x, high_x, padded=False)
        min_y, max_y, y_grad_size = self.get_graduation_range(low_y, high_y)
        x_scale, x_zero = self.get_xscale_xzero(min_x, max_x, x_grad_size, self.rect)
        y_scale, y_zero = self.get_yscale_yzero(min_y, max_y, y_grad_size, self.rect)
        self.make_y_graduation_lines(min_y, max_y, y_zero, y_scale, y_grad_size, self.rect)
        self.make_x_graduation_lines(min_x, max_x, x_zero, x_scale, x_grad_size, self.rect)
        for line in self.data_lines:
            line.scale_points(x_zero, y_zero, x_scale, y_scale)
            line.calc_graph_points(x_zero, y_zero, x_scale, y_scale)
        
        
    def make_togglers(self, tickbox_size, toggler_width, top_margin, bottom_margin):
        total = len(self.data_lines)
        w, h = tickbox_size
        avail_h = int(self.bottom_rect.h * (1 - (top_margin + bottom_margin)))
        num_rows = avail_h // h
        row_space = avail_h // min(num_rows, len(self.data_lines))
        toggle = 0
        left = self.rect.left
        top = self.bottom_rect.top + int(self.bottom_rect.h * top_margin)
        togglers = []
        for line in self.data_lines:
            toggler = LineToggler((left, top), tickbox_size, self.toggler_font, line, self.graduation_text_color)
            togglers.append(toggler)
            top += row_space
            toggle += 1
            if not toggle % num_rows:
                left += toggler_width
                top = self.bottom_rect.top + int(self.bottom_rect.h * top_margin)
        return togglers            
        
    def get_highs_lows(self, data_lines):
        max_x = max([line.max_x_val for line in data_lines])
        min_x = min([line.min_x_val for line in data_lines])
        max_y = max([line.max_y_val for line in data_lines])
        min_y = min([line.min_y_val for line in data_lines])
        return min_x, max_x, min_y, max_y 
        
    def make_y_graduation_lines(self, min_y, max_y, y_zero, y_scale, y_graduation_size, rect):
        size = max(1, y_graduation_size // 2)
        self.y_graduation_lines = []
        for y in range(min_y, max_y, size):
            spots = [(rect.left, y_zero - (y * y_scale)),
                         (rect.right, y_zero - (y * y_scale))]
            line = GraduationLine(spots, y, self.graduation_lines_color,
                                           self.graduation_font,
                                           self.graduation_text_color) 
            self.y_graduation_lines.append(line)
            
    def make_x_graduation_lines(self, min_x, max_x, x_zero, x_scale, x_graduation_size, rect):
        size = max(1, x_graduation_size // 2)
        self.x_graduation_lines = []
        bottom = self.rect.bottom
        for x in range(min_x, max_x + 1, size):
            spots = [(x_zero + (x * x_scale), bottom),
                         (x_zero + (x * x_scale), self.title_rect.bottom)]
            line = GraduationLine(spots, x, self.graduation_lines_color,
                                           self.graduation_font,
                                           self.graduation_text_color) 
            self.x_graduation_lines.append(line)

    def update(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        x, y = mouse_x - self.frame.left, mouse_y - self.frame.top
        self.hover_label = None
        self.hover_rect = None
        for line in [d_line for d_line in self.data_lines if d_line.active]:
            line.update((x, y))
            for point in line.data_points:
                if point.hovered:
                    self.hover_label = self.hover_label_font.render(
                                "{:.2f}".format(point.y_val), True, point.color) #self.hover_label_text_color)
                    centerx = point.dot_rect.centerx # + self.frame.left
                    bottom = point.dot_rect.top #+ self.frame.top                    
                    self.hover_rect = self.hover_label.get_rect(bottomright=(centerx, bottom))
        self.hovered = False
        if self.moveable:
            if self.frame.collidepoint((mouse_x, mouse_y)):
                self.hovered = True
        if self.grabbed:
            self.frame.topleft = (mouse_x - self.grab_point[0],
                                mouse_y - self.grab_point[1])
        for t in self.togglers:
            t.update((x, y))
  
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.moveable and self.hovered:
                mouse_x, mouse_y = event.pos 
                x, y = mouse_x - self.frame.left, mouse_y - self.frame.top
                self.grabbed = True
                self.grab_point = (x, y)
        
        elif event.type == pg.MOUSEBUTTONUP:
            self.grabbed = False
        rescale = False
        for t in self.togglers:
            if t.get_event(event):
                rescale = True
        if rescale:
            self.make_graph()
            
    def draw(self, surface):
        if self.moveable:
            self.frame.clamp_ip(surface.get_rect())
        self.surface.blit(self.background, self.rect)
        self.draw_frame()
        for g_line in self.y_graduation_lines:
            g_line.draw(self.surface)        
        for x_line in self.x_graduation_lines:
            x_line.draw(self.surface)
        for line in self.data_lines:
            if self.show_lines and line.active:
                pg.draw.aalines(self.surface, line.color, False, line.graph_points)
            if self.show_points and line.active:
                for point in line.data_points:
                    point.draw(self.surface)
        if self.hover_label:
            self.hover_rect.clamp_ip(self.rect)
            self.surface.blit(self.hover_label, self.hover_rect)
        for t in self.togglers:
            t.draw(self.surface)
        self.surface.set_alpha(self.alpha)
        surface.blit(self.surface, self.frame)
