from conductor_electrical_resistance import *
from convection_heat_loss import *
from radiated_heat_loss import *
from solar_heat_gain import *


def steady_state_thermal_rating( q_c, q_r, q_s, R_T_avg ):
    '''
    Calcula la corriente que produce cierta temperatura del conductor bajo condiciones ambientales especificas.

    Args:
        q_c: tasa de perdida de calor por convección [W/m]
        q_r: tasa de pérdida de calor radiado por unidad de longitud [W/m]
        q_s: tasa de ganancia de calor del sol [W/m]
        R_T_avg: resistividad  del conductor a una temperatura T_avg [Ω/m]

    Returns:
        I: corriente del conductor [A]
    '''
    from math import sqrt
    try:
        I = sqrt( ( q_c + q_r - q_s ) / ( R_T_avg ) )
    except:
        I = 0
    return I

def ss_thermal_rating( V_w, phi, epsilon, alpha, T_a, T_max, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere:bool, year, month, day, hour, H_e ):
    '''
    Calcula la corriente que produce cierta temperatura del conductor bajo condiciones ambientales especificas.

    Args:
        V_w: velocidad del viento [m/s]
        phi: ángulo entre la dirección del viento y el eje axial del conductor [deg]
        epsilon: coeficiente de emisividad [adimensional]
        alpha: absorción solar [adimensional]
        T_a: temperatura ambiente [°C]
        T_max: Temperatura maxima del conductor [°C]
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

    Returns:
        I: corriente del conductor [A]
    '''
    # Convection heat loss
    q_c = convection_heat_loss( T_max, T_a, H_e, D_o, phi, V_w )
    # Radiated heat loss
    q_r = radiated_heat_loss( D_o, epsilon, T_max, T_a )
    # Solar heat gain
    q_s = solar_heat_gain( year, month, day, hour, H_e, lat, industrial_atmosphere, Z_l, D_o, alpha )
    # Resistance at T_avg
    R_T_avg = conductor_electrical_resistance( R_0, T_0, alpha_T, T_max )
    #  Steady-state thermal rating
    I = steady_state_thermal_rating( q_c, q_r, q_s, R_T_avg )
    return I

