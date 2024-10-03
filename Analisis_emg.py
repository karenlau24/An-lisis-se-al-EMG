import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.fft import fft 
from scipy.stats import f_oneway


# -----------------------FUNCIONES CON LAS QUE SE VA A TRABAJAR ------------------------------------------

# Butterworth

def pasabaja(cutoff, fs, order=5):
    nyquist = 0.5 * fs 
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def pasaalta(cutoff, fs, order=5):
    nyquist = 0.5 * fs 
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


# Filtros

def filtros(data, fs):
   
    fc_alta = 200 
    fc_baja = 300  
    
    b_high, a_high = pasaalta(fc_alta, fs, order=4)
    b_low, a_low = pasabaja(fc_baja, fs, order=4)
    
    # Pasa alta
    
    filtrada = filtfilt(b_high, a_high, data)
    
    # Pasa baja
    
    filtrada = filtfilt(b_low, a_low, filtrada)
    
    return filtrada

# Hanning

def hanning(data, window_size, fs):
    
    n = len(data)
    ventana = np.hanning(window_size)
    datos_aventanados = []

    
    for i in range(0, n - window_size, window_size):
        
        segmento = data[i:i+window_size]
        segmento_aventanado = segmento * ventana
        datos_aventanados.append(segmento_aventanado)

    
    datos_aventanados = np.concatenate(datos_aventanados)
    
    return datos_aventanados

# Distintos de cero

def distinto_de_cero(data_aventanada):
    segmentos = []
    segmento_actual = []
    
    for i in range(len(data_aventanada)):
        if data_aventanada[i] != 0:
            segmento_actual.append(data_aventanada[i])
        else:
            if len(segmento_actual) > 0:
                segmentos.append(np.array(segmento_actual))
                segmento_actual = []
    
    if len(segmento_actual) > 0:
        segmentos.append(np.array(segmento_actual))
    
    return segmentos

# FFT   
def fft_segmentos(segmentos, fs):
    for i, segmento in enumerate(segmentos):
        espectro = np.abs(fft(segmento))
        frecuencias = np.fft.fftfreq(len(segmento), d=1/fs)
        plt.figure(figsize=(10, 6), facecolor='blanchedalmond') 
        plt.plot(frecuencias[:len(segmento) // 2], espectro[:len(segmento) // 2], 
         label=f'FFT del Segmento {i+1}', 
         color='goldenrod', linewidth=2, linestyle='-')  
        plt.title('Espectro de Frecuencias', fontsize=16, fontweight='bold')
        plt.xlabel('Frecuencia (Hz)', fontsize=16)
        plt.ylabel('Magnitud', fontsize=16)
        plt.grid(color='gray', linestyle=':', linewidth=0.5)  
        plt.legend(loc='upper right', fontsize=12, frameon=False)
        plt.tight_layout()
        plt.show()
# ---------------------------------------------TRABAJO CON LOS DATOS OBTENIDOS-------------------------

# Cargar los datos
datos = np.loadtxt('karen_y_pau.txt', delimiter=',')
# Separar las columnas en variables tiempo y voltaje
tiempo = datos[:, 0]  # Primera columna para el tiempo
voltaje = datos[:, 1]  # Segunda columna para los valores de voltaje

# Definir frecuencia de muestreo (1000 Hz)
fs = 2000  # Frecuencia de muestreo en Hz

# Filtrar la señal
voltaje_filtrado = filtros(voltaje, fs)

# Aplicar aventanamiento de Hanning con un tamaño de ventana de 256 muestras

window_size = 256
voltaje_aventanado = hanning(voltaje_filtrado, window_size, fs)

# Separar los segmentos no nulos de la señal aventanada
segmentos = distinto_de_cero(voltaje_aventanado)

#Estilos 



# Graficar la señal original, la filtrada y la aventanada
plt.figure(figsize=(12, 8), facecolor='blanchedalmond')
plt.subplots_adjust(hspace=0.5)


# Señal original
plt.subplot(3, 1, 1)
plt.plot(tiempo, voltaje, label='Señal original', color='#164484')
plt.xlabel('Tiempo (s)')
plt.ylabel('Voltaje (mV)')
plt.title('Señal EMG original', fontsize=10, fontweight='bold')
plt.grid(True)
plt.legend()

# Señal filtrada
plt.subplot(3, 1, 2)
plt.plot(tiempo, voltaje_filtrado, label='Señal filtrada', color='#458744')
plt.xlabel('Tiempo (s)', fontsize=13)
plt.ylabel('Voltaje (mV)', fontsize=13)
plt.title('Señal EMG con filtro Butterworth', fontsize=10, fontweight='bold')
plt.grid(True)
plt.legend()

# Señal aventanada con Hanning
plt.subplot(3, 1, 3)
plt.plot(tiempo[:len(voltaje_aventanado)], voltaje_aventanado, label='Señal Hanning', color='#815270')
plt.xlabel('Tiempo (s)', fontsize=13)
plt.ylabel('Voltaje (mV)', fontsize=13)
plt.title('Señal EMG aventanada con Hanning', fontsize=10, fontweight='bold')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

# Calcular la FFT de los segmentos no nulos y graficar
fft_segmentos(segmentos, fs)

def calcular_media_segmentos(segmentos):
    for i, segmento in enumerate(segmentos):
        media = np.mean(segmento)
        mediana = np.median(segmento)
        desviacion_std = np.std(segmento)
        print(f'Segmento {i+1}:')
        print(f'   Media: {media}')
        print(f'   Mediana: {mediana}')
        print(f'   Desviación estándar: {desviacion_std}\n')



# Función para graficar los segmentos no nulos
def graficar_segmentos(segmentos, fs):
    plt.figure(figsize=(12, 8), facecolor='blanchedalmond')
    
    for i, segmento in enumerate(segmentos):
        plt.subplot(len(segmentos), 1, i + 1)
        t_segmento = np.arange(0, len(segmento)) / fs  # Crear eje de tiempo para cada segmento
        plt.plot(t_segmento, segmento, label=f'Segmento {i+1}', color='orange')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Voltaje (mV)')
        plt.title(f'Segmento {i+1} de la señal aventanada')
        plt.grid(True)
        plt.legend()
    
    plt.tight_layout()
    plt.show()


# Llamar a la función de graficación de segmentos
graficar_segmentos(segmentos, fs)

medias = calcular_media_segmentos(segmentos)

# Aplicar ANOVA
resultados_anova = f_oneway(*segmentos)


print(f'Estadístico F: {resultados_anova.statistic}')
print(f'Valor p: {resultados_anova.pvalue}')

alpha = 0.05
if resultados_anova.pvalue < alpha:
    print("Se rechaza la hipótesis nula: hay diferencias significativas entre las medias de los segmentos.")
else:
    print("No se rechaza la hipótesis nula: no hay diferencias significativas entre las medias de los segmentos.")
