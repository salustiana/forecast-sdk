# Predictor
Predictor es la entidad que representa un predictor existente para nuestro proyecto. Los predictores se entrenan a partir de [datasets](./dataset.md) y sirven para realizar predicciones.

### Instanciación

Los predictores se crean a partir del método **Project.train_new_predictor**:
```
mi_predictor = mi_proyecto.train_new_predictor(
    name: str,
    algorithm: str,
    horizon: int,
    frequency: str,
    featurizations: list = None,
    supplementary_features: list = None,
    backtest_windows: int = 1,
    window_offset: int = None,
    hpo: int = False,
    hpo_config: dict = None,
    training_parameters: dict = None,
)
```
- **name**: un nombre descriptivo para el predictor. Tener en cuenta que mediante éste nombre podremos recuperar un predictor ya entrenado.

- **algorithm**: el algoritmo de entrenamiento para el predictor. Debe ser uno de los [siguientes](https://docs.aws.amazon.com/forecast/latest/dg/aws-forecast-choosing-recipes.html): "ARIMA", "Deep\_AR\_Plus", "ETS", "NPTS", "Prophet", "CNN-QR" o "AUTO". Al especificar AUTO, el servicio elegirá el mejor algoritmo luego de haber entrenado con todos los posibles.

- **horizon**: representa qué tan a futuro (en unidades de la frecuencia especificada) puede predecir nuestro predictor respecto al último dato que haya en nuestro dataset al momento de realizar la predicción. Por ejemplo: si nuestra frecuencia es 'D', nuestro horizonte es 30, y subimos un **TARGET TIME SERIES** que termina el 20 de Abril, podremos predecir la demanda hasta el 30 de Mayo.

- **frequency**: representa la frecuencia de predicción a futuro que podrá hacer nuestro predictor, es decir: con una frecuencia diaria, nuestro predictor podrá decirnos qué demanda de item tendremos por cada día futuro. (la frecuencia especificada no puede ser mayor que la del **TARGET TIME SERIES** que hayamos subido a nuestro proyecto). Por ejemplo: "yyyy-MM-dd".

- **supplementary_features**: Describe una característica complementaria del dataset referente al clima y a los días festivos. Para usar el [pronóstico del clima](https://docs.aws.amazon.com/forecast/latest/dg/weather.html) tal como lo ofrece el servicio de Amazon, debe incluirse un atributo de geolocalización en el dataset. Además debe especificarse las zonas horarias requeridas. Por otra parte, la característica de [días festivos](https://docs.aws.amazon.com/forecast/latest/dg/holidays.html) se incorpora en el predictor de acuerdo al calendario de los países soportados por el servicio de Amazon Forecast, entre los que se encuentran: Argentina "AR", Brazil "BR", Colombia "CO" entre otros 63 más. Sin embargo, actualmente el servicio sólo está soportando la característica de días festivos. Por ejemplo:  supplementary_features: <blockquote> [{"Name": "holiday","Value": "AR"}]


- **featurizations**: 
<details>
  <summary>A list of dictionaries</summary>
<ul>
    A list of featurization (transformation) information for the fields of a dataset.
<li><em>(dict) --</em><p>Provides featurization (transformation) information for a dataset field. This object is part of the  FeaturizationConfig object.</p>
<p>For example:</p>
<blockquote>
<div><tt class="docutils literal"><span class="pre">{</span></tt><p><tt class="docutils literal"><span class="pre">"AttributeName":</span> <span class="pre">"demand",</span></tt></p>
<p><tt class="docutils literal"><span class="pre">FeaturizationPipeline</span> <span class="pre">[</span> <span class="pre">{</span></tt></p>
<p><tt class="docutils literal"><span class="pre">"FeaturizationMethodName":</span> <span class="pre">"filling",</span></tt></p>
<p><tt class="docutils literal"><span class="pre">"FeaturizationMethodParameters":</span> <span class="pre">{"aggregation":</span> <span class="pre">"avg",</span> <span class="pre">"backfill":</span> <span class="pre">"nan"}</span></tt></p>
<p><tt class="docutils literal"><span class="pre">}</span> <span class="pre">]</span></tt></p>
<p><tt class="docutils literal"><span class="pre">}</span></tt></p>
</div></blockquote>
<ul>
<li><strong>AttributeName</strong> <em>(string) --</em> <strong>[REQUIRED]</strong><p>The name of the schema attribute that specifies the data field to be featurized. Amazon Forecast supports the target field of the <tt class="docutils literal"><span class="pre">TARGET\_TIME\_SERIES</span></tt> and the <tt class="docutils literal"><span class="pre">RELATED\_TIME\_SERIES</span></tt> datasets. For example, for the <tt class="docutils literal"><span class="pre">RETAIL</span></tt> domain, the target is <tt class="docutils literal"><span class="pre">demand</span></tt> , and for the <tt class="docutils literal"><span class="pre">CUSTOM</span></tt> domain, the target is <tt class="docutils literal"><span class="pre">target\_value</span></tt> . For more information, see  howitworks-missing-values .</p>
</li>
<li><strong>FeaturizationPipeline</strong> <em>(list) --</em><p>An array of one <tt class="docutils literal"><span class="pre">FeaturizationMethod</span></tt> object that specifies the feature transformation method.</p>
<ul>
<li><em>(dict) --</em><p>Provides information about the method that featurizes (transforms) a dataset field. The method is part of the <tt class="docutils literal"><span class="pre">FeaturizationPipeline</span></tt> of the  Featurization object.</p>
<p>The following is an example of how you specify a <tt class="docutils literal"><span class="pre">FeaturizationMethod</span></tt> object.</p>
<blockquote>
<div><tt class="docutils literal"><span class="pre">{</span></tt><p><tt class="docutils literal"><span class="pre">"FeaturizationMethodName":</span> <span class="pre">"filling",</span></tt></p>
<p><tt class="docutils literal"><span class="pre">"FeaturizationMethodParameters":</span> <span class="pre">{"aggregation":</span> <span class="pre">"sum",</span> <span class="pre">"middlefill":</span> <span class="pre">"zero",</span> <span class="pre">"backfill":</span> <span class="pre">"zero"}</span></tt></p>
<p><tt class="docutils literal"><span class="pre">}</span></tt></p>
</div></blockquote>
<ul>
<li><strong>FeaturizationMethodName</strong> <em>(string) --</em> <strong>[REQUIRED]</strong><p>The name of the method. The "filling" method is the only supported method.</p>
</li>
<li><strong>FeaturizationMethodParameters</strong> <em>(dict) --</em><p>The method parameters (key-value pairs), which are a map of override parameters. Specify these parameters to override the default values. Related Time Series attributes do not accept aggregation parameters.</p>
<p>The following list shows the parameters and their valid values for the "filling" featurization method for a <strong>Target Time Series</strong> dataset. Bold signifies the default value.</p>
<ul>
<li><tt class="docutils literal"><span class="pre">aggregation</span></tt> : <strong>sum</strong> , <tt class="docutils literal"><span class="pre">avg</span></tt> , <tt class="docutils literal"><span class="pre">first</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
<li><tt class="docutils literal"><span class="pre">frontfill</span></tt> : <strong>none</strong></li>
<li><tt class="docutils literal"><span class="pre">middlefill</span></tt> : <strong>zero</strong> , <tt class="docutils literal"><span class="pre">nan</span></tt> (not a number), <tt class="docutils literal"><span class="pre">value</span></tt> , <tt class="docutils literal"><span class="pre">median</span></tt> , <tt class="docutils literal"><span class="pre">mean</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
<li><tt class="docutils literal"><span class="pre">backfill</span></tt> : <strong>zero</strong> , <tt class="docutils literal"><span class="pre">nan</span></tt> , <tt class="docutils literal"><span class="pre">value</span></tt> , <tt class="docutils literal"><span class="pre">median</span></tt> , <tt class="docutils literal"><span class="pre">mean</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
</ul>
<p>The following list shows the parameters and their valid values for a <strong>Related Time Series</strong> featurization method (there are no defaults):</p>
<ul>
<li><tt class="docutils literal"><span class="pre">middlefill</span></tt> : <tt class="docutils literal"><span class="pre">zero</span></tt> , <tt class="docutils literal"><span class="pre">value</span></tt> , <tt class="docutils literal"><span class="pre">median</span></tt> , <tt class="docutils literal"><span class="pre">mean</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
<li><tt class="docutils literal"><span class="pre">backfill</span></tt> : <tt class="docutils literal"><span class="pre">zero</span></tt> , <tt class="docutils literal"><span class="pre">value</span></tt> , <tt class="docutils literal"><span class="pre">median</span></tt> , <tt class="docutils literal"><span class="pre">mean</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
<li><tt class="docutils literal"><span class="pre">futurefill</span></tt> : <tt class="docutils literal"><span class="pre">zero</span></tt> , <tt class="docutils literal"><span class="pre">value</span></tt> , <tt class="docutils literal"><span class="pre">median</span></tt> , <tt class="docutils literal"><span class="pre">mean</span></tt> , <tt class="docutils literal"><span class="pre">min</span></tt> , <tt class="docutils literal"><span class="pre">max</span></tt></li>
</ul>
<p>To set a filling method to a specific value, set the fill parameter to <tt class="docutils literal"><span class="pre">value</span></tt> and define the value in a corresponding <tt class="docutils literal"><span class="pre">_value</span></tt> parameter. For example, to set backfilling to a value of 2, include the following: <tt class="docutils literal"><span class="pre">"backfill":</span> <span class="pre">"value"</span></tt> and <tt class="docutils literal"><span class="pre">"backfill_value":"2"</span></tt> .</p>
<ul>
<li><em>(string) --</em><ul>
<li><em>(string) --</em></li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>

</details>

- **backtest_windows**: La cantidad de veces que se separa la data para hacer backtests. El default es 1, y los valores válidos son del 1 al 5.

- **window_offset**: El punto final del dataset desde donde se quiere separar la data para realizar los tests en vez de entrenamiento. Se debe especificar el valor como el número de puntos de datos. El default es el valor del horizonte que se indicó anteriormente. Éste valor debe ser mayor o igual al horizonte de forecast y menor que la mitad de la cantidad de datos en el TARGET_TIME_SERIES.

- **hpo**: si realizar o no hyper-parameter optimization.

- **hpo_config**: 
<details>
    <summary>Un diccionario</summary>
    <li>(<em>dict</em>) -- <p>Provides hyperparameter override values for the algorithm. If you don't provide this parameter, Amazon Forecast uses default values. The individual algorithms specify which hyperparameters support hyperparameter optimization (HPO). For more information, see  aws-forecast-choosing-recipes .</p>
        <blockquote>
{
            
        'ParameterRanges': {
            
            'CategoricalParameterRanges': [
            
                {
            
                    'Name': 'string',
            
                    'Values': [
            
                        'string',
            
                    ]
            
                },
            
            ],
            
            'ContinuousParameterRanges': [
            
                {
            
                    'Name': 'string',
            
                    'MaxValue': 123.0,
            
                    'MinValue': 123.0,
            
                    'ScalingType': 
            'Auto'|'Linear'|'Logarithmic'|'ReverseLogarithmic'
            
                },
            
            ],
            
            'IntegerParameterRanges': [
            
                {
            
                    'Name': 'string',
            
                    'MaxValue': 123,
            
                    'MinValue': 123,
            
                    'ScalingType': 
            'Auto'|'Linear'|'Logarithmic'|'ReverseLogarithmic'
            
                },
            
            ]
            
        }
            
    },
</div></blockquote>
<p>If you included the <tt class="docutils literal"><span class="pre">HPOConfig</span></tt> object, you must set <tt class="docutils literal"><span class="pre">PerformHPO</span></tt> to true.</p>
<ul>
<li><strong>ParameterRanges</strong> <em>(dict) --</em><p>Specifies the ranges of valid values for the hyperparameters.</p>
<ul>
<li><strong>CategoricalParameterRanges</strong> <em>(list) --</em><p>Specifies the tunable range for each categorical hyperparameter.</p>
<ul>
<li><em>(dict) --</em><p>Specifies a categorical hyperparameter and it's range of tunable values. This object is part of the  ParameterRanges object.</p>
<ul>
<li><strong>Name</strong> <em>(string) --</em> <strong>[REQUIRED]</strong><p>The name of the categorical hyperparameter to tune.</p>
</li>
<li><strong>Values</strong> <em>(list) --</em> <strong>[REQUIRED]</strong><p>A list of the tunable categories for the hyperparameter.</p>
<ul>
<li><em>(string) --</em></li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
<li><strong>ContinuousParameterRanges</strong> <em>(list) --</em><p>Specifies the tunable range for each continuous hyperparameter.</p>
<ul>
<li><em>(dict) --</em><p>Specifies a continuous hyperparameter and it's range of tunable values. This object is part of the  ParameterRanges object.</p>
<ul>
<li><strong>Name</strong> <em>(string) --</em> <strong>[REQUIRED]</strong><p>The name of the hyperparameter to tune.</p>
</li>
<li><strong>MaxValue</strong> <em>(float) --</em> <strong>[REQUIRED]</strong><p>The maximum tunable value of the hyperparameter.</p>
</li>
<li><strong>MinValue</strong> <em>(float) --</em> <strong>[REQUIRED]</strong><p>The minimum tunable value of the hyperparameter.</p>
</li>
<li><strong>ScalingType</strong> <em>(string) --</em><p>The scale that hyperparameter tuning uses to search the hyperparameter range. Valid values:</p>
<blockquote>
<div>Auto</div></blockquote>
<p>Amazon Forecast hyperparameter tuning chooses the best scale for the hyperparameter.</p>
<blockquote>
<div>Linear</div></blockquote>
<p>Hyperparameter tuning searches the values in the hyperparameter range by using a linear scale.</p>
<blockquote>
<div>Logarithmic</div></blockquote>
<p>Hyperparameter tuning searches the values in the hyperparameter range by using a logarithmic scale.</p>
<p>Logarithmic scaling works only for ranges that have values greater than 0.</p>
<blockquote>
<div>ReverseLogarithmic</div></blockquote>
<p>hyperparameter tuning searches the values in the hyperparameter range by using a reverse logarithmic scale.</p>
<p>Reverse logarithmic scaling works only for ranges that are entirely within the range 0 &lt;= x &lt; 1.0.</p>
<p>For information about choosing a hyperparameter scale, see <a class="reference external" href="http://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-ranges.html#scaling-type">Hyperparameter Scaling</a> . One of the following values:</p>
</li>
</ul>
</li>
</ul>
</li>
<li><strong>IntegerParameterRanges</strong> <em>(list) --</em><p>Specifies the tunable range for each integer hyperparameter.</p>
<ul>
<li><em>(dict) --</em><p>Specifies an integer hyperparameter and it's range of tunable values. This object is part of the  ParameterRanges object.</p>
<ul>
<li><strong>Name</strong> <em>(string) --</em> <strong>[REQUIRED]</strong><p>The name of the hyperparameter to tune.</p>
</li>
<li><strong>MaxValue</strong> <em>(integer) --</em> <strong>[REQUIRED]</strong><p>The maximum tunable value of the hyperparameter.</p>
</li>
<li><strong>MinValue</strong> <em>(integer) --</em> <strong>[REQUIRED]</strong><p>The minimum tunable value of the hyperparameter.</p>
</li>
<li><strong>ScalingType</strong> <em>(string) --</em><p>The scale that hyperparameter tuning uses to search the hyperparameter range. Valid values:</p>
<blockquote>
<div>Auto</div></blockquote>
<p>Amazon Forecast hyperparameter tuning chooses the best scale for the hyperparameter.</p>
<blockquote>
<div>Linear</div></blockquote>
<p>Hyperparameter tuning searches the values in the hyperparameter range by using a linear scale.</p>
<blockquote>
<div>Logarithmic</div></blockquote>
<p>Hyperparameter tuning searches the values in the hyperparameter range by using a logarithmic scale.</p>
<p>Logarithmic scaling works only for ranges that have values greater than 0.</p>
<blockquote>
<div>ReverseLogarithmic</div></blockquote>
<p>Not supported for <tt class="docutils literal"><span class="pre">IntegerParameterRange</span></tt> .</p>
<p>Reverse logarithmic scaling works only for ranges that are entirely within the range 0 &lt;= x &lt; 1.0.</p>
<p>For information about choosing a hyperparameter scale, see <a class="reference external" href="http://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-ranges.html#scaling-type">Hyperparameter Scaling</a> . One of the following values:</p>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
    </details>
    
- **training_parameters**: Los hiperparámetros a sobreescribir para el entrenamiento del modelo (predictor). Los hiperparámetros que se pueden sobreescribir están en la [documentación](https://docs.aws.amazon.com/forecast/latest/dg/aws-forecast-choosing-recipes.html) de cada algoritmo por separado.The hyperparameters to override for model training.

### Recuperar un predictor
Podemos recuperar un predictor existente en nuestro proyecto mediante el método **Project.get_predictor()**:

```
mi_predictor = mi_proyecto.get_predictor(
    name: str
)
```
Para ver qué predictores hay disponibles en el proyecto, podemos usar el método **Project.predictors()**
```
mi_proyecto.predictors()
```

### Métodos

#### metrics():
Exporta dos archivos csv conteniendo métricas de entrenamiento a un directorio especificado:
   - **backtest_forecasts.csv**: contiene las predicciones realizadas sobre las ventanas de entrenamiento y los valores reales que contenía el dataset para poder realizar una comparación manual.
   - **backtest_metrics.csv**: contiene métricas de precisión durante el entrenamiento, incluído el error cuadrático medio entre otros.
    
```
mi_predictor.metrics(destination_dir: str)
```

  - **destination**: el directorio a donde exportar los csv. Puede o no existir. (si existen el directorio y los archivos con los mismos nombres, serán sobreescritos).


#### forecast(): 
Realiza una predicción a futuro y exporta los resultados a un archivo csv local.

```
mi_predictor.forecast(
    destination_path: str,
    quantiles: list = None,
)
```
- **destination_path**: la ruta a dónde exportar el csv conteniendo las predicciones.

- **quantiles**: Los cuantiles en los que se generan los pronósticos probabilísticos. Se pueden especificar hasta 5 cuantiles por pronóstico. Los valores aceptados incluyen 0.01 a 0.99 (incrementos de 0.01 solamente) y la media. El pronóstico medio es diferente de la mediana (0,50) cuando la distribución no es simétrica (por ejemplo, Beta y Binomial negativo). El valor predeterminado es \["0.1", "0.5", "0.9"\].
