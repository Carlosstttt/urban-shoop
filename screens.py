from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen
import webbrowser
from kivy.core.window import Window
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.app import MDApp  # <- Importado de manera global para evitar NameErrors
from plyer import filechooser
from kivy.uix.image import Image
import os
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
from kivymd.uix.card import MDSeparator

# ─── DATOS CENTRALIZADOS ────────────────────────────────────────────────────
PRODUCTOS = {
    "Camisa Casual": {
        "precio": 25.00,
        "imagen": "assets/camisa casual.jpg",
        "descripcion": "Camisa de algodón premium con corte slim. Perfecta para el día a día urbano.",
        "categoria": "Camisas",
        "nuevo": True,
    },
    "Zapatos Urban": {
        "precio": 45.00,
        "imagen": "assets/zapatos.jpg",
        "descripcion": "Sneakers de cuero sintetico con suela antideslizante. Estilo y comodidad.",
        "categoria": "Calzado",
        "nuevo": False,
    },
    "Pantalón Jean": {
        "precio": 35.00,
        "imagen": "assets/pantalon.jpg",
        "descripcion": "Jean slim fit con tela elástica. Resistente y cómodo para cualquier ocasión.",
        "categoria": "Pantalones",
        "nuevo": False,
    },
    "Gorra Urban": {
        "precio": 15.00,
        "imagen": "assets/gorra.jpg",
        "descripcion": "Gorra snapback de tela 100% algodón con bordado exclusivo Urban Shoop.",
        "categoria": "Accesorios",
        "nuevo": True,
    },
}

class Login(Screen):
    def on_enter(self, *args):
        """Método de Kivy que se dispara automáticamente al mostrar el Login"""
        self.animar_percha()

    def animar_percha(self):
        """Busca el widget de la percha por su ID e inicia el balanceo continuo"""
        # Verificamos si existe el ID para evitar crasheos imprevistos
        if "percha_animada" in self.ids:
            percha = self.ids.percha_animada
            
            # Limpiamos cualquier animación previa que pudiera haberse quedado activa
            Animation.cancel_all(percha)
            
            # Definimos la oscilación de 6 grados a -6 grados suavemente ('in_out_quad')
            anim = Animation(angle=6, duration=1.6, transition='in_out_quad') + \
                   Animation(angle=-6, duration=1.6, transition='in_out_quad')
            
            anim.repeat = True
            anim.start(percha)
    def validar_login(self):
        usuario = self.ids.usuario.text.strip()
        clave = self.ids.clave.text.strip()
        if usuario == "admin" and clave == "1234":
            self.ids.mensaje.text = ""
            self.ids.usuario.error = False
            self.ids.clave.error = False
            self.manager.transition.direction = "left"
            self.manager.current = "inicio"
        else:
            self.ids.mensaje.text = "Usuario o contraseña incorrectos"
            self.ids.usuario.error = True
            self.ids.clave.error = True
            self.ids.clave.text = ""

class Inicio(Screen):
    pos_figura = ListProperty([-100, -100])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_motion=self.actualizar_mouse)
    
    def on_pre_enter(self, *args):
        self.actualizar_interfaz_favoritos()

    def actualizar_mouse(self, window, etype, touch):
        if etype in ('update', 'move'):
            local_pos = self.to_local(touch.x, touch.y)
            self.pos_figura = [local_pos[0] - 15, local_pos[1] - 15]

    def actualizar_interfaz_favoritos(self):
        app = MDApp.get_running_app()
        
        if "contenedor_favoritos" not in self.ids or "vista_vacia_favoritos" not in self.ids:
            return
            
        contenedor = self.ids.contenedor_favoritos
        vista_vacia = self.ids.vista_vacia_favoritos
        
        # CORRECCIÓN: En lugar de borrar todo, removemos solo las tarjetas (MDCards) anteriores
        for hijo in list(contenedor.children):
            if isinstance(hijo, MDCard):
                contenedor.remove_widget(hijo)
        
        if not app.favoritos:
            # Si no hay favoritos, mostramos el mensaje informativo
            vista_vacia.opacity = 1
            vista_vacia.height = "250dp"
        else:
            # Si hay favoritos, ocultamos el mensaje informativo
            vista_vacia.opacity = 0
            vista_vacia.height = 0
            
            # Construimos dinámicamente las tarjetas de tus productos favoritos
            for nombre_prod in app.favoritos:
                if nombre_prod in PRODUCTOS:
                    info = PRODUCTOS[nombre_prod]
                    
                    tarjeta = MDCard(
                        orientation="horizontal",
                        size_hint_y=None,
                        height="100dp",
                        padding="12dp",
                        spacing="12dp",
                        radius=[12],
                        ripple_behavior=True,
                        elevation=2,
                        on_release=lambda x, n=nombre_prod: self.abrir_detalle_desde_inicio(n)
                    )
                    
                    box_textos = MDBoxLayout(
                        orientation="vertical",
                        size_hint_x=0.75,
                        pos_hint={"center_y": 0.5},
                        spacing="4dp",
                    )
                    
                    lbl_titulo = MDLabel(
                        text=nombre_prod,
                        bold=True,
                        font_style="Subtitle1",
                    )
                    
                    lbl_precio = MDLabel(
                        text=f"${info['precio']:.2f}",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        font_style="Subtitle1",
                        bold=True,
                    )
                    
                    box_textos.add_widget(lbl_titulo)
                    box_textos.add_widget(lbl_precio)
                    
                    btn_quitar = MDIconButton(
                        icon="heart",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        pos_hint={"center_y": 0.5},
                        on_release=lambda x, n=nombre_prod: self.quitar_de_favoritos_click(n)
                    )
                    
                    tarjeta.add_widget(box_textos)
                    tarjeta.add_widget(btn_quitar)
                    
                    # Añadimos la tarjeta al contenedor principal
                    contenedor.add_widget(tarjeta)

    def quitar_de_favoritos_click(self, nombre_producto):
        app = MDApp.get_running_app()
        app.toggle_favorito(nombre_producto)
        self.actualizar_interfaz_favoritos()

    def ir_a_categoria(self, nombre_categoria):
        self.manager.transition.direction = "left"
        self.manager.current = "catalogo"

    def abrir_detalle_desde_inicio(self, nombre_producto):
        pantalla_detalle = self.manager.get_screen("detalle")
        pantalla_detalle.pantalla_origen = "inicio"
        pantalla_detalle.cargar_datos_producto(nombre_producto)
        self.manager.transition.direction = "left"
        self.manager.current = "detalle"

    def abrir_carrito(self):
        self.manager.transition.direction = "left"
        self.manager.current = "carrito"

    def ejecutar_busqueda(self, texto_buscar):
        texto_limpio = texto_buscar.strip().lower()
        for nombre_producto in PRODUCTOS:
            if texto_limpio in nombre_producto.lower():
                self.abrir_detalle_desde_inicio(nombre_producto)
                self.ids.input_busqueda.text = ""
                self.ids.input_busqueda.error = False
                return
        self.ids.input_busqueda.helper_text = "No se encontraron resultados"
        self.ids.input_busqueda.error = True
    def abrir_red_social(self, red):
        """Abre los enlaces oficiales en el navegador de la PC o Celular"""
        enlaces = {
            "instagram": "https://instagram.com/tu_perfil",
            "tiktok": "https://tiktok.com/@tu_perfil",
            "whatsapp": "https://wa.me/593999999999" # Cambia por tu número real
        }
        
        url = enlaces.get(red)
        if url:
            webbrowser.open(url)

class Catalogo(Screen):
    def regresar_inicio(self):
        self.manager.transition.direction = "right"
        self.manager.current = "inicio"

    def ver_detalle_producto(self, nombre_producto):
        pantalla_detalle = self.manager.get_screen("detalle")
        pantalla_detalle.pantalla_origen = "catalogo"
        pantalla_detalle.cargar_datos_producto(nombre_producto)
        self.manager.transition.direction = "left"
        self.manager.current = "detalle"


class Detalle(Screen):
    talla_seleccionada = StringProperty("M")
    # 1. AÑADE ESTA NUEVA PROPIEDAD AQUÍ ABAJO:
    texto_cm = StringProperty("") 
    pantalla_origen = "catalogo"

    # Mapeo de conversión de tallas de calzado a centímetros
    EQUIVALENCIAS_CALZADO = {
        "38": "24.5 cm",
        "39": "25.0 cm",
        "40": "25.5 cm",
        "41": "26.5 cm",
        "42": "27.0 cm"
    }

    def regresar(self):
        self.ids.txt_cantidad.text = "1"
        self.manager.transition.direction = "right"
        self.manager.current = self.pantalla_origen

    def seleccionar_talla(self, talla):
        self.talla_seleccionada = talla
        
        # 2. ACTUALIZA EL TEXTO EN CM SI ES UN ZAPATO
        if talla in self.EQUIVALENCIAS_CALZADO:
            self.texto_cm = f"👟 Equivale a: {self.EQUIVALENCIAS_CALZADO[talla]}"
        else:
            self.texto_cm = "" # Se limpia si no es calzado

        app = MDApp.get_running_app()
        color_primario = app.theme_cls.primary_color
        
        lista_botones = ["btn_xs", "btn_s", "btn_m", "btn_l", "btn_xl"]
        
        for btn_id in lista_botones:
            if btn_id in self.ids:
                boton = self.ids[btn_id]
                
                if boton.text == talla:
                    boton.line_color = color_primario
                    boton.theme_text_color = "Custom"
                    boton.text_color = color_primario
                else:
                    boton.line_color = [0.5, 0.5, 0.5, 1]  # Gris medio
                    boton.theme_text_color = "Secondary"
    def cambiar_cantidad(self, cambio):
        try:
            cant_actual = int(self.ids.txt_cantidad.text)
        except ValueError:
            cant_actual = 1
        nueva_cant = cant_actual + cambio
        if nueva_cant < 1:
            nueva_cant = 1
        self.ids.txt_cantidad.text = str(nueva_cant)

    def alternar_favorito(self, boton_icono):
        app = MDApp.get_running_app()
        nombre_producto = self.ids.txt_titulo.text
        app.toggle_favorito(nombre_producto)
        if nombre_producto in app.favoritos:
            boton_icono.icon = "heart"
        else:
            boton_icono.icon = "heart-outline"

    def agregar_al_carrito(self):
        cantidad = self.ids.txt_cantidad.text
        producto = self.ids.txt_titulo.text
        precio = self.ids.txt_precio.text
        pantalla_carrito = self.manager.get_screen("carrito")
        pantalla_carrito.agregar_item(producto, precio, cantidad, self.talla_seleccionada)
        self.manager.transition.direction = "left"
        self.manager.current = "carrito"

    def cargar_datos_producto(self, nombre_producto):
        if nombre_producto in PRODUCTOS:
            info = PRODUCTOS[nombre_producto]
            self.ids.txt_titulo.text = nombre_producto
            self.ids.txt_precio.text = f"${info['precio']:.2f}"
            self.ids.txt_descripcion.text = info["descripcion"]
            self.ids.producto_imagen.source = info["imagen"]
            self.ids.txt_cantidad.text = "1"
            
            # ─── DETERMINAR CATEGORÍA Y TALLAS ──────────────────────────────
            categoria = info.get("categoria", "Camisas")
            
            if categoria == "Calzado":
                self.tallas_actuales = ["38", "39", "40", "41", "42"]
            elif categoria == "Accesorios":
                self.tallas_actuales = ["Única", "", "", "", ""]
            else:
                self.tallas_actuales = ["S", "M", "L", "XL", "XXL"]
            
            # Guardamos por defecto la primera disponible
            self.talla_seleccionada = self.tallas_actuales[0]
            
            # Modificamos los textos visuales de los botones
            lista_ids = ["btn_xs", "btn_s", "btn_m", "btn_l", "btn_xl"]
            for i, btn_id in enumerate(lista_ids):
                if btn_id in self.ids:
                    boton = self.ids[btn_id]
                    talla_texto = self.tallas_actuales[i]
                    
                    if talla_texto == "":
                        boton.opacity = 0
                        boton.disabled = True
                    else:
                        boton.opacity = 1
                        boton.disabled = False
                        boton.text = talla_texto  
            # Marcamos visualmente el primer botón (índice 0)
            self.seleccionar_talla_por_indice(0)    
            app = MDApp.get_running_app()
            for widget in self.walk():
                if widget.__class__.__name__ == "MDTopAppBar":
                    nuevo_icono = "heart" if nombre_producto in app.favoritos else "heart-outline"
                    widget.right_action_items = [[nuevo_icono, lambda x: self.alternar_favorito(x)]]
                    break

    def seleccionar_talla_por_indice(self, indice):
        talla_real = self.tallas_actuales[indice]
        self.talla_seleccionada = talla_real
        
        # 3. ACTUALIZA EL TEXTO EN CM CUANDO SE CARGA POR PRIMERA VEZ DESDE EL ÍNDICE
        if talla_real in self.EQUIVALENCIAS_CALZADO:
            self.texto_cm = f" Equivale a: {self.EQUIVALENCIAS_CALZADO[talla_real]}"
        else:
            self.texto_cm = ""

        app = MDApp.get_running_app()
        color_primario = app.theme_cls.primary_color
        lista_ids = ["btn_xs", "btn_s", "btn_m", "btn_l", "btn_xl"]
        
        for i, btn_id in enumerate(lista_ids):
            if btn_id in self.ids:
                boton = self.ids[btn_id]
                if i == indice:
                    boton.line_color = color_primario
                    boton.theme_text_color = "Custom"
                    boton.text_color = color_primario
                else:
                    boton.line_color = [0.5, 0.5, 0.5, 1]
                    boton.theme_text_color = "Secondary"


class Carrito(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.productos_carrito = []

    def on_pre_enter(self, *args):
        self.actualizar_interfaz_carrito()

    def agregar_item(self, nombre, precio_str, cantidad_str, talla="M"):
        precio_num = float(precio_str.replace("$", "").strip())
        cantidad_num = int(cantidad_str)
        for item in self.productos_carrito:
            if item["nombre"] == nombre and item["talla"] == talla:
                item["cantidad"] += cantidad_num
                item["subtotal_item"] = item["precio"] * item["cantidad"]
                return
        self.productos_carrito.append({
            "nombre": nombre,
            "precio": precio_num,
            "cantidad": cantidad_num,
            "talla": talla,
            "subtotal_item": precio_num * cantidad_num,
        })

    def eliminar_item(self, index):
        if 0 <= index < len(self.productos_carrito):
            self.productos_carrito.pop(index)
            self.actualizar_interfaz_carrito()

    def actualizar_interfaz_carrito(self):
        app = MDApp.get_running_app()
        contenedor = self.ids.contenedor_productos
        contenedor.clear_widgets()

        for i, item in enumerate(self.productos_carrito):
            tarjeta = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height="100dp",
                padding="12dp",
                spacing="12dp",
                radius=[12],
                ripple_behavior=True,
                elevation=2,
            )
            box_textos = MDBoxLayout(
                orientation="vertical",
                size_hint_x=0.75,
                pos_hint={"center_y": 0.5},
                spacing="4dp",
            )
            lbl_titulo = MDLabel(
                text=f"{item['nombre']}",
                bold=True,
                font_style="Subtitle1",
                size_hint_y=None,
                height="24dp",
            )
            lbl_titulo.bind(size=lbl_titulo.setter("text_size"))

            lbl_detalle = MDLabel(
                text=f"Talla: {item['talla']}  ·  Cant: {item['cantidad']}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height="18dp",
            )
            lbl_detalle.bind(size=lbl_detalle.setter("text_size"))

            lbl_precio = MDLabel(
                text=f"${item['subtotal_item']:.2f}",
                theme_text_color="Custom",
                text_color=app.theme_cls.primary_color,
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height="24dp",
            )

            box_textos.add_widget(lbl_titulo)
            box_textos.add_widget(lbl_detalle)
            box_textos.add_widget(lbl_precio)

            btn_eliminar = MDIconButton(
                icon="trash-can-outline",
                pos_hint={"center_y": 0.5},
                on_release=lambda x, n=i: self.eliminar_item(n),
            )

            tarjeta.add_widget(box_textos)
            tarjeta.add_widget(btn_eliminar)
            contenedor.add_widget(tarjeta)

        subtotal = sum(i["subtotal_item"] for i in self.productos_carrito)
        envio = 5.00 if subtotal > 0 else 0.00
        total = subtotal + envio

        self.ids.txt_subtotal_num.text = f"${subtotal:.2f}"
        self.ids.txt_envio_num.text = f"${envio:.2f}"
        self.ids.txt_total_num.text = f"${total:.2f}"

    def regresar_anterior(self):
        self.manager.transition.direction = "right"
        self.manager.current = "inicio"

    def procesar_pago(self):
        if not self.productos_carrito:
            return
        layout_botones = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="12dp",
            padding=[0, "10dp", 0, 0],
        )
        btn_tarjeta = MDRaisedButton(
            text="  Tarjeta de Crédito / Débito",
            size_hint_x=1,
            height="48dp",
            on_release=self.finalizar_compra,
        )
        btn_transferencia = MDRaisedButton(
            text="  Transferencia Bancaria",
            size_hint_x=1,
            height="48dp",
            on_release=self.finalizar_compra,
        )
        btn_efectivo = MDRaisedButton(
            text="  Pago Contraentrega (Efectivo)",
            size_hint_x=1,
            height="48dp",
            on_release=self.finalizar_compra,
        )
        layout_botones.add_widget(btn_tarjeta)
        layout_botones.add_widget(btn_transferencia)
        layout_botones.add_widget(btn_efectivo)

        self.pasarela_pago = MDDialog(
            title="Método de Pago",
            type="custom",
            content_cls=layout_botones,
            auto_dismiss=True,
        )
        self.pasarela_pago.open()

    def finalizar_compra(self, boton_presionado):
        if hasattr(self, "pasarela_pago") and self.pasarela_pago:
            self.pasarela_pago.dismiss()
        metodo = boton_presionado.text.strip()
        if "Tarjeta" in metodo:
            self.abrir_formulario_tarjeta()
            return
        if "Transferencia" in metodo:
            self.abrir_transferencia()
            return
        else:
            mensaje = "¡Pedido confirmado!\n\nPreparamos tu paquete. Ten el efectivo listo al momento de la entrega."
        self.dialogo_exito = MDDialog(
            title="¡Compra Exitosa!",
            text=mensaje,
            buttons=[MDRaisedButton(text="ACEPTAR", on_release=self.completar_flujo_final)],
            auto_dismiss=False,
        )
        self.dialogo_exito.open()

    def abrir_transferencia(self):
        self.ruta_comprobante = ""

        layout = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing="10dp", padding=[0, "10dp", 0, 0])
        layout.add_widget(MDLabel(text="Banco Pichincha\nCuenta: 2201984576\nTitular: Urban Shoop S.A.", halign="center"))

        self.lbl_archivo = MDLabel(text="Ningún comprobante seleccionado", halign="center")
        self.preview = Image(size_hint=(1, None), height=220)

        layout.add_widget(MDRaisedButton(text="Seleccionar comprobante", pos_hint={"center_x":0.5},
            on_release=lambda x:self.seleccionar_comprobante()))
        layout.add_widget(self.lbl_archivo)
        layout.add_widget(self.preview)

        self.dialog_transferencia = MDDialog(
            title="  Transferencia Bancaria",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x:self.dialog_transferencia.dismiss()),
                MDRaisedButton(text="Confirmar", on_release=self.completar_flujo_final)
            ],
            auto_dismiss=False
        )
        self.dialog_transferencia.open()

    def seleccionar_comprobante(self):
        filechooser.open_file(
            filters=[("Imágenes","*.jpg;*.jpeg;*.png")],
            on_selection=self.comprobante_seleccionado
        )

    def comprobante_seleccionado(self, selection):
        if selection:
            self.ruta_comprobante=selection[0]
            self.lbl_archivo.text=os.path.basename(self.ruta_comprobante)
            self.preview.source=self.ruta_comprobante
            self.preview.reload()

    def abrir_formulario_tarjeta(self):
        layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing="10dp",
            padding=[0, "10dp", 0, 0],
        )
        self.txt_titular = MDTextField(hint_text="Nombre del Titular", icon_right="account")
        self.txt_numero = MDTextField(hint_text="Número de Tarjeta", icon_right="credit-card", max_text_length=16)
        
        layout_corto = MDBoxLayout(orientation="horizontal", spacing="15dp", adaptive_height=True)
        
        # Guardamos la referencia de la fecha y limitamos a 5 caracteres (MM/AA)
        self.txt_fecha = MDTextField(hint_text="MM/AA", max_text_length=5)
        # ENLACE: Cada vez que el texto cambie, llamará a nuestro formateador
        self.txt_fecha.bind(text=self.formatear_fecha_input)
        
        self.txt_cvv = MDTextField(hint_text="CVV", password=True, max_text_length=3)
        
        layout_corto.add_widget(self.txt_fecha)
        layout_corto.add_widget(self.txt_cvv)
        layout.add_widget(self.txt_titular)
        layout.add_widget(self.txt_numero)
        layout.add_widget(layout_corto)

        self.dialogo_tarjeta = MDDialog(
            title="Datos de la Tarjeta",
            type="custom",
            content_cls=layout,
            buttons=[MDRaisedButton(text="PAGAR AHORA", on_release=self.procesar_pago_tarjeta_formulario)],
            auto_dismiss=True,
        )
        self.dialogo_tarjeta.open()

    def formatear_fecha_input(self, instance, value):
        """Agrega automáticamente el '/' después de los primeros 2 dígitos y limpia caracteres no numéricos"""
        # Eliminamos cualquier cosa que no sea un número
        texto_limpio = "".join([c for c in value if c.isdigit()])
        
        # Si tiene más de 2 dígitos, insertamos la barra diagonal
        if len(texto_limpio) > 2:
            nuevo_texto = f"{texto_limpio[:2]}/{texto_limpio[2:4]}"
        else:
            nuevo_texto = texto_limpio
            
        # Evitamos un bucle infinito al asignar el texto formateado
        if value != nuevo_texto:
            instance.text = nuevo_texto

    def procesar_pago_tarjeta_formulario(self, boton):
        if not self.txt_titular.text or not self.txt_numero.text or not self.txt_cvv.text:
            self.txt_titular.error = True
            return
        if hasattr(self, "dialogo_tarjeta") and self.dialogo_tarjeta:
            self.dialogo_tarjeta.dismiss()
        ultimos = self.txt_numero.text[-4:] if len(self.txt_numero.text) >= 4 else "****"
        self.dialogo_exito = MDDialog(
            title="¡Pago Procesado!",
            text=f"Tu tarjeta terminada en {ultimos} fue procesada.\n\n¡Gracias por tu compra en Urban Shoop!",
            buttons=[MDRaisedButton(text="TERMINAR", on_release=self.completar_flujo_final)],
            auto_dismiss=False,
        )
        self.dialogo_exito.open()

    def completar_flujo_final(self, boton_aceptar):
        # --- NUEVO: GUARDAR EN EL HISTORIAL ANTES DE BORRAR EL CARRITO ---
        if self.productos_carrito:
            store = JsonStore('historial_compras.json')
            id_pedido = datetime.now().strftime("%Y%m%d_%H%M%S")
            fecha_legible = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Guardamos los datos clave de la compra
            store.put(id_pedido,
                fecha=fecha_legible,
                total=self.ids.txt_total_num.text,
                metodo="Transferencia o Tarjeta", # Puedes refinarlo según el flujo
                productos=[{
                    "nombre": p["nombre"],
                    "talla": p["talla"],
                    "cantidad": p["cantidad"]
                } for p in self.productos_carrito]
            )
        # -----------------------------------------------------------------

        if hasattr(self, "dialog_transferencia") and self.dialog_transferencia:
            self.dialog_transferencia.dismiss()
        if hasattr(self, "dialogo_exito") and self.dialogo_exito:
            self.dialogo_exito.dismiss()
            
        self.productos_carrito = []
        self.manager.transition.direction = "right"
        self.manager.current = "inicio"

class HistorialScreen(Screen):
    def on_pre_enter(self, *args):
        self.cargar_historial_interfaz()

    def cargar_historial_interfaz(self):
        store = JsonStore('historial_compras.json')
        contenedor = self.ids.contenedor_pedidos
        contenedor.clear_widgets()

        # Si no hay pedidos grabados
        if not store.keys():
            contenedor.add_widget(
                MDLabel(
                    text="Aún no has realizado ninguna compra.",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Body1",
                    size_hint_y=None,
                    height="100dp"
                )
            )
            return

        # Cargamos los pedidos del más reciente al más viejo
        for pedido_id in reversed(sorted(store.keys())):
            datos = store.get(pedido_id)
            
            # Tarjeta contenedora del pedido
            tarjeta = MDCard(
                orientation="vertical",
                size_hint_y=None,
                adaptive_height=True,
                padding="14dp",
                spacing="8dp",
                radius=[12],
                md_bg_color=[0.14, 0.14, 0.17, 1],
                elevation=2
            )

            # Encabezado (Fecha y Total)
            box_encabezado = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="30dp")
            box_encabezado.add_widget(MDLabel(text=f" {datos['fecha']}", bold=True, font_style="Subtitle2"))
            box_encabezado.add_widget(MDLabel(text=f"Total: {datos['total']}", halign="right", bold=True, text_color=MDApp.get_running_app().theme_cls.primary_color, theme_text_color="Custom"))
            
            tarjeta.add_widget(box_encabezado)
            tarjeta.add_widget(MDSeparator())

            # Listar los productos de esa compra
            for prod in datos['productos']:
                lbl_prod = MDLabel(
                    text=f"• {prod['nombre']} (Talla: {prod['talla']}) x{prod['cantidad']}",
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height="20dp"
                )
                tarjeta.add_widget(lbl_prod)
                
            # Método de pago usado
            tarjeta.add_widget(MDLabel(text=f" Pago: {datos['metodo']}", font_style="Caption", theme_text_color="Hint"))

            contenedor.add_widget(tarjeta)

    def regresar_perfil(self):
        self.manager.transition.direction = "right"
        self.manager.current = "inicio" # O como se llame tu pantalla de perfil en el ScreenManager
# NOTA: Se eliminó FavoritosScreen para evitar conflictos con Inicio.actualizar_interfaz_favoritos()