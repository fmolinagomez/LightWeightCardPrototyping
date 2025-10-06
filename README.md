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
usage: LWCProto.py [-h] -c FILE [-i]

Card generator for game prototypes

options:
  -h, --help            show this help message and exit
  -c FILE, --cards FILE json file containing cards description
  -i, --images          Add images to cards
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
Las imagenes deben almacenarse en el directorio "images" que se encuentra en la misma carpeta que LWCProto.py, el formato de las imagenes es indiferente y su tamaño tambien estas seran redimensionadas automaticamente para adaptarse al tamaño disponible en el layout. El script genera los resultados dentro del directorio `output/<nombre_del_archivo>/cards`, creando versiones individuales en PNG de cada carta del archivo JSON. Si se habilitan las imágenes (`--images`), también se creará una carpeta `output/<nombre_del_archivo>/images` con las versiones redimensionadas de las ilustraciones.
## Fuentes

Este proyecto se basa en el original [LightWeithgMTGProxy](https://github.com/tilleraj/LightWeightMTGProxy) todo el credito le pertenece a él, hacemos extensivo sus agradecimientos a .Rai de Cardgame Coalition creador del layout original que estamos utilizando
