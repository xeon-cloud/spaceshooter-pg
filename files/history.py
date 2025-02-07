import pygame_menu
import pygame_menu.events
import pygame_menu.themes

import methods

class Panel:
    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_selection_effect = None
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        mytheme.title_font_size = 1

        self.menu = pygame_menu.Menu('История', width, height, theme=mytheme, center_content=False)

        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)
        
        # self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)
        self.table = self.menu.add.table('Тест', border_color='white').set_alignment("align-center").update_font(style={"size": 18, "name": methods.load_font("PressStart2P-Regular")})

        self.table.default_cell_padding = 10
        self.renderData()
        self.menu.mainloop(screen)

    def renderData(self):
        self.table.add_row(['№ Игры', 'Дата', 'Продолжительность', 'Ступень', 'Статус'], cell_border_color='white', cell_align=pygame_menu.locals.ALIGN_CENTER)
        for i, j in enumerate(methods.loadHistory()):
            self.table.add_row([i + 1] + j, cell_border_color='white', cell_align=pygame_menu.locals.ALIGN_CENTER)
        
    def Return(self):
        self.menu.disable()