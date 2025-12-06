# Proyecto de Graficación: Editor de Dibujo en Python

Este repositorio contiene el código fuente y la documentación de una aplicación de dibujo vectorial desarrollada en Python como parte del proyecto de las Unidades 1 y 2 de la materia de Graficación.

## 📋 Descripción

El objetivo principal de este proyecto es simular las funcionalidades de las aplicaciones de dibujo clásicas, permitiendo al usuario generar y manipular gráficos de forma intuitiva. La interfaz gráfica está construida utilizando la biblioteca **Tkinter**.

La aplicación permite el dibujo de primitivas geométricas, edición de propiedades (color y tamaño), transformaciones geométricas (rotación y escalado) y guardado de archivos.

## 🚀 Características Principales

* **Herramientas de Dibujo**:
    * ✏️ **Lápiz**: Dibujo a mano alzada.
    * 📏 **Línea**: Trazado de líneas rectas.
    * ⬜ **Rectángulo**: Creación de figuras rectangulares.
    * ⭕ **Círculo (Óvalo)**: Creación de elipses y círculos.
    * 🔺 **Polígono**: Creación de polígonos irregulares mediante múltiples clics (clic derecho para finalizar).
* **Edición y Transformación**:
    * **Selección**: Herramienta para seleccionar objetos existentes en el lienzo.
    * **Transformaciones**: Mover, rotar y redimensionar las figuras seleccionadas.
    * **Colores**: Personalización de color de borde, color de relleno y color de fondo del lienzo.
* **Gestión de Archivos**:
    * Guardado del lienzo resultante como imagen (formatos soportados: BMP, PNG, JPG).

## 🛠️ Requisitos del Sistema

Para ejecutar este proyecto necesitas tener instalado Python. Las dependencias principales son:

* **Tkinter**: Biblioteca estándar para la GUI (incluida usualmente con Python).
* **Math**: Para cálculos trigonométricos de rotación y formas.
* **Pillow (PIL)**: Necesaria para la funcionalidad de guardado de imágenes (`ImageGrab`).

### Instalación de dependencias
Si no tienes Pillow instalado, puedes hacerlo vía pip:

```bash
pip install Pillow
