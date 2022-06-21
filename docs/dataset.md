# Dataset
Dataset es la entidad que representa un dataset existente para nuestro proyecto. Los datasets son necesarios para entrenar [predictores](./predictor.md) que luego sirven para realizar predicciones.

### Instanciación

Los datasets se crean a partir de un archivo **csv** local a partir del método **Project.upload_dataset**:
```
mi_dataset = mi_proyecto.upload_dataset(
   local_path: str,
   ds_type: str,
   schema: dict,
   frequency: str,
   timestamp_format: str,
)
```
- **local_path**: la ruta local del archivo csv que contiene nuestro set de datos.
- **ds_type**: el tipo de dataset que estamos creando. Debe ser uno de los [siguientes](https://docs.aws.amazon.com/forecast/latest/dg/howitworks-datasets-groups.html#howitworks-dataset-domainstypes): "TARGET\_TIME\_SERIES", "RELATED\_TIME\_SERIES", "ITEM\_METADATA".
- **[schema](https://docs.aws.amazon.com/forecast/latest/dg/howitworks-datasets-groups.html#howitworks-dataset-schema)**: un diccionario que le proporciona a AWS información sobre el dataset que estamos creando.
- **frequency**: la frecuencia que tiene nuestro set de datos. Los intervalos válidos son "Y" (Year), "M" (Month), "W" (Week), "D" (Day), "H" (Hour), "30min" (30 minutes), "15min" (15 minutes), "10min" (10 minutes), "5min" (5 minutes), y "1min" (1 minute).
- **timestamp_format**: el formato de las fechas que contiene nuestro csv. Por ejemplo: "yyyy-MM-dd"

### Recuperar un dataset
Podemos recuperar un dataset existente en nuestro proyecto mediante el método **Project.get_dataset()**:

```
mi_dataset = mi_proyecto.get_dataset(
    ds_type: str
)
```
Para ver qué datasets hay disponibles en el proyecto, podemos usar el método **Project.datasets()**
```
mi_proyecto.datasets()
```

### Métodos
#### to\_csv(): 
Exporta el dataset que existe para nuestro proyecto a un csv.

```
mi_dataset.to_csv(
    destination: str
)
```
- **destination**: la ruta local donde queremos exportar el csv.
