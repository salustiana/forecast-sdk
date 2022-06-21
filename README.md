# Sibila

Sibila es una librería que permite realizar predicciones (forecasts) de manera sencilla, utilizando por detrás el servicio de Forecasting de AWS. 

### Instalación
```
python3 -m pip install boto3 && \
    python3 -m pip install --index-url http://pypi.ml.com/simple/ \
    --trusted-host pypi.ml.com sibila
```

### Requisitos
- Credenciales de AWS
- Dataset de entrenamiento

**Obtención de las credenciales:**

 1. Generar una nueva solicitud de acceso a AWS:
    
    1.  [Ingresar a SHIELD](https://shield.adminml.com/)
    
    2.  Crear una solicitud de tipo "AWS - Acceso vía Bastión"
    
		- Cuenta: 628956477585

		- Rol: CrossAccountManager-BI-Forecasting

		- Tipo de acceso: Permanente
		⚠️ **Atención:** Si no está en la lista de roles, seleccionar “NO ENCONTRE EL ROL EN LA LISTA” y escribir el nombre del rol el campo de texto del form de Shield)

  2. Seguir las [instrucciones](https://github.com/mercadolibre/fury_aws-bastion-cli-client/blob/master/README.md) de uso del cliente de **bastion** para generar credenciales temporarias

### Uso

Se puede encontrar un ejemplo de uso básico en esta [notebook](./docs/basic_example.ipynb), y más información específica sobre las entidades y métodos que ofrece la librería [aquí](./docs).
