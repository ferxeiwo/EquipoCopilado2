# EquipoCopilado2
#Diccionario de Datos Clave

#Customer_ID:
Es el identificador único de cada cliente. Lo usamos como llave principal para poder hacer el Left Join entre la información de ventas (SQL) y los perfiles de usuario (NoSQL/JSON). Sin este campo no podríamos saber qué cliente hizo qué compra ni enriquecer la tabla maestra.

Tipo: int
Ejemplo: 101, 873

id_transaccion: Identificador único de cada venta realizada. Lo usamos en la fase de limpieza para detectar y eliminar registros duplicados en el histórico de ventas.

Tipo: int
Ejemplo: 1045


#Timestamp
Son las fechas registradas en las distintas fuentes, pero el problema es que cada una las guardaba en un formato diferente. Por eso necesitamos normalizarlas.

Problema inicial: SQL traía 12/05/2023, el inventario 05-12-2023, y los logs 15/Jul/2023:08:32:10.

Solución: Convertimos todas a formato datetime64 usando Pandas para poder ordenarlas y analizarlas correctamente.


#Categorías
Son campos de texto que deberían tener un solo valor estándar, pero en los datos en crudo venían "sucios" y escritos de muchas formas.

Problema inicial: Aparecían como "México", "mx", "MEX", "Mexico".

Solución: Se estandarizó el texto convirtiendo todo a minúsculas y haciendo un mapeo para que todas queden como "mx".

Features Numéricas (Métricas)
Son las variables de valor que vienen de las distintas fuentes. Tienen escalas muy diferentes entre sí, lo cual es un problema para el modelo de PCA (una variable de 80,000 opacaría a una de 50). Para solucionarlo, les aplicamos escalado Min-Max para que todas queden en un rango de 0 a 1.

monto: Valor de la compra (de 50 a 5,000 MXN). Usado también para detectar outliers en los Boxplots.
gasto_mensual: Promedio de consumo del usuario (de 200 a 8,000 MXN).
puntos_lealtad: Puntuación del usuario en nuestro programa de recompensas (de 0 a 5,000).
edad: Edad del comprador (usada para reglas de negocio).
stock (inventario): Cantidad de productos disponibles. Esta variable traía datos nulos (NaN), por lo que aplicamos limpieza .dropna() para no afectar los cruces.

#Variables Creadas por el Pipeline (Insights)
Estas columnas no venían en los datos originales; nuestro ETL las creó para generar valor y facilitar la toma de decisiones.
segmento_cliente: Variable categórica creada mediante reglas de negocio (np.where).
Lógica: Si el cliente gastó más de $1,000 y tiene menos de 30 años, se etiqueta como "Premium Joven". El resto cae en "Estándar".
PCA1, PCA2, PCA3: Componentes principales generados mediante la reducción de dimensionalidad (Algoritmo PCA).

Explicación: Teníamos 20 variables de comportamiento distintas. El algoritmo de Machine Learning las comprimió en estas 3 columnas matemáticas, reteniendo la mayor cantidad de varianza posible para poder graficar los clusters de usuarios en un Scatter Plot de forma sencilla.


#Proyecto:
Proyecto Final
#Materia:
Programación para el Procesamiento de Datos
