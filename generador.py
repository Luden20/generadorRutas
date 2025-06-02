import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import requests
import json
import os
def generateUrl(lugar1,lugar2,token):
    return f'https://api.mapbox.com/directions/v5/mapbox/driving/{lugar1["longitud"]},{lugar1["latitud"]};{lugar2["longitud"]},{lugar2["latitud"]}?geometries=geojson&access_token={token}'
def main():
    load_dotenv()
    cred = credentials.Certificate("credenciales.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    token = os.getenv("MAPBOX_TOKEN")  
    docs_maps = db.collection('maps').stream()
    #DE MOMENTO BORRO LAS RUTAS PARA NO TENER REPETIDOS
    docs_routes = db.collection("routes").stream()
    for doc in docs_routes:
        doc.reference.delete()

    lugares=[]
    for doc in docs_maps:
        lugares.append({
            "id":doc.id,
            "latitud":doc.to_dict()["latitud"],
            "longitud":doc.to_dict()["longitud"]
        })
    rutas={}
    for i in range(len(lugares)):
        if lugares[i]["id"] not in rutas:
            rutas[lugares[i]["id"]]={}
        for j in range(len(lugares)):
            if i==j:
                continue
            url=generateUrl(lugares[i],lugares[j],token)
            res=requests.request("GET",url)
            data=res.json()
            data=data["routes"][0]
            aux={
                "salidaId":lugares[i]["id"],
                "llegadaId":lugares[j]["id"],
                "duracion":data["duration"],
                "distancia":data["distance"],
                "ruta": [{"lon": p[0], "lat": p[1]} for p in data["geometry"]["coordinates"]]
            }
            rutas[lugares[i]["id"]][lugares[j]["id"]]=aux
            doc_ref = db.collection("routes").document()
            doc_ref.set(aux)
main()