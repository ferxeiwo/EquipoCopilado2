from sqlalchemy import create_engine

USUARIO = "postgres"
PASSWORD = "1"
HOST = "localhost"
PUERTO = "5432"
BASE_DATOS = "clientes"

def conectar():
    try:
        url = f"postgresql://{USUARIO}:{PASSWORD}@{HOST}:{PUERTO}/{BASE_DATOS}"
        engine = create_engine(url)

        print("Conectado correctamente")
        return engine

    except Exception as e:
        print("Error en la conexión:", e)
        return None


conectar()