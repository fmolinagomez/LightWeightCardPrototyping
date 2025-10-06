# LightWeightCardPrototyping

Genera cartas de forma rapida y sencilla para tus prototipos

## Descripcion

Este proyecto esta basado en https://github.com/tilleraj/LightWeightMTGProxy, cerca del 80% del codigo les pertenece, sobre todo el relativo a la generacion de las cartas utilizando cairo. El objetivo de este proyecto es facilitar la generacion de cartas para prototipos de juegos de mesa automatizando en la medida de lo posible las tareas de añadir una imagen asi como el texto relativo a la carta. Esta automatizacion se realiza definiendo la carta en un archivo de texto.

## Primero Pasos

En principio todo lo que se necesita para ejecutar este script es python 3.9 instalado en tu ordenador

### Windows
- Descarga e instala Python 3 [Link](https://www.python.org/downloads/windows/)
- Abre una consola CMD
- Ejecuta pip install -r requirements.txt

### Linux
- Descarga e instala Python 3 utilizando el gestor de paquetes de tu distribucion
- Abre una consola
- Ejecuta pip install -r requirements.txt

## Documentacion

### Sintaxis

```
usage: LWCProto.py [-h] -d FILE -c FILE [-i] [-r RGB RGB RGB] [-l FILE]
                   [--single-card] [-o OUTPUT_DIR]

Deck Generator for Game Designers

optional arguments:
  -h, --help            show this help message and exit
  -d FILE, --deck FILE  csv file containing the deck
  -c FILE, --cards FILE
                        json file containing cards description
  -i, --images          Add images to cards
  -r RGB RGB RGB, --rgb RGB RGB RGB
                        Update layout card border colour with given R,G,B, only works with default layout
  -l FILE, --layout FILE (==> Not ready yet)
                        Use a different layout than default
  --single-card          Render each card as an individual 63x85mm PNG at 300 DPI
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory where generated decks will be stored
```
### Archivo de definicion de cartas:

El archivo de definicion de cartas es un archivo en jormato json con el siguente formato:
```

{
    "CartID":
        {
            "header": {
                "text": "str",
                "color": "#RRGGBB",
                "banner": true | false,
                "banner_color": "#RRGGBB"
            },
            "type": "str",
            "subtype": "str",
            "card_text": {
                "text": "str",
                "colour": "#RRGGBB"
            },
            "background_color": "#RRGGBB",
            "footer": {
                "text": "str",
                "color": "#RRGGBB",
                "font_style": "normal | negrita | itálica"
            },
            "manaCost": "str",
            "power": int,
            "toughness": int,
            "image": "str",
            "full_frame_image": true | false
        },
        ....
}
```
El objeto `header` define el texto visible en la parte superior de la carta. El campo `color` ajusta el color del texto, mientras que los campos `banner` y `banner_color` permiten activar un recuadro de color sólido detrás del encabezado cuando sea necesario.
El bloque `card_text` permite especificar el texto del cuerpo y el color con el que debe renderizarse. Para las imágenes puedes indicar un nombre de archivo directamente o un objeto con las claves `source` y `full_frame`. Cuando `full_frame_image` (o `full_frame` en el objeto de imagen) es `true`, la ilustración se ampliará para cubrir toda la carta; en caso contrario se mantendrá dentro del marco de arte.
Puedes controlar el color de fondo del lienzo con el campo opcional `background_color`. Debe indicarse en formato hexadecimal (`#RRGGBB`) y solo se aplica cuando la carta no utiliza una imagen a pantalla completa (`full_frame_image: false`).
El bloque `footer` es opcional y permite mostrar una nota en la parte inferior de la carta. Puedes personalizar el texto, su color y el estilo de fuente (`normal`, `negrita` o `itálica`). Si no se especifica `font_style`, se utilizará `normal` por defecto.
Las imagenes deben almacenarse en el directorio "images" que se encuentra en la misma carpeta que LWCProto.py, el formato de las imagenes es indiferente y su tamaño tambien estas seran redimensionadas automaticamente para adaptarse al tamaño disponible en el layout. Puedes utilizar el argumento `--output-dir` para indicar otro directorio base donde almacenar las cartas generadas, lo que facilita mantener varios prototipos separados.

### Archivo de definicion del mazo

Archivo en formato csv que tiene el siguiente formato:
```
Qty,Name
40,CartID_1
300,CartID_2
```
## Fuentes

Este proyecto se basa en el original [LightWeithgMTGProxy](https://github.com/tilleraj/LightWeightMTGProxy) todo el credito le pertenece a él, hacemos extensivo sus agradecimientos a .Rai de Cardgame Coalition creador del layout original que estamos utilizando
