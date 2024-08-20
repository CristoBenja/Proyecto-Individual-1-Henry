## Importo las librerías a utilizar
from fastapi import FastAPI, HTTPException
import pandas as pd

## Instancio el objeto FastAPI() 
app = FastAPI()

## Cargo los csv de "movies_ETL" y "credits_ETL"
df_movies = pd.read_csv("Movies_ETL.csv")
df_movies["release_date"] = pd.to_datetime(df_movies["release_date"])
## Creo una columna mes para devolver el total de películas grabadas en un mes específico
df_movies["mes"] = df_movies["release_date"].dt.month

## Diccionario con todos los meses
meses = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12
}

## Decorador "post"
@app.get("/cantidad_filmaciones_mes/")
def cantidad_filmaciones_mes(mes: str):
    
    ## Convierto el mes a minúsculas para asegurar que puedan pasar varias formas de escritura
    mes = str(mes).lower()
    ## Verifico que el mes sea válido
    if mes not in meses:
        raise HTTPException(status_code=400, detail="Mes inválido. Por favor, escribir un mes válido.")
    
    ## Guardo el mes con el numero que le corresponde para verificar en pandas
    mes_num = meses[mes]
    ## Cuento el total de peliculas del mes requerido
    total_peliculas_mes = df_movies[df_movies["mes"] == mes_num].shape[0]
    
    ## Retorno en la FastAPI el total de películas por dicho mes pedido
    return {"mes": mes, "total_peliculas": total_peliculas_mes}


df_movies["dia_semana"] = df_movies["release_date"].dt.day_name()

dias = {
    "lunes": "Monday",
    "martes": "Tuesday",
    "miércoles": "Wednesday",
    "jueves": "Thursday",
    "viernes": "Friday",
    "sábado": "Saturday",
    "domingo": "Sunday"
}

@app.get("/cantidad_filmaciones_dia/")
def cantidad_filmaciones_dia(dia: str):
    dia = str(dia).lower()
    if dia not in dias:
        raise HTTPException(status_code=400, detail="Día inválido. Por favor, escribir un día válido")
    if dia == "miercoles":
        dia = "miércoles"
    if dia == "sabado":
        dia = "sábado"
    
    dia_ingles = dias[dia]

    total_peliculas_dia = df_movies[df_movies["dia_semana"] == dia_ingles].shape[0]

    return {"dia": dia, "total_peliculas": total_peliculas_dia}

    
@app.get("/score_titulo/")
def score_titulo(titulo: str):
    indice_pelicula = df_movies[df_movies["title"].str.lower() == titulo.lower()].index[0]
    pelicula = df_movies.loc[indice_pelicula, "title"]
    fecha_estreno = df_movies.loc[indice_pelicula, "release_date"]
    score = df_movies.loc[indice_pelicula, "popularity"]

    if pelicula == "":
        raise HTTPException(status_code=404, detail="Título no encontrado.")

    return {"La película": pelicula,
            "fue estrenada en el año": fecha_estreno.strftime("%Y-%m-%d"),
            "con un score/popularidad de": score}


@app.get("/votos_titulo/")
def votos_titulo(titulo: str):
    indice_pelicula = df_movies[df_movies["title"].str.lower() == titulo.lower()].index[0]
    pelicula = df_movies.loc[indice_pelicula, "title"]
    fecha_estreno = df_movies.loc[indice_pelicula, "release_date"]
    valoraciones = df_movies.loc[indice_pelicula, "vote_count"]
    valoraciones_promedio = df_movies.loc[indice_pelicula, "vote_average"]

    if valoraciones < 2000:
        return {"La pelicula": pelicula,
                "no cuenta con suficientes votos para valorarla correctamente": valoraciones}
    else:
        return {"La película": pelicula, 
                "fue estrenada en el año": fecha_estreno.strftime("%Y-%m-%d"), 
                "Tiene un total de valoraciones de": valoraciones, 
                "con un promedio de": valoraciones_promedio}
    

df_credits = pd.read_csv("credits.csv")

@app.get("/get_actor/")
def get_actor(nombre_actor: str):
    apariciones = 0
    retorno = 0
    promedio_retorno = 0
    for i, lista_casting in enumerate(df_credits["cast"]):
        if nombre_actor.lower() in str(lista_casting).lower():
            apariciones += 1
            retorno += df_movies["return"][i]
    promedio_retorno += retorno / apariciones

    return {"Actor": nombre_actor,
            "Total de películas que ha participado": apariciones,
            "Ha conseguido un retorno de": retorno,
            "Con un promedio por filmación de": promedio_retorno
            }


@app.get("/get_director/")
def get_director(nombre_director: str):
    retorno_total = 0
    retorno = []
    costo = []
    ganancia = []
    pelicula = []
    fecha = []

    
    for i, miembro_crew  in enumerate(df_credits["crew"]):
        if nombre_director.lower() in str(miembro_crew).lower():
            retorno_total += df_movies["return"][i]
            retorno.append(df_movies["return"][i])
            costo.append(df_movies["budget"][i])
            ganancia.append(df_movies["revenue"][i])
            pelicula.append(df_movies["title"][i])
            fecha.append(df_movies["release_date"][i].strftime("%Y-%m-%d"))

    peli_retor_cost_gananc_fecha =   [
        {"pelicula": p, "retorno": r, "costo": c, "ganancia": g, "fecha": f} 
        for p, r, c, g, f in zip(pelicula, retorno, costo, ganancia, fecha)
    ]
    

    return {"Director": nombre_director,
            "Ha conseguido un retorno total de": retorno_total,
            "Peliculas en las que ha trabajado": peli_retor_cost_gananc_fecha
            }