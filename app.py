from flask import Flask, request, render_template, redirect, url_for, session    
import requests    
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


app = Flask(__name__)

# Ruta para la página principal (index.html)
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    if request.method == 'POST':
        city = request.form['city']
        api_key = "f86a587487d6bd7471b9385ced1a35e4"
        weather_data = get_weather(city, api_key)
    
    return render_template('index.html', weather=weather_data)
    


# Ruta para la página de ecosistemas (ecosistemas.html)
@app.route('/ecosistemas')
def ecosistemas():
    return render_template('ecosistemas.html')

# Ruta para la página de especies (especies.html)
@app.route('/especies')
def especies():
    return render_template('especies.html')

# Ruta para la página de fundaciones (fundaciones.html)
@app.route('/fundaciones')
def fundaciones():
    return render_template('fundaciones.html')

#@app.route('/conocenos')
#def conocenos():
#    return render_template('conocenos.html')

@app.route('/conocenos', methods=['GET', 'POST'])
def conocenos():
    mensaje_confirmacion = session.pop('mensaje_confirmacion', None)
    return render_template('conocenos.html', mensajeOK=mensaje_confirmacion)


# Ruta para la página de ecosistemas (estadistica.html)
@app.route('/estadistica')
def estadistica():
    # Cargar el archivo CSV
    try:
        df = pd.read_csv('datos_biodiversidad_boyaca_cundinamarca.csv', encoding='latin1')
    except FileNotFoundError:
        return "Archivo CSV no encontrado", 404
    except UnicodeDecodeError:
        return "Error de decodificación de caracteres en el archivo CSV", 500    

    # Realizar algunos cálculos
    conteo_departamento = df['Departamento'].value_counts().to_dict()
    
    especies_unicas = df['Especie'].nunique()
    lista_especies_unicas = df['Especie'].unique().tolist()  # Lista de las especies únicas
 
    promedio_latitud = round(df['Latitud'].mean(), 4)
    promedio_longitud = round(df['Longitud'].mean(), 4)
    
    especies_unicas_departamento = df.groupby('Departamento')['Especie'].nunique()  # Agrupamos los datos por 'Departamento' y contamos las especies únicas en cada uno


    # Crear gráfico de la distribución de especies (Top 10 especies)
    plt.figure(figsize=(12, 8))
    especies_conteo = df['Especie'].value_counts().head(10)
    
    especies_conteo.plot(kind='bar', color='skyblue')
    plt.title('Distribución de las Principales Especies', fontsize=16)
    plt.xlabel('Especie', fontsize=12)
    plt.ylabel('Conteo', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    grafico_path1 = 'static/images/grafico_distribucion_especies.png'
    plt.savefig(grafico_path1)
    plt.close()

    # Gráfico circular (pie chart) de distribución de especies por departamento
    plt.figure(figsize=(8, 8))
    
    # Colores personalizados
    colores = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0', '#ffb3e6']
    
    plt.pie(conteo_departamento.values(), 
            labels=conteo_departamento.keys(), 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colores, 
            wedgeprops={'edgecolor': 'black'})
    
    plt.title('Distribución de Especies por Departamento', fontsize=16)
    plt.axis('equal')  # Asegura que el gráfico sea un círculo
    grafico_path2 = 'static/images/grafico_pie_departamento.png'
    plt.savefig(grafico_path2)
    plt.close()


    # Pasar los datos a la plantilla
    return render_template('estadistica.html', 
                           conteo_departamento=conteo_departamento, 
                           especies_unicas=especies_unicas,
                           lista_especies_unicas=lista_especies_unicas, 
                           promedio_latitud=promedio_latitud,
                           promedio_longitud=promedio_longitud,
                           grafico_path=grafico_path1,
                           grafico_path2=grafico_path2)


def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()


app.secret_key = 'supersecretkey'  # Necesario para usar la sesión

#ruta para guardar datos del formulario Escribenos de la pagina conocenos.html 
@app.route('/guardar_datos', methods=['POST'])   # se conoce como endpoint 
def guardar_datos():
    nombre = request.form['nombre']
    email = request.form['email']
    asunto = request.form['asunto']
    mensaje = request.form['mensaje']

    # Validación básica
    if not nombre or not email or not asunto or not mensaje:
        return "Todos los campos son obligatorios"

    # Formato de correo electrónico (ejemplo básico)
    if not "@" in email or not "." in email:
        return "Formato de correo electrónico inválido"

    # Guardar en archivo con formato CSV y fecha
    with open('mensajes.csv', 'a') as archivo:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archivo.write(f"{fecha_hora},{nombre},{email},{asunto},{mensaje}\n")

    # return redirect(url_for('confirmacion', nombre=nombre))

    # Almacenar el mensaje de confirmación en la sesión
    session['mensaje_confirmacion'] = f"Mensaje enviado y guardado exitosamente, {nombre}"
    
    return redirect(url_for('conocenos'))


#@app.route('/confirmacion') 
#def confirmacion ():
#    nombre = request.args.get('nombre')
#    return f"<h2>Mensaje enviado y guardado exitosamente, { nombre }</h2><a href='/'>Volver al formulario</a>"  





#main
if __name__ == '__main__':  
    app.run(debug=True)
