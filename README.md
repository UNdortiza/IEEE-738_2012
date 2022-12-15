# IEEE-738_2012

En este repositorio incluye una serie de funciones para calcular la temperatura o la corriente en conductores aéreos desnudos, usando modelos que relacionan estas dos magnitudes, en función de las propiedades del conductor y las condiciones ambientales, basado en las relaciones establecidas en el estándar IEEE-738 en su version del 2012. Al igual que en dicho documento, se incluyen funciones para realizar cálculos de equilibrio térmico en estado estable y también para cuando se tienen variaciones de corriente  o/y condiciones ambientales. El NoteBook deJupyter [pruebas.ipynb](./src/pruebas.ipynb) contiene ejemplos de implementación de las diferentes funciones.

## Marco teórico

### Cálculo para equilibrio de calor en estado estable

Para este caso se consideran constantes todos los parámetros ambientales y la corriente en el conductor, de los cuales depende la temperatura de equilibrio a la que llega en dichas condiciones, como se muestra en la siguiente ecuación:

$$
    q_c + q_r = q_s + I^2 \, R(T_c)
$$

Donde $q_c$ representa las perdidas de calor por convección,  $q_r$ las perdidas de calor por radiación,  $q_s$ la ganancia de calor por radiación solar,  $I$ la corriente en el conductor y $R(T_c)$ la resistencia del conductor a una temperatura $T_c$.

### Cálculo de temperatura con cambios de corriente

Para este caso se consideran constantes las condiciones ambientales, asumiendo una variación discreta en el cambio de la corriente y temperatura. El intervalo de variación debe ser lo suficientemente pequeño, de tal manera que todo el calor generado se mantiene dentro del conductor. El modelo de dicho comportamiento dinámico se muestra en la siguiente ecuación.

$$
    \frac{dT_{avg}}{dt} = \frac{R(T_{avg}) \, I^2 + q_s - q_c - q_r}{m \, C_p}
$$

donde $\frac{dT_{avg}}{dt}$ es la razón de cambio de la temperatura respecto del tiempo, $m$ es la masa por unidad de longitud y $C_p$ es el calor especifico del material. El producto de los dos últimos es conocido como la capacidad calorífica del material.

### Perdidas de calor por convección

La transferencia  de calor por convección de un cuerpo hacia un fluido  puede darse de manera forzada o natural, dependiendo de la velocidad y naturaleza del movimiento del fluido.

###### Convección forzada
Se usan dos modelos para su cálculo: para velocidades bajas ($<50Km/h$) se implementa la ecuación 

$$
    q_{c1} = K_{angle}\,(1.01 + 1.35 \, N_{Re}^{0.52})\, k_f \, (T_s - T_a)
$$

y para velocidades altas ($>50Km/h$) la ecuación 

$$
    q_{c2} = K_{angle}\, 0.754 \, N_{Re}^{0.6}\, k_f \, (T_s - T_a)
$$

En cualquiera de los casos, las perdidas por convección forzada es función de la conductividad térmica del aire ($k_f$), la temperatura superficial del conductor ($T_s$), la temperatura en el ambiente ($T_a$), el factor de dirección del viento ($K_{angle}$) y el número de Reynolds ($N_{re}$). El factor de dirección del viento, a su vez, es un valor dependiente del ángulo que forma el eje axial del conductor y la dirección del viento ($\phi$) y su valor está definido por el modelo de la ecuación

$$
    K_{angle} = 1.194 - \cos{(\phi)} + 0.194\cos{(2\phi)} + 0.368\sin{(2\phi)}
$$

mientras que el número de Reynolds depende del diámetro externo del conductor ($D_0$), la densidad ($\rho_f$) y viscosidad dinámica ($\mu_f$) del aire y la velocidad del viento ($V_w$).

$$
    N_{Re} = \frac{D_0\,\rho_f \, V_w}{\mu_f}
$$

###### Convección natural
Para lugares en donde la velocidad del viento es mínima, se aplica la relación de la siguiente ecuación para calcular las perdidas por convección natural.

$$
    q_{cn} = 3.645 \, \rho_f^{0.5} \, D_0^{0.75} \, (T_s-T_a)^{1.25}
$$

### Pérdidas de calor por radiación
La transferencia de calor del conductor al ambiente depende en primer lugar de la diferencia de temperatura del conductor ($T_s$) y  la temperatura del ambiente ($T_a$). También depende del estado de limpieza de la superficie del conductor, que se representa mediante el factor de emisividad ($\epsilon$), y por supuesto del diámetro del conductor ($D_0$).

$$
    q_r = 17.8 \, D_0 \, \epsilon \left[ \left(\frac{T_s + 273}{100}\right)^4 - \left(\frac{T_a + 273}{100}\right)^4 \right]
$$

### Ganancia de calor por radiación solar
La ganancia de energía en forma de calor proveniente de la radiación solar depende de un coeficiente de absorción solar ($\beta$), el ángulo efectivo de incidencia de los rayos solares ($\theta$), un factor de corrección ($Q_{se}$) y el área efectiva proyectada del conductor ($A'$).

$$
    q_s = \beta \, Q_{se} \, \sin{(\theta)} \, A'
$$

Los parámetros de los cuales depende la ganancia de calor por radiación solar se pueden obtener mediante el cálculo en función de otros parámetros, o bien de tablas características que dependen de condiciones del conductor y condiciones ambientales.

## Lista de funciones

-   **transient_conductor_temperature:** calcula valores incrementales de temperatura respecto del tiempo en intervalos igualmente espaciados, debido a un incremento repentino en la corriente del conductor, mientras las condiciones ambientales permanecen constantes.
-   **transient_settling_time:** Calcula valores incrementales de temperatura respecto del tiempo en intervalos igualmente espaciados, debido a un incremento repentino en la corriente del conductor, mientras las condiciones ambientales permanecen constantes.
-   **steady_state_thermal_rating:** Calcula la corriente que produce cierta temperatura del conductor bajo condiciones ambientales específicas. En el mismo módulo se encuentra otra función que calcula la misma corriente recibiendo los parámetros ambientales y físicos del conductor.
-   **steady_state_conductor_temperature:** Calcula la temperatura dada una corriente de estado estable, considerando las condiciones ambientales constantes.
-   **convection_heat_loss:** calcula la perdida de calor por convección como el valor mayor entre las perdidas de calor por convección forzada y convección natural. El módulo también contiene funciones auxiliares para efectuar cálculos ambientales.
-   **radiated_heat_loss:** Calcula la tasa de pérdida de calor radiado por unidad de longitud.
-   **solar_heat_gain:** Calcula la ganancia de calor debida a la radiación del sol.
-   **conductor_electrical_resistance:** Calcula la resistencia eléctrica por unidad de longitud en función del incremental de temperatura y sus propiedades físicas y eléctricas.