from steady_state_conductor_temperature import *

def transient_conductor_temperature( I_i, I_f, dt, time, mC_p, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere:bool, year, month, day, hour, H_e, es, imax ):
    '''
    Calcula valores incrementales de temperatura respecto del tiempo en intervalos igualmente espaciados, debido a un incremento repentino en la corriente del conductor, mientras las condiciones ambientales permanecen constantes.

    Args:
        I_i: corriente inicial en el conductor antes de su incremento repentino [A]
        I_f: corriente final en el conductor [A]
        dt: variación discreta de tiempo con la cual se realiza la evaluación iterativa de cambios de temperatura. [segundos]
        time: tiempo transcurrido después del cambio de corriente en el conductor [segundos]
        mC_p: Capacidad calorífica total del conductor [J/(m-°C)]
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
        T: lista con valores de temperatura en el conductor, calculados en valores incrementales 'dt' durante un tiempo 'time' [°C]
    '''
    from numpy import trunc
    # Antes del cambio de corriente en el conductor, se presentan las siguientes condiciones en estado estable
    T_i = steady_state_conductor_temperature( I_i, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere, year, month, day, hour, H_e,  es, imax )
    q_s = solar_heat_gain( year, month, day, hour, H_e, lat, industrial_atmosphere, Z_l, D_o, alpha )
    # Crea la lista en donde se guardara las temperaturas calculadas 
    T = [ T_i ]
    # Calcula el numero de intervalos a evaluar
    n = int(trunc( time / dt ))
    nt = [ dt ] * n
    for delta_t in nt:
        # En cada iteración se calculan los valores dependientes de la temperatura
        R_T_i = conductor_electrical_resistance( R_0, T_0, alpha_T, T[-1] )
        q_c_i = convection_heat_loss( T[-1], T_a, H_e, D_o, phi, V_w )
        q_r_i = radiated_heat_loss(D_o, epsilon, T[-1], T_a )
        # Calcula la variación de la temperatura después del intervalo de tiempo
        dT = delta_T( R_T_i, I_f, q_s, q_c_i, q_r_i, mC_p, delta_t )
        # Se agrega el valor de la temperatura después del intervalo
        T.append( T[-1] + dT )
    return T

def transient_settling_time( I_i, I_f, dT, mC_p, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere:bool, year, month, day, hour, H_e, es, imax ):
    '''
    Calcula valores incrementales de temperatura respecto del tiempo en intervalos igualmente espaciados, debido a un incremento repentino en la corriente del conductor, mientras las condiciones ambientales permanecen constantes.

    Args:
        I_i: corriente inicial en el conductor antes de su incremento repentino [A]
        I_f: corriente final en el conductor [A]
        dT: variación discreta de temperatura con la cual se realiza la evaluación iterativa de cambios de temperatura. [°C]
        mC_p: Capacidad calorífica total del conductor [J/(m-°C)]
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
        Time: tiempo de establecimiento de temperatura transcurrido después del cambio de corriente en el conductor [segundos]
    '''
    # Antes del cambio de corriente en el conductor, se presentan las siguientes condiciones en estado estable
    T_i = steady_state_conductor_temperature( I_i, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere, year, month, day, hour, H_e,  es, imax )
    T_f = steady_state_conductor_temperature( I_f, V_w, phi, epsilon, alpha, T_a, D_o, R_0, T_0, alpha_T, Z_l, lat, industrial_atmosphere, year, month, day, hour, H_e,  es, imax )
    q_s = solar_heat_gain( year, month, day, hour, H_e, lat, industrial_atmosphere, Z_l, D_o, alpha )
    Time = 0
    T = T_i
    while T <= T_f :
        # En cada iteración se calculan los valores dependientes de la temperatura
        R_T_i = conductor_electrical_resistance( R_0, T_0, alpha_T, T )
        q_c_i = convection_heat_loss( T, T_a, H_e, D_o, phi, V_w )
        q_r_i = radiated_heat_loss(D_o, epsilon, T, T_a )
        # Calcula la variación de la temperatura después del intervalo de tiempo
        dt = delta_t( R_T_i, I_f, q_s, q_c_i, q_r_i, mC_p, dT )
        # Se actualiza el valor de temperatura y tiempo
        T += dT
        Time += dt
    return Time

def delta_T(R_T_avg, I, q_s, q_c, q_r, mC_p, dt ):
    '''
    Calcula el incremento de temperatura en un conductor luego de un cambio repentino en la corriente en el mismo.

    Args:
        R_T_avg: Resistencia eléctrica del conductor a la temperatura antes del incremento en la corriente [Ω/m] 
        I: corriente final en el conductor [A]
        q_s: tasa de ganancia de calor del sol [W/m]
        q_c: tasa de perdida de calor por convección [W/m]
        q_r: tasa de pérdida de calor radiado por unidad de longitud [W/m]
        mC_p: Capacidad calorífica total del conductor [J/(m-°C)]
        dt: variación discreta de tiempo [segundos]

    Returns:
        dT: incremento de temperatura en el conductor [°C]
    '''
    dT = ( ( R_T_avg * I**2 + q_s -q_c - q_r ) / ( mC_p ) ) * ( dt )
    return dT


def delta_t(R_T_avg, I, q_s, q_c, q_r, mC_p, dT ):
    '''
    Calcula el incremento de tiempo en un conductor luego de un cambio repentino en la corriente y temperatura.

    Args:
        R_T_avg: Resistencia eléctrica del conductor a la temperatura antes del incremento en la corriente [Ω/m] 
        I: corriente final en el conductor [A]
        q_s: tasa de ganancia de calor del sol [W/m]
        q_c: tasa de perdida de calor por convección [W/m]
        q_r: tasa de pérdida de calor radiado por unidad de longitud [W/m]
        mC_p: Capacidad calorífica total del conductor [J/(m-°C)]
        dT: incremento de temperatura en el conductor [°C]

    Returns:
        dt: variación discreta de tiempo [segundos]
    '''
    dt = ( ( mC_p ) / ( R_T_avg * I**2 + q_s -q_c - q_r ) ) * ( dT )
    return dt