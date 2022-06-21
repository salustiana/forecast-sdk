# Project
Project es la entidad que nos permite interactuar con el servicio. Representa un proyecto específico en el cual estamos trabajando (por ejemplo la predicción de demanda de un producto en particular), e instancia los clientes para la interacción con el servicio de AWS. Es por eso que la librería recibe las credenciales de AWS por medio de ésta entidad.

### Instanciación
```   
mi_proyecto = Project(
    name: str,
    team: str,
    username: str,
    password: str,
    aws_access_key_id: str = entorno_bastion,
    aws_secret_access_key: str = entorno_bastion,
    aws_session_token: str = entorno_bastion,
    region_name: str = "us-east-1",
)
```

- **name**: un nombre descriptivo del proyecto en el cual estamos trabajando. Tener en cuenta que mediante éste nombre podremos recuperar un proyecto en el cual trabajamos antes. Por ejemplo: "demanda\_zapatillas".
- **team**: el nombre del equipo al cual pertenecemos dentro de mercadolibre. Es importante ser consistente con el nombre de equipo ya que también se utiliza para identificar los proyectos y poder recuperarlos. Ejemplo: "bi-ml-cross".
- **username**: el usuario LDAP de quien esté utilizando la librería.
- **password**: el password correspondiente a ese usuario.
- **credenciales**: todas las credenciales que genera bastión. Si estamos trabajando en un shell generado por bastión, **sibila** levanta automáticamente éstas variables del entorno y no es necesario especificarlas.
- **region_name**: la región en la cual nuestra cuenta de AWS está hosteada. Por defecto "us-east-1".

### Métodos

#### Métodos que devuelven [Datasets](./dataset.md)

#### upload\_dataset()

```
mi_proyecto.upload_dataset(
   local_path: str,
   ds_type: str,
   schema: dict,
   frequency: str,
   timestamp_format: str,
)
```
La información detallada sobre cómo crear un dataset se encuentra en [Datasets](./dataset.md)
#### get\_dataset()

```
mi_proyecto.get_dataset(
    ds_type: str
)
```
#### Métodos que devuelven [Predictors](./predictor.md)

#### train\_new\_predictor()

```
mi_proyecto.train_new_predictor(
    name: str,
    algorithm: str,
    horizon: int,
    frequency: str,
    supplementary_features: list = None,
    featurizations: list = None,
    backtest_windows: int = 1,
    window_offset: int = None,
    hpo: int = False,
    hpo_config: dict = None,
    training_parameters: dict = None,
    )
```
La información detallada sobre cómo crear un predictor se encuentra en [Predictors](./predictor.md)

#### get\_predictor()

```
mi_proyecto.get_predictor(
    name: str
)
```

#### Métodos informativos

#### datasets()
#### predictors()

```
mi_proyecto.datasets()
mi_proyecto.predictors()
```
Devuelven una lista de datasets y predictores que existen para el proyecto respectivamente.
