from conductor_electrical_resistance import *
from convection_heat_loss import *
from radiated_heat_loss import *
from solar_heat_gain import *
from steady_state_thermal_rating import *


def steady_state_conductor_temperature( I_ss, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere:bool, year, month, day, hour, H_e,  es, imax ):
    '''
    Calcula la temperatura dada una corriente de estado estable las condiciones ambientales constantes.
        a) Se calcula la entrada de calor solar al conductor (es independiente de la temperatura del conductor).
        b) Se supone una temperatura de prueba del conductor.
        c) La resistencia del conductor se calcula para la temperatura de prueba.
        d) En combinación con las condiciones meteorológicas supuestas, se calculan los términos de calor por convección y radiación. 
        e) La corriente del conductor se calcula mediante el balance de calor en la Ecuación (1b) de 4.4.1.
        f) La corriente se compara con la corriente del conductor de prueba.
        g) La temperatura del conductor de prueba aumenta o disminuye hasta que la corriente calculada sea igual a la corriente de prueba dentro de una tolerancia especificada por el usuario.
    
    Args:
        I_ss: Corriente del conductor en estado estable
        V_w: velocidad del viento [m/s]
        phi: ángulo entre la dirección del viento y el eje axial del conductor [deg]
        epsilon: coeficiente de emisividad [adimensional]
        alpha: absorción solar [adimensional]
        T_a: temperatura ambiente [°C]
        D_o: diámetro exterior del conductor [m]
        R_0: Resistividad del conductor a una temperatura inicial T_0 [Ω/m] 
        T_0: temperatura inicial del conductor [°C]
        alpha_T: coeficiente de variación relativa de la resistencia debido a la temperatura [1/°C]
        Z_l: azimut del conductor [deg]
        lat: grados de latitud [deg]
        industrial_atmosphere: valor booleano que representa el ambiente industrial. Si es falso, se asume un ambiente claro.
        year: año para el cual se hace el calculo [AAAA]
        month: mes para el cual se hace el calculo [MM]
        day: dia para el cual se hace el calculo [DD]
        hour: hora del dia para el cual se hace el calculo en formato militar [hh]
        H_e: elevación del conductor sobre el nivel del mar [m]
        es: porcentaje máximo del error tolerado [0-100%]
        imax: numero máximo de iteraciones 

    Returns:
        T_avg: temperatura media del conductor [°C]
    '''
    # Solar heat gain
    q_s = solar_heat_gain( year, month, day, hour, H_e, lat, industrial_atmosphere, Z_l, D_o, alpha )
    print('q_s = ', q_s)
    # Selección del cambio fraccionario para solución numérica por el método de la secante modificado
    delta = 0.1
    T_i = T_a + 5 # Temperatura de prueba
    ea = 100 # El error porcentual relativo inicia como el 100%
    i = 0 # Se inicializa el numero de iteraciones en 0
    T_avg = None
    while True:
        i += 1
        T_i2 = T_i * ( 1 + delta )
        # Resistance at T_avg
        R_T_i = conductor_electrical_resistance( R_0, T_0, alpha_T, T_i )
        R_T_i2 = conductor_electrical_resistance( R_0, T_0, alpha_T, T_i2 )
        # Convection heat loss
        q_ci = convection_heat_loss( T_i, T_a, H_e, D_o, phi, V_w )
        q_ci2 = convection_heat_loss( T_i2, T_a, H_e, D_o, phi, V_w )
        # Radiated heat loss
        q_ri = radiated_heat_loss( D_o, epsilon, T_i, T_a )
        q_ri2 = radiated_heat_loss( D_o, epsilon, T_i2, T_a )
        # comparing calculated Steady-state thermal rating  vs Steady-state real value
        f_i = steady_state_thermal_rating( q_ci, q_ri, q_s, R_T_i ) - I_ss
        f_i2 = steady_state_thermal_rating( q_ci2, q_ri2, q_s, R_T_i2 ) - I_ss
        # Se guarda la temperatura  de prueba anterior
        T_iold = T_i
        # Se calcula el nuevo valor de la temperatura mediante el criterio del método de la secante
        if ( f_i2 - f_i ) != 0:
            T_i = T_i - ( ( delta * T_i * f_i ) / ( f_i2 - f_i ) ) 
        # Se calcula el error relativo del antiguo valor respecto del nuevo valor aproximado
        if T_i != 0:
            ea = abs( ( T_i - T_iold ) / T_i ) * 100
        # Se evalúa si el error relativo es inferior al error tolerado para terminar las iteraciones
        if ea <= es or i >= imax :
            T_avg = T_i
            print('Número de iteraciones: ', i)
            break
    return T_avg