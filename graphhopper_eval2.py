import urllib.parse
import requests

# URL del servicio de rutas
route_url = "https://graphhopper.com/api/1/route?"

# Reemplaza con tu API Key personal de Graphhopper
key = "82338bb5-cbd9-4790-8183-9169d95b1edc"


def geocoding(location, key):
    """Obtiene las coordenadas y nombre formateado de una ubicación."""
    while location == "":
        location = input("Por favor, ingrese una ubicación válida: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode(
     {"q": location, "limit": "1", "countrycode": "cl", "key": key}
     )

    reply = requests.get(url)
    json_data = reply.json()
    json_status = reply.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        new_loc = (
            f"{name}, {state}, {country}" if state else f"{name}, {country}"
        )
        print(
            f"Ubicación encontrada para Graphhopper: {new_loc} (Tipo: {value})"
        )
    else:
        lat, lng = "ERROR", "ERROR"
        new_loc = location
        if json_status != 200:
            print(
                f"Estado Geocoding: {json_status} - {json_data.get('message', '')}"
            )

    return json_status, lat, lng, new_loc


# Bucle principal del programa
while True:
    print("\n" + "=" * 60)
    loc1 = input(
        "Ingrese la ciudad de origen (o 's'/'salir' para terminar): "
    ).strip()
    if loc1.lower() in ["s", "salir"]:
        print("¡Programa finalizado! Hasta luego.")
        break

    loc2 = input(
        "Ingrese la ciudad de destino (o 's'/'salir' para terminar): "
    ).strip()
    if loc2.lower() in ["s", "salir"]:
        print("¡Programa finalizado! Hasta luego.")
        break

    print("\n--- Obteniendo coordenadas de origen ---")
    orig_status, orig_lat, orig_lng, orig_name = geocoding(loc1, key)
    print("\n--- Obteniendo coordenadas de destino ---")
    dest_status, dest_lat, dest_lng, dest_name = geocoding(loc2, key)

    if orig_status == 200 and dest_status == 200:
        params = (
            f"point={orig_lat},{orig_lng}"
            f"&point={dest_lat},{dest_lng}"
            f"&vehicle=car&locale=es&key={key}"
        )
        op_url = route_url + params

        response = requests.get(op_url)
        paths_data = response.json()
        if response.status_code == 200 and "paths" in paths_data:
            distancia_m = paths_data["paths"][0]["distance"]
            tiempo_ms = paths_data["paths"][0]["time"]
            distancia_km = distancia_m / 1000
            tiempo_min = tiempo_ms / 1000 / 60
            tiempo_hrs = tiempo_min / 60

            print("\n" + "=" * 60)
            print(f"Ruta desde {orig_name} hasta {dest_name}")
            print(f"Distancia total: {distancia_km:.2f} km")
            print(
                f"Tiempo estimado: {tiempo_min:.2f} minutos ({tiempo_hrs:.2f} horas)"
            )
            print("=" * 60)
            print("NARRATIVA DEL VIAJE (PASO A PASO):")
            print("-" * 60)

            instrucciones = paths_data["paths"][0]["instructions"]
            for idx, paso in enumerate(instrucciones, start=1):
                texto_paso = paso["text"]
                dist_paso = paso["distance"] / 1000
                print(f"{idx}. {texto_paso} ({dist_paso:.2f} km)")
            print("-" * 60)
        else:
            print("No se pudo calcular la ruta entre los puntos especificados.")
            if "message" in paths_data:
                print(f"Detalle del error: {paths_data['message']}")