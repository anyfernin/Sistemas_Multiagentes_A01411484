# -*- coding: utf-8 -*-
"""M1_Actividad_A01411484.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XvdsKNH68uE6ezjo4HoB2GnMX9I_nfsO

### M1. Actividad
### Ana Fernanda Hernández Tovar A01411484

### INSTRUCCIONES

Para este problema, deberás entregar, de manera individual, un informe en PDF que estudie las estadísticas de un robot de limpieza reactivo, así como el enlace al repositorio en Github del código desarrollado para esta actividad. El código debe ajustarse al estilo solicita en el siguiente documento.

Dado:



*   Habitación de MxN espacios.
*   Número de agentes.
*   Porcentaje de celdas inicialmente sucias.
*   Tiempo máximo de ejecución.



Realiza la siguiente simulación:


1.   Inicializa las celdas sucias (ubicaciones aleatorias).
2.   Todos los agentes empiezan en la celda [1,1].

En cada paso de tiempo:

1.   Si la celda está sucia, entonces aspira.
2.   Si la celda está limpia, el agente elije una dirección aleatoria para moverse (unas de las 8 celdas vecinas) y elije la acción de movimiento (si no puede moverse allí, permanecerá en la misma celda).

*   Se ejecuta el tiempo máximo establecido.

Deberás recopilar la siguiente información durante la ejecución:


*   Tiempo necesario hasta que todas las celdas estén limpias (o se haya llegado al tiempo máximo).
*   Porcentaje de celdas limpias después del termino de la simulación.


*   Número de movimientos realizados por todos los agentes.
*   Analiza cómo la cantidad de agentes impacta el tiempo dedicado, así como la cantidad de movimientos realizados. Desarrollar un informe con lo observado.


 Incluye el diagrama de tu máquina de estados del agente.
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install mesa
# La clase `Model` se hace cargo de los atributos a nivel del modelo, maneja los agentes. 
# Cada modelo puede contener múltiples agentes y todos ellos son instancias de la clase `Agent`.
from mesa import Agent, Model 

# Debido a que necesitamos un solo agente por celda elegimos `SingleGrid` que fuerza un solo objeto por celda.
from mesa.space import MultiGrid

# Con `SimultaneousActivation` hacemos que todos los agentes se activen de manera simultanea.
from mesa.time import SimultaneousActivation

# Vamos a hacer uso de `DataCollector` para obtener el grid completo cada paso (o generación) y lo usaremos para graficarlo.
from mesa.datacollection import DataCollector

# mathplotlib lo usamos para graficar/visualizar como evoluciona el autómata celular.
# %matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Definimos los siguientes paquetes para manejar valores númericos.
import numpy as np
import pandas as pd
import random

# Definimos otros paquetes que vamos a usar para medir el tiempo de ejecución de nuestro algoritmo.
import time
import datetime

def grid_room(model): # La clase grid_room se utiliza para obtener el grid de la habitación
  grid = np.zeros((model.grid.width, model.grid.height))
  for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        for objeto in cell_content:
            if isinstance(objeto, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(objeto, Celda):
                grid[x][y] = objeto.estado
  return grid

class RobotLimpieza(Agent): #Clase RobotLimpieza genera y realiza los movimientos del robot de limpieza dependiendo de la logica de las instrucciones

  def __init__(self, un_id, model):
    super().__init__(un_id, model)
    self.sig_pos = None
    self.pos = un_id

  def step(self):
    vecinos = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True)
       
       # Defino el siguiente estado que va a tener el piso para la siguiente iteracion sin asignarlo todavia eso lo hago en el método `advance`.
    for vecino in vecinos:
      if isinstance(vecino,Celda) and self.pos == vecino.pos:
        if vecino.estado == 1:
            #limpiar
          vecino.sig_estado = 0
          self.sig_pos = self.pos  
        else:
          vecinos2 = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
          vecino.sig_estado = 0
          self.sig_pos = random.choice(vecinos2)
        break


   # Actualizamos el estado del piso
  def advance(self):

    vecinos = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True)
    
    for vecino in vecinos:
      if isinstance(vecino, Celda) and self.pos == vecino.pos:
        vecino.estado = vecino.sig_estado
        break
    self.model.grid.move_agent(self, self.sig_pos)  # Movemos la aspiradora a su nueva posicion
    self.pos = self.sig_pos

class Celda(Agent): #Clase Celda que inicializa la celda del piso
    #SUCIO = 1
    #LIMPIO = 0
    
    def __init__(self, un_id, modelo, estado):
        super().__init__(un_id, modelo)
        self.pos =  un_id
        self.estado = estado
        self.sig_estado = None

class Habitacion(Model): # Clase Habitación es para modelar la habitación del ejercicio, y tambien llama las funciones para empezar a recolectar datos 

  def __init__(self, M, N, num_agentes, por_celdas_sucias):
    self.num_agentes = num_agentes
    self.por_celdas_sucias = por_celdas_sucias
    self.por_celdas_limpias = 1 - por_celdas_sucias
    self.grid = MultiGrid(M, N, False)
    self.schedule = SimultaneousActivation(self)

    # Posicionar celdas sucias de forma aleatoria
    num_celdas_sucias = int(M*N * por_celdas_sucias)
    for (content, x, y) in self.grid.coord_iter():
      num = random.randint(0,1)
      if num == 1 and num_celdas_sucias > 0:
        a = Celda((x, y), self, 1)
        num_celdas_sucias -= 1
      else:
        a = Celda((x, y), self, 0)
      
      self.grid.place_agent(a, (x, y))
      self.schedule.add(a)

    #pocisiona a los agentes del robot limpieza
    for id in range(num_agentes):
      r = RobotLimpieza(id, self)
      self.grid.place_agent(r, (1, 1))
      self.schedule.add(r)

    self.datacollector = DataCollector(
        model_reporters={"Grid": grid_room})
    
    
  def step(self):
    self.datacollector.collect(self)
    self.schedule.step()

# Datos de la habitacion:
M = 10
N = 10

# Numero de agentes
num_agentes = 3

# Porcentaje de celdas inicialmente sucias:
por_celdas_sucias = 0.6

# Tiempo máximo de ejecución (segundos)
tiempo_max = 0.06

#Se obtiene el tiempo inicial
tiempo_inicio = str(datetime.timedelta(seconds=tiempo_max))


model = Habitacion(M, N, num_agentes, por_celdas_sucias)
start_time = time.time()
while((time.time() - start_time) < tiempo_max):
  model.step()

tiempo_ejecucion = str(datetime.timedelta(seconds=(time.time() - start_time)))
# Imprimimos el tiempo que le tomó correr al modelo.
print('Tiempo de ejecución:', tiempo_ejecucion)

all_grid = model.datacollector.get_model_vars_dataframe()

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# 
# fig, axs = plt.subplots(figsize=(7,7))
# axs.set_xticks([])
# axs.set_yticks([])
# patch = plt.imshow(all_grid.iloc[0][0], cmap=plt.cm.binary)
# 
# def animate(i):
#   patch.set_data(all_grid.iloc[i][0])
# 
# anim = animation.FuncAnimation(fig, animate, frames=len(all_grid))

anim

movimientos = model.datacollector.get_agent_vars_dataframe()

print('Tiempo necesario hasta que todas las celdas estén limpias:', tiempo_ejecucion, '/', tiempo_inicio)
print('Porcentaje de celdas limpias después del termino de la simulación:', model.por_celdas_limpias)
print('Número de movimientos realizados por todos los agentes:', movimientos.tail().sum())