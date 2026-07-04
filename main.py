from kivy.config import Config

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from screens import Login, Inicio, Catalogo, Detalle, Carrito, HistorialScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.properties import ListProperty
from kivy.storage.jsonstore import JsonStore


class GestorPantallas(ScreenManager):
    pass

class TiendaApp(MDApp):

    dialogo = None
    favoritos= ListProperty([])

    def build(self):
        store = JsonStore('historial_compras.json')
        store.clear()
        # Paleta urbana: oscura con acento naranja
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Dark"

        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/inicio.kv")
        Builder.load_file("kv/catalogo.kv")
        Builder.load_file("kv/detalle.kv")
        Builder.load_file("kv/carrito.kv")
        Builder.load_file("kv/historial.kv")

        sm = GestorPantallas(transition=SlideTransition(duration=0.25))

        sm.add_widget(Login(name="login"))
        sm.add_widget(Inicio(name="inicio"))
        sm.add_widget(Catalogo(name="catalogo"))
        sm.add_widget(Detalle(name="detalle"))
        sm.add_widget(Carrito(name="carrito"))
        sm.add_widget(HistorialScreen(name="historial"))

        sm.current = "login"
        return sm
    
    def toggle_favorito(self, producto):
        """
        Recibe un diccionario o ID del producto. 
        Si ya está, lo quita. Si no está, lo agrega.
        """
        if producto in self.favoritos:
            self.favoritos.remove(producto)
            print(f"Eliminado de favoritos: {producto}")
        else:
            self.favoritos.append(producto)
            print(f"Añadido a favoritos: {producto}")

    def mostrar_dialogo_salida(self, *args):
        if not self.dialogo:
            self.dialogo = MDDialog(
                title="¿Cerrar sesión?",
                text="Los artículos en tu carrito no se guardarán.",
                size_hint=(0.85, None),
                auto_dismiss=False,
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.cerrar_dialogo
                    ),
                    MDFlatButton(
                        text="SÍ, SALIR",
                        theme_text_color="Custom",
                        text_color=(1, 0.3, 0.3, 1),
                        on_release=self.ejecutar_salida
                    ),
                ],
            )
        self.dialogo.open()

    def cerrar_dialogo(self, *args):
        if self.dialogo:
            self.dialogo.dismiss()

    def ejecutar_salida(self, *args):
        if self.dialogo:
            self.dialogo.dismiss()
        self.root.current = "login"

if __name__ == "__main__":
    TiendaApp().run()
