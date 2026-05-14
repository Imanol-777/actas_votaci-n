# TITULO DEL PROYECTO...
Proyecto realizado para la materia de Programación II, en este proyecto se hace uso de la inteligencia artificial para leer y extraer automaticamente los resultados de votacion de  actas electorales fotografiadas.

## Equipo FizzBuzz
## Nombres de los integrantes del equipo:
Mario Jonathan Morales Aguilar  
...  
...  
...  

## Que hace el proyecto?
El proyecto consta de dos codigos:
1. El primero es llamado **corregir_fotos.py** y corrige automaticamente la inclinacion de las fotos de las actas antes de procesarlas
2. El segundo es llamado **aaa.py** (cambiar nombre), manda las fotos a Azure OpenAI y de cada foto extrae los votos de cada partido en formato JSON

## IMPORTANTE
### Estructura de carpetas
proyecto/ 
      corregir_fotos.py     #codigo usado para corregir la inclinacion de las fotos
      aaa.py                #codigo principal usado para la extraccion de datos 
      actas_resultados/     #carpeta donde se meten las fotos de las actas
 actas
      json_resultados/      #carpeta donde se guaradan los resultados (se crea automaticamente)


## Cómo usarlo      
### Paso 1 - Corregir las fotos (opcional)
Si las fotos estan inclinadas puedes usar el codigo mencionado anteriormente para corregirlas:  
corregir_fotos.py  
actas_resultados/  
las fotos corregidas deberian guardarse en "actas_resultados/corregidas/".

### paso 2 - Extraer los datos  
Pon las fotos seleccionadas en la carpeta "actas_resultados" y ejecuta el codigo:  
aaa.py  
Los archivos deberian guardarse en la carpeta "json_resultados/" como archivos .json, uno por cada acta

### Salida
Cada acta genera un archivo .json con esta estructura:  
{ 
  "acta": (nombre_del_archivo),
  "resultados": [
    {"partido": "PAN" , "votos": 53},  
    ...  
    ...  
