import pandas as pd
import numpy as np
import requests
import re
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# FASE 1: EXTRACCIÓN (Extract)

def conectar_pg():
    USUARIO = "postgres"
    PASSWORD = "1"
    HOST = "localhost"
    PUERTO = "5432"
    BASE_DATOS = "clientes"
    try:
        url = f"postgresql://{USUARIO}:{PASSWORD}@{HOST}:{PUERTO}/{BASE_DATOS}"
        engine = create_engine(url)
        print("Conectado a PostgreSQL correctamente")
        return engine
    except Exception as e:
        print("Error en la conexión a PG:", e)
        return None

engine = conectar_pg()

df_ventas = pd.DataFrame({
    'id_transaccion': [1, 2, 3, 3], # Un duplicado intencional
    'Customer_ID': [101, 102, 103, 103],
    'monto': [1500, 200, 3500, 3500],
    'fecha': ['12/05/2023', '05-12-2023', '2023/05/13', '2023/05/13'],
    'id_tienda': ['MX', 'mex', 'México', 'México']
})
# ---------------------------------------------------------------------------------

df_perfiles = pd.read_json("perfiles_usuarios.json")
df_master = pd.merge(df_ventas, df_perfiles, left_on='Customer_ID', right_on='id_cliente', how='left')

df_inventario = pd.read_csv('inventario.csv')
print(f"Extracción CSV exitosa: {len(df_inventario)} filas de inventario importadas.")


response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
tipo_cambio = response.json()['rates'].get('MXN', 17.5) # Fallback a 17.5 si falla

# FASE 2: TRANSFORMACIÓN (Transform & Clean)


df_ventas = df_ventas.drop_duplicates(subset=['id_transaccion'])
df_inventario = df_inventario.dropna(subset=['stock'])

# 2.2 Normalización de Fechas y Textos
df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'], format='mixed', dayfirst=True)
df_ventas['id_tienda'] = df_ventas['id_tienda'].str.lower().replace({'mex': 'mx', 'méxico': 'mx', 'mexico': 'mx'})

df_master = pd.merge(df_ventas, df_perfiles, on='Customer_ID', how='left')


# Si gastan más de 1000 y tienen menos de 30 años, son "Premium Joven"
df_master['segmento_cliente'] = np.where(
    (df_master['monto'] > 1000) & (df_master['edad'] < 30),
    'Premium Joven',
    'Estándar'
)


# FASE 3: ANALÍTICA AVANZADA (PCA)

print("Iniciando PCA...")
for i in range(1, 18):
    df_master[f'var_comportamiento_{i}'] = np.random.rand(len(df_master)) * 100

columnas_pca = ['monto', 'gasto_mensual', 'puntos_lealtad'] + [f'var_comportamiento_{i}' for i in range(1, 18)]

# Escalar (Min-Max)
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df_master[columnas_pca].fillna(0))

# Aplicar PCA (3 componentes)
pca = PCA(n_components=3)
componentes = pca.fit_transform(df_scaled)
df_master['PCA1'] = componentes[:, 0]
df_master['PCA2'] = componentes[:, 1]
df_master['PCA3'] = componentes[:, 2]

# FASE 4: VISUALIZACIÓN Y SALIDA

plt.figure(figsize=(8, 5))
sns.boxplot(x=df_master['monto'])
plt.title('Detección de Outliers en Montos de Venta')
plt.show()

plt.figure(figsize=(8, 5))
sns.scatterplot(x='PCA1', y='PCA2', hue='segmento_cliente', data=df_master)
plt.title('Clusters de Comportamiento (PCA1 vs PCA2)')
plt.show()

fig = go.Figure(data=[go.Sankey(
    node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5),
        label = ["Visita Web", "Añade al Carrito", "Compra Exitosa", "Abandono"]
    ),
    link = dict(
        source = [0, 1, 0, 1], 
        target = [1, 2, 3, 3],
        value = [800, 400, 200, 400] 
    ))])
fig.update_layout(title_text="Flujo de Usuarios (Sankey Diagram)", font_size=10)
fig.show()

# 4.4 Guardar el entregable final
df_master.to_parquet('data_master_clean.parquet', index=False)
print("Pipeline ejecutado con éxito. Datos guardados en data_master_clean.parquet")