# Notas sobre el proyecto Validador de Tarifas

### 1. Estado del código heredado

Para empezar, el código heredado ya contaba con componentes iniciales importantes del proyecto: en particular, con el modelo definido de la estructura de datos para la creación de solicitudes y la recepción de respuestas, así como métodos básicos relacionados a las tarifas y al historial, algunas pruebas unitarias y archivos de configuración que permitieron, luego de la ejecución mediante las instrucciones dadas en el README, realizar pruebas iniciales. 

Sin embargo, además del bug reportado para los historiales, se identificaron errores puntuales en algunos de estos archivos de configuración (específicamente requirements.txt y Dockerfile), para los que se requirió una inspección concreta y un ajuste mínimo para lograr un funcionamiento esperado de las pruebas y del despliegue en Docker respectivamente. Se evitó realizar cambios sobre las demás partes del proyecto que no participaban en las tareas asignadas y funcionaban correctamente. 

Ahora bien, en cuanto al bug, este se puede replicar cuando se registran las validaciones de dos o más tarjetas, ya que al consultar, sin importar cuál es el valor de la tarjeta dentro del endpoint, se recuperaban los registros de todas las tarjetas (lo cual no se identificaba al guardar las validaciones de una sola tarjeta), y esto se debía a que el atributo "calculos" se manejaba como un atributo de la clase compartido por las instancias, en lugar de haber uno independiente en cada instancia. 

---

## 2. Casos borde manejados

- El principal caso borde manejado en la aplicación corresponde a validaciones que tienen una diferencia de 90 minutos exactamente, justo cuando termina la ventana donde se considera un transbordo: aquí se trata igual como transbordo; pero una vez ha superado los 90 minutos, en efecto se trata como un viaje nuevo. 
- Otro caso borde importante corresponde al historial donde, después de corregir el bug, se probó con distintos valores para tarjeta y, aunque estos variaran en un solo carácter, los registros correspondientes a cada una se trataron de manera independiente.
- Para el caso de una solicitud sin validaciones, se verificó que la respuesta incluyera la lista de cobros vacía y el total en cero.
- Para la consulta de validaciones de una tarjeta que no contaba con registros, se confirmó que devuelve una lista vacía. 

---

## 3. Supuestos aceptados

+ Las validaciones pueden llegar en cualquier orden. 
+ Los valores de id y estación de cada validación se aceptan tal y como se reciben. 
+ No hay restricciones en la fecha_hora asociada a cada validación, siempre que se trate de un valor real.
+ En ningún campo, sea de una consulta GET o de una solicitud POST, se esperan caracteres especiales. 
+ Cualquier solicitud al endpoint sigue el contrato indicado.
+ No se realiza manejo de carga de trabajo ni escalabilidad sobre la aplicación.
+ No se implementa autenticación de usuarios ni control de acceso.
+ La información no se almacena en una base de datos, se pierde con cada reinicio. 

---

## 4. Orden de prioridad en un escenario de producción

* La primera tarea a resolver sería el bug reportado por el cliente, tomando en cuenta que fue tipificado con prioridad alta y se ha identificado para él un tiempo de solución bajo. 
* Procederíamos luego a implementar la política de transbordos definida en la regla de negocio.
* A continuación, tendríamos los ajustes necesarios para el correcto despliegue en Docker.
* Después se elaborarían las verificaciones sobre el endpoint para los casos en donde se espera una respuesta 422. 
* Lo que seguiría es la elaboración de pruebas unitarias para revisar todos los desarrollos anteriores.
* Por último, se cerraría el proceso con la documentación de los cambios aplicados. 