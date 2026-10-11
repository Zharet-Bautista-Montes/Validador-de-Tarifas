# Bitácora de uso de IA en el Proyecto

**Herramienta elegida y uso:** El desarrollo en esta ocasión se ha apoyado en Claude, dadas sus capacidades para sugerir opciones de programación y su baja tendencia a errores en esta área. 

**Prompts destacables:**

- En el primer prompt usado en la conversación, se establece el rol, las características principales del proyecto, las tareas a completar y se consulta a Claude que información le falta para llevar a cabo tales tareas correctamente

```
En esta sesión, vas a ejercer el rol de asistente de desarrollo, el objetivo principal consiste en realizar ajustes en una versión inicial de un proyecto en Python con rutas API REST que simula el cálculo y registro de cobros en un sistema de transporte. Las tareas concretas son: transformar la función original de cálculo de cobro para incluir la medida de trasbordos; corregir un bug en la función de consulta; y habilitar la ejecución de la aplicación en Docker. Sólo vas a mostrar una propuesta de código cuando te lo solicite para una tarea concreta y, para cada vez, deberás explicar la justificación de cada cambio. Antes de empezar, deberás describir los aspectos del proyecto que necesitas saber para ofrecer respuestas adecuadas al contexto.
```

- Al llegar a este prompt, se indica detalladamente la regla de negocio para transbordos que se busca implementar, así como el lugar donde se agrega (antes de calcular descuento). 

```
Procedamos entonces a actualizar la función para calcular el cobro: inicialmente, se aplica la misma tarifa base en cada validación y luego un descuento según el perfil asociado a la tarjeta. En esta nueva versión, el manejo de transbordos se toma en cuenta por 90 minutos desde la validación inicial (viaje nuevo), que paga la tarifa base con descuento, y cualquier validación fuera de este lapso es "viaje nuevo" y paga este mismo valor; no obstante, si dentro de estos 90 minutos hay una primera nueva validación, sólo se paga por el transbordo $500 menos el descuento, y si hay una segunda validación, es transbordo gratis; no hay tercer transbordo, pues a partir de ahí vuelve a ser "viaje nuevo" y paga otra vez la tarifa base con descuento.
```

- En el prompt para abordar el bug en historial, se presenta la clase responsable de manejarlo, se describe el síntoma identificado previamente y se solicita el cambio requerido para llegar al resultado esperado. 

```
Ahora procedamos con la corrección del bug en consultas: el endpoint es http://localhost:8000/tarjetas/{tarjeta}/historial (donde {tarjeta} es el parámetro para filtrar los registros por la tarjeta indicada), pero he descubierto que al realizar la consulta no se filtran los registros, sino que se muestran todos los cobros de todas las tarjetas. A continuación, adjunto el código de la clase encargada de esta función, indica qué verificación hace falta y cómo se implementa.
```

- Por iniciativa propia, se solicitó a la IA en este nuevo prompt crear una clase independiente a cargo de la ejecución de verificaciones, donde se especifican las condiciones que se deben cumplir para responder con el código 422 (en lugar del 200 asignado por defecto). 

```
Atención, acabo de descubrir que no se ha implementado la verificación de datos para el endpoint POST /tarifas/calcular, por lo que vamos a desarrollar esta nueva tarea: éste debería devolver error 422 (en lugar de 200) si dentro del JSON incluido se tiene un perfil distinto a 'general', 'estudiante' o 'adulto_mayor'; si existen validaciones con el mismo validacion_id o si alguna fecha_hora no incluye la zona horaria (la falta "-05:00" o "Z"). Sugiero crear una clase independiente que realice estas validaciones y sea consultada desde la clase tarifas.py antes de proceder con el cálculo de tarifas, así que necesito una prouesta para esta nueva clase.
```

**Contrastación de propuesta de IA:** 

En un par de ocasiones, a las propuestas entregadas por la IA se les añadían más funciones de las solicitadas o se incluían características que no estaban planeadas al principio. Luego de preguntar por su propósito, algunas de estas fueron descartadas, otras fueron ajustadas al contexto del proyecto (coincidencia en nombres de variables, entre otros). Por ejemplo, para la función que llama a las verificaciones desde main.py, Claude colocó un async que no era necesario, de modo que se omitió.

Ahora bien, cuando la solución propuesta parece razonable, se revisa primero línea por línea para entender su operación, luego se implementa y se somete a prueba con datos específicos. En caso de una decisión que no se comprenda del todo, se le pregunta por esta decisión concreta y se le consultan o proponen otras alternativas, para elegir entre ellas la más práctica que logra el resultado. 

**Factor humano en el manejo de la IA:**

+ _Definición de objetivos:_ Establezco exactamente las tareas que se deben llevar a cabo y el resultado que se debe lograr para dirigir el funcionamiento de la IA. 
+ _Control de ingestión de datos:_ Solamente le suministro a la IA la información que requiere en el momento en que se necesita para que identifique correctamente qué y dónde buscar.
+ _Selección de resultados:_ Aunque la IA puede ofrecer como respuesta varias opciones y sugerencias adicionales, yo determino cuáles de estos componentes se pueden agregar finalmente al proyecto.
+ _Reconocimiento de errores:_ Establezco qué fallas en el proyecto pueden prescindir del uso de IA para su resolución, identifico inconsistencias en las propuestas entregadas por la IA y recurro a otras fuentes para contrastar características que no se comprenden completamente.