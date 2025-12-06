import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import math

class Program:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto Graficación Unidad 1 y 2")
        
        self.current_tool = 'line'
        self.start_x = None
        self.start_y = None
        self.current_item = None
        self.selected_item = None
        self.pen_color = 'black'
        self.fill_color = ''
        self.polygon_points = []
        self.shapes = {}
        self.tool_buttons = {}
        
        self.is_moving = False
        self.is_resizing = False
        self.is_rotating = False
        self.resize_handle = None
        self.rotate_handle = None
        self.active_outline_color = 'blue'
        
        self.setup_ui()

    def setup_ui(self):
        tool_frame = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(tool_frame, text="Herramientas").pack(pady=5)
        tools = [
            ('Lápiz', 'pencil'), ('Línea', 'line'), ('Rectángulo', 'rectangle'),
            ('Círculo', 'oval'), ('Polígono', 'polygon'), ('Seleccionar', 'select')
        ]
        
        for name, tool in tools:
            button = tk.Button(tool_frame, text=name, relief=tk.RAISED, command=lambda t=tool: self.set_tool(t))
            button.pack(fill=tk.X, padx=5, pady=2)
            self.tool_buttons[tool] = button

        tk.Label(tool_frame, text="Colores").pack(pady=10)
        tk.Button(tool_frame, text="Color de Borde", command=self.choose_pen_color).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(tool_frame, text="Color de Relleno", command=self.choose_fill_color).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(tool_frame, text="Color de Fondo", command=self.choose_bg_color).pack(fill=tk.X, padx=5, pady=2)
        
        status_frame = tk.Frame(tool_frame, bd=1, relief=tk.SUNKEN)
        status_frame.pack_propagate(False)
        status_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=10)
        self.status_label = tk.Label(status_frame, text="", wraplength=90, justify=tk.LEFT, height=9)
        self.status_label.pack(padx=5, pady=5)

        tk.Button(tool_frame, text="Guardar", command=self.save_canvas).pack(side=tk.BOTTOM, pady=20, padx=5, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg='white', width=800, height=600, relief=tk.SUNKEN, bd=2)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.handle_polygon)
        self.canvas.bind("<Delete>", self.delete_selected)
        
        self.set_tool(self.current_tool)

    def on_press(self, event):
        self.canvas.focus_set()
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.current_tool == 'select':
            self.handle_select_press()
        elif self.current_tool == 'polygon':
            self.polygon_points.extend([self.start_x, self.start_y])
            if len(self.polygon_points) > 2:
                self.canvas.create_line(self.polygon_points[-4:], fill=self.pen_color, tags="poly_line")
        elif self.current_tool == 'pencil':
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, 
                                                       fill=self.pen_color, width=2, capstyle=tk.ROUND, smooth=True)

    def handle_select_press(self):
        clicked_item = self.canvas.find_closest(self.start_x, self.start_y)
        if not clicked_item:
            self.deselect_all()
            return

        clicked_item_id = clicked_item[0]

        if self.resize_handle and clicked_item_id == self.resize_handle:
            self.is_resizing = True
        elif self.rotate_handle and clicked_item_id in (self.rotate_handle, self.rotate_handle + 1):
            self.is_rotating = True
        elif clicked_item_id in self.shapes:
            self.is_moving = True
            if self.selected_item != clicked_item_id:
                self.select_item(clicked_item_id)
        else:
            self.deselect_all()

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.current_tool == 'select' and self.selected_item:
            self.handle_select_drag(cur_x, cur_y)
        elif self.current_tool in ['line', 'rectangle', 'oval', 'pencil']:
            if not self.current_item:
                self.create_shape(cur_x, cur_y)
            else:
                self.update_shape(cur_x, cur_y)

    def handle_select_drag(self, cur_x, cur_y):
        dx, dy = cur_x - self.start_x, cur_y - self.start_y

        if self.is_moving:
            self.canvas.move(self.selected_item, dx, dy)
            if 'points' in self.shapes[self.selected_item]:
                points = self.shapes[self.selected_item]['points']
                self.shapes[self.selected_item]['points'] = [(p[0] + dx, p[1] + dy) for p in points]                
            self.update_selection_handles()

        elif self.is_resizing:
            if self.shapes[self.selected_item]['type'] in ('polygon', 'pencil'):
                self.scale_polygon(dx)
            else:
                coords = self.canvas.coords(self.selected_item)
                self.canvas.coords(self.selected_item, coords[0], coords[1], coords[2] + dx, coords[3] + dy)
            self.update_selection_handles()

        elif self.is_rotating:
            self.rotate_shape(cur_x, cur_y)
            self.update_selection_handles()

        self.start_x, self.start_y = cur_x, cur_y

    def on_release(self, event):
        if self.current_item and self.current_tool not in ['select', 'polygon']:
            self.save_shape()
            
        if self.is_resizing and self.selected_item:
            self.shapes[self.selected_item]['coords'] = self.canvas.coords(self.selected_item)

        self.is_moving = self.is_resizing = self.is_rotating = False

    def create_shape(self, cur_x, cur_y):
        if self.current_tool == 'line':
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, cur_x, cur_y, 
                                                       fill=self.pen_color, width=2)
        elif self.current_tool == 'rectangle':
            points = [self.start_x, self.start_y, cur_x, self.start_y, cur_x, cur_y, self.start_x, cur_y]
            self.current_item = self.canvas.create_polygon(points, outline=self.pen_color, fill=self.fill_color, width=2)
        elif self.current_tool == 'oval':
            points = self.get_oval_points(self.start_x, self.start_y, cur_x, cur_y)
            self.current_item = self.canvas.create_polygon(points, outline=self.pen_color, fill=self.fill_color, width=2)

    def update_shape(self, cur_x, cur_y):
        if self.current_tool == 'pencil':
            coords = self.canvas.coords(self.current_item)
            coords.extend([cur_x, cur_y])
            self.canvas.coords(self.current_item, *coords)
        elif self.current_tool == 'line':
            self.canvas.coords(self.current_item, self.start_x, self.start_y, cur_x, cur_y)
        elif self.current_tool == 'rectangle':
            points = [self.start_x, self.start_y, cur_x, self.start_y, cur_x, cur_y, self.start_x, cur_y]
            self.canvas.coords(self.current_item, *points)
        elif self.current_tool == 'oval':
            points = self.get_oval_points(self.start_x, self.start_y, cur_x, cur_y)
            self.canvas.coords(self.current_item, *points)

    def save_shape(self):
        item_type = self.current_tool
        
        if item_type in ('rectangle', 'oval', 'pencil'):
            flat_points = self.canvas.coords(self.current_item)
            points = [(flat_points[i], flat_points[i+1]) for i in range(0, len(flat_points), 2)]
            shape_data = {
                'type': 'polygon' if item_type != 'pencil' else 'pencil',
                'points': points,
                'rotation': 0
            }
        else:
            coords = self.canvas.coords(self.current_item)
            shape_data = {
                'type': 'line',
                'coords': coords,
                'rotation': 0,
                'points': [(coords[0], coords[1]), (coords[2], coords[3])]
            }
        
        self.shapes[self.current_item] = shape_data
        self.current_item = None

    def set_tool(self, tool):
        if self.current_tool in self.tool_buttons:
            self.tool_buttons[self.current_tool].config(relief=tk.RAISED)

        self.current_tool = tool
        self.deselect_all()
        if tool != 'polygon':
            self.polygon_points = []
            self.canvas.delete("poly_line")
        
        if self.current_tool in self.tool_buttons:
            self.tool_buttons[self.current_tool].config(relief=tk.SUNKEN)
            
        messages = {
            'pencil': "Dibuja a mano alzada.",
            'line': "Haz clic y arrastra para dibujar una línea.",
            'rectangle': "Haz clic y arrastra para dibujar un rectángulo.",
            'oval': "Haz clic y arrastra para dibujar un círculo.",
            'polygon': "Haz clics para añadir puntos. Clic derecho para finalizar el polígono.",
            'select': "Selecciona una figura para moverla, escalarla, rotarla o cambiar sus colores. Presiona Suprimir para borrar."
        }
        self.status_label.config(text=messages.get(tool, ""))

    def choose_pen_color(self):
        color = colorchooser.askcolor(title="Elegir color de borde")[1]
        if color:
            if self.selected_item:
                item_type = self.canvas.type(self.selected_item)
                shape_type = self.shapes[self.selected_item]['type']
                config_key = 'outline' if item_type == 'polygon' and shape_type != 'pencil' else 'fill'
                self.canvas.itemconfig(self.selected_item, **{config_key: color})
            else:
                self.pen_color = color

    def choose_fill_color(self):
        color = colorchooser.askcolor(title="Elegir color de relleno")[1]
        if color:
            if self.selected_item and self.canvas.type(self.selected_item) != 'line':
                self.canvas.itemconfig(self.selected_item, fill=color)
            else:
                self.fill_color = color

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Elegir color de fondo")[1]
        if color:
            self.canvas.config(bg=color)

    def handle_polygon(self, event):
        if self.current_tool == 'polygon' and len(self.polygon_points) >= 6:
            item = self.canvas.create_polygon(self.polygon_points, outline=self.pen_color, 
                                             fill=self.fill_color, width=2)
            self.shapes[item] = {
                'type': 'polygon',
                'points': [(self.polygon_points[i], self.polygon_points[i+1]) for i in range(0, len(self.polygon_points), 2)],
                'rotation': 0
            }
            self.polygon_points = []
        self.canvas.delete("poly_line")

    def save_canvas(self):
        self.deselect_all()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".bmp",
            filetypes=[("BMP", "*.bmp"), ("PNG", "*.png"), ("JPG", "*.jpg"), ("All files", "*.*")]
        )
        if not file_path:
            return

        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        try:
            from PIL import ImageGrab
            ImageGrab.grab().crop((x, y, x1, y1)).save(file_path)
            messagebox.showinfo("Guardado Exitoso", f"La imagen se ha guardado correctamente en:\n{file_path}")
        except Exception:
            messagebox.showerror("Error al Guardar", "No se pudo guardar la imagen.")

    def select_item(self, item_id):
        if self.selected_item == item_id and not (self.resize_handle or self.rotate_handle):
            self.draw_selection_handles(item_id)
            return

        self.deselect_all()
        self.selected_item = item_id
        self.canvas.lift(self.selected_item)
        self.draw_selection_handles(item_id)

    def deselect_all(self):
        if self.selected_item:
            self.delete_selection_handles()
            self.selected_item = None

    def draw_selection_handles(self, item_id):
        self.delete_selection_handles()
        bbox = self.canvas.bbox(item_id)
        if not bbox: return

        x1, y1, x2, y2 = bbox
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.active_outline_color, 
                                   dash=(4, 4), tags="selection_handle")

        handle_size = 10
        self.resize_handle = self.canvas.create_rectangle(x2 - handle_size/2, y2 - handle_size/2, 
                                                         x2 + handle_size/2, y2 + handle_size/2, 
                                                         fill=self.active_outline_color, outline='white', 
                                                         tags="selection_handle")

        cx = (x1 + x2) / 2
        self.rotate_handle = self.canvas.create_line(cx, y1, cx, y1 - 20, fill=self.active_outline_color, 
                                                   width=2, tags="selection_handle")
        self.canvas.create_oval(cx - 5, y1 - 25, cx + 5, y1 - 15, fill=self.active_outline_color, 
                               outline='white', tags="selection_handle")

    def delete_selection_handles(self):
        self.canvas.delete("selection_handle")
        self.resize_handle = self.rotate_handle = None

    def update_selection_handles(self):
        if self.selected_item:
            self.draw_selection_handles(self.selected_item)

    def delete_selected(self, event=None):
        if self.selected_item:
            item_id = self.selected_item
            self.deselect_all()
            self.canvas.delete(item_id)
            del self.shapes[item_id]

    def rotate_point(self, x, y, cx, cy, angle_rad):
        temp_x, temp_y = x - cx, y - cy
        rotated_x = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
        rotated_y = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)
        return rotated_x + cx, rotated_y + cy

    def rotate_shape(self, mouse_x, mouse_y):
        shape_info = self.shapes[self.selected_item]
        
        if shape_info['type'] == 'line':
            points = shape_info['points']
            if not points: return
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)
        elif 'points' in shape_info:
            points = shape_info['points']
            if not points: return
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)
        else:
            return
        
        angle_rad = math.atan2(mouse_y - cy, mouse_x - cx) + math.pi / 2
        rotation_diff = angle_rad - shape_info.get('rotation', 0)
        shape_info['rotation'] = angle_rad
        
        if shape_info['type'] == 'line':
            original_points = shape_info['points']
        else:
            original_points = shape_info['points']
        
        rotated_points = []
        for px, py in original_points:
            rotated_points.extend(self.rotate_point(px, py, cx, cy, rotation_diff))
        
        if shape_info['type'] == 'pencil':
            self.canvas.coords(self.selected_item, *rotated_points)
            shape_info['points'] = [(rotated_points[i], rotated_points[i+1]) for i in range(0, len(rotated_points), 2)]
        elif shape_info['type'] == 'line':
            self.canvas.coords(self.selected_item, *rotated_points)
            shape_info['coords'] = rotated_points
            shape_info['points'] = [(rotated_points[i], rotated_points[i+1]) for i in range(0, len(rotated_points), 2)]
        else:
            self.canvas.coords(self.selected_item, *rotated_points)
            shape_info['points'] = [(rotated_points[i], rotated_points[i+1]) for i in range(0, len(rotated_points), 2)]

    def get_oval_points(self, x1, y1, x2, y2, segments=72):
        points = []
        rx, ry = abs(x2 - x1) / 2, abs(y2 - y1) / 2
        cx, cy = min(x1, x2) + rx, min(y1, y2) + ry
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            points.extend([cx + rx * math.cos(angle), cy + ry * math.sin(angle)])
        return points

    def replace_line_with_polygon(self, points):
        fill_c = self.canvas.itemcget(self.selected_item, "fill")
        
        old_id = self.selected_item
        self.canvas.delete(self.selected_item)
        self.selected_item = self.canvas.create_polygon(points, fill=fill_c, outline=fill_c, width=2)
        
        new_shape_info = self.shapes.pop(old_id)
        new_shape_info.update({
            'type': 'polygon',
            'coords': None,
            'points': [(points[i], points[i+1]) for i in range(0, len(points), 2)]
        })
        self.shapes[self.selected_item] = new_shape_info

    def scale_polygon(self, dx):
        shape_info = self.shapes[self.selected_item]
        bbox = self.canvas.bbox(self.selected_item)
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        scale_factor = 1 + dx / 100.0

        scaled_points = []
        for px, py in shape_info['points']:
            scaled_points.extend([cx + (px - cx) * scale_factor, cy + (py - cy) * scale_factor])
        
        self.canvas.coords(self.selected_item, *scaled_points)
        shape_info['points'] = [(scaled_points[i], scaled_points[i+1]) for i in range(0, len(scaled_points), 2)]

if __name__ == '__main__':
    root = tk.Tk()
    app = Program(root)
    root.mainloop()