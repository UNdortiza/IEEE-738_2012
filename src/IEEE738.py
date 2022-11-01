# STEADY STATE #

## Steady state termal rating

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

## Steady state conductor temperature

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

### Convection heat loss

def convection_heat_loss( T_s, T_a, H_e, D_o, phi, V_w ):
    '''
    Calcula la perdida de calor por convección como el valor mayor entre las perdidas de calor por convección forzada y convección natural.

    Args:
        T_s: temperatura de la superficie del conductor [°C]
        T_a: temperatura ambiente [°C]
        H_e: elevación del conductor sobre el nivel del mar [m]
        D_o: diámetro exterior del conductor [m]
        phi: ángulo entre la dirección del viento y el eje axial del conductor [deg]
        V_w: velocidad del viento [m/s][ft/s]

    Returns:
        q_c: perdidas de calor por convección [W/m]
    '''
    # Air and conductor properties
    T_film = temperature_boundary_layer( T_s, T_a )
    rho_f = air_density( H_e, T_film )
    mu_f = air_viscosity( T_film )
    k_f = air_thermal_conductivity_coefficient( T_film )
    # Natural Convection heat loss q_cn: perdidas de calor por convección natural [W/m]
    q_cn = natural_convection_heat_loss( rho_f, D_o, T_s, T_a )
    # Forced Convection heat loss q_cf: perdidas de calor por convección forzada [W/m]
    K_angle = wind_direction_factor( phi )
    N_Re = reynolds_number( D_o, rho_f, V_w, mu_f )
    q_cf = forced_convection_heat_loss( K_angle, N_Re, k_f, T_s, T_a )
    # Calcula la perdida de calor por convección como el valor mayor entre las perdidas de calor por convección forzada y convección natural.
    try:
        q_c = max( q_cf, q_cn )
    except:
        q_c = 0
    return q_c
    

def forced_convection_heat_loss( K_angle:float, N_Re:float, k_f:float, T_s:float, T_a:float ):
    '''
    Calcula las perdidas de calor por convección forzada. Los parámetros de entrada deben estar en unidades estándar SI o US, uno a la vez.
    El calculo es valido para diámetros de conductor entre 0.01 y 150 mm; Velocidades del aire entre 0 y 18.9 m/s; temperatura del aire entre 15.6 y 260 ˚C; temperatura del conductor entre 21 y 1004 ˚C; presión del aire entre 40.5 y 405 kPa.   

    Args:
        K_angle: factor de dirección del viento[adimensional]
        N_Re: número de Reynolds [adimensional]
        k_f: conductividad térmica del aire a temperatura media de la capa límite [W/(m-°C)][W/(ft-°C)]
        T_s: temperatura de la superficie del conductor [°C][°C]
        T_a: temperatura ambiente [°C][°C]

    Returns:
        q_cf: perdidas de calor por convección forzada [W/m][W/ft]. Se calcula como el mayor valor entre:
            q_cf1: válida para bajas velocidades del viento
            q_cf2: válida para altas velocidades del viento
    '''
    q_cf1 = K_angle * ( 1.01 + 1.35 * pow( N_Re, 0.52 )  ) * k_f * ( T_s - T_a )
    q_cf2 = K_angle * 0.754 * pow( N_Re, 0.6 ) * k_f * ( T_s - T_a )
    try:
        q_cf = max( q_cf1, q_cf2 )
    except:
        q_cf = 0
    return q_cf

def natural_convection_heat_loss(rho_f:float, D_o:float, T_s:float, T_a:float):
    '''
    Calcula las perdidas de calor por convección natural. Los parámetros de entrada deben estar en unidades estándar SI.

    Args:
        rho_f: densidad del aire [kg/m3]
        D_o: diámetro exterior del conductor [m]
        T_s: temperatura de la superficie del conductor [°C]
        T_a: temperatura ambiente [°C]

    Returns:
        q_cn: perdidas de calor por convección natural [W/m]
    '''
    q_cn = 3.645 * pow( rho_f, 0.5 ) * pow( D_o, 0.75 ) * pow( ( T_s - T_a ), 1.25 )
    return q_cn

def reynolds_number(D_o:float, rho_f:float, V_w:float, mu_f:float):
    '''Calcula el número de Reynolds.
    
    Args: 
        D_o: diámetro exterior del conductor [m][ft]
        rho_f: densidad del aire [kg/m3][lb/ft3]
        V_w: velocidad del viento [m/s][ft/s]
        mu_f: viscosidad absoluta (dinámica) del aire [kg/m-s][lb/ft-hr]

    Returns:
        N_Re: número de Reynolds [adimensional]
    '''
    N_Re = D_o * rho_f * V_w / mu_f
    return N_Re

def wind_direction_factor( phi:float ):
    ''' Calcula el factor de dirección del viento.

    Args:
        phi (float): ángulo entre la dirección del viento y el eje axial del conductor [deg]

    Returns:
        K_angle (float): factor de dirección del viento[adimensional]
    '''
    from math import cos, sin, radians
    K_angle = 1.194 - cos( radians( phi ) ) + 0.194 * cos( radians( 2 * phi ) ) + 0.368 * sin( radians( 2 * phi ) )
    return K_angle

def temperature_boundary_layer(T_s, T_a):
    '''
    Calcula la temperatura media de la capa límite.

    Args:
        T_s: temperatura de la superficie del conductor [°C]
        T_a: temperatura ambiente [°C]
    
    Returns:
        T_film: temperatura media de la capa límite [°C]
    '''
    T_film = ( T_s + T_a ) / 2
    return T_film

def air_density(H_e, T_film):
    '''
    Calcula la densidad del aire.

    Args:
        H_e: elevación del conductor sobre el nivel del mar [m]
        T_film: temperatura media de la capa límite [°C]

    Returns:
        rho_f: densidad del aire [kg/m3]
    '''
    rho_f = ( 1.293 - 1.525e-4 * H_e + 6.379e-9 * pow( H_e, 2 ) ) / ( 1 + 0.00367 * T_film )
    return rho_f

def air_viscosity(T_film):
    '''
    Calcula la viscosidad dinámica del aire.

    Args:
        T_film: temperatura media de la capa límite [°C]
    
    Returns:
        mu_f: viscosidad absoluta (dinámica) del aire [kg/m-s]
    '''
    mu_f = ( 1.458e-6 * pow( ( T_film + 273 ), 1.5 ) ) / ( T_film + 383.4 )
    return mu_f

def air_thermal_conductivity_coefficient(T_film):
    '''
    Calcula conductividad térmica del aire a temperatura media de la capa límite.

    Args:
        T_film: temperatura media de la capa límite [°C]
    
    Returns:
        k_f:  conductividad térmica del aire a T_film [W/(m-°C)]
    '''
    k_f = 2.424e-2 + 7.477e-5 * T_film - 4.407e-9 * pow( T_film, 2 )
    return k_f

### Radiated heat loss

def radiated_heat_loss(D_o, epsilon, T_s, T_a ):
    '''
    Calcula la tasa de pérdida de calor radiado por unidad de longitud.

    Args:
        D_o: diámetro exterior del conductor [m]
        epsilon: coeficiente de emisividad [adimensional]
        T_s: temperatura de la superficie del conductor [°C]
        T_a: temperatura ambiente [°C]

    Returns:
        q_r: tasa de pérdida de calor radiado por unidad de longitud [W/m]
    '''
    q_r = 17.8 * D_o * epsilon * ( pow( ( T_s + 273 ) / 100 , 4 ) - pow( ( T_a + 273 ) / 100 , 4 ) )
    return q_r

### Solar heat gain

from datetime import datetime

def solar_heat_gain( year, month, day, hour, H_e, lat, industrial_atmosphere, Z_l, D_o, alpha ):
    '''
    Calcula la tasa de ganancia de calor debido al sol.
    
    Args:
        year: año para el cual se hace el calculo [AAAA]
        month: mes para el cual se hace el calculo [MM]
        day: dia para el cual se hace el calculo [DD]
        hour: hora del dia para el cual se hace el calculo en formato militar [hh]
        H_e: elevación del conductor sobre el nivel del mar [m]
        lat: grados de latitud [deg]
        industrial_atmosphere: valor booleano que representa el ambiente industrial. Si es falso, se asume un ambiente claro
        Z_l: azimut del conductor [deg]
        D_o: diámetro exterior del conductor [m]
        alpha: coeficiente de absorción solar [adimensional]

    Returns:
        q_s: tasa de ganancia de calor del sol [W/m]
    '''
    from math import sin, radians
    date = datetime(year, month, day)
    K_solar = elevation_correction_factor( H_e )
    N = day_of_year( date )
    delta = solar_declination( N )
    omega = hour_angle( hour )
    H_c = altitude_sun( lat, delta, omega )
    Q_s = total_heat_flux_density( H_c, industrial_atmosphere )
    Q_se = total_heat_flux_intensity( K_solar, Q_s )
    ji = azimuth_variable( omega, lat, delta )
    C = azimuth_constant( omega, ji )
    Z_c = azimuth( C, ji )
    theta = solar_rays_incidence_angle( H_c, Z_c, Z_l )
    # A: Área proyectada del conductor [m2/linear m], se asume como el diámetro del conductor por cada metro.
    A = D_o
    q_s = alpha * Q_se * sin( radians( theta ) ) * A 
    if q_s < 0:
        q_s = 0
    return q_s
    
def solar_rays_incidence_angle( H_c, Z_c, Z_l ):
    '''
    Calcula el ángulo efectivo de incidencia de los rayos del sol.

    Args:
        H_c: ángulo de altitud del sol [deg]
        Z_c: azimut del sol [deg]
        Z_l: azimut del conductor [deg]
    
    Returns:
        theta: ángulo efectivo de incidencia de los rayos del sol [deg]
    '''
    from math import acos, cos, radians, degrees
    theta = degrees( acos( cos( radians( H_c ) ) * cos( radians( Z_c - Z_l ) ) ) )
    return theta

def altitude_sun( lat, delta, omega ):
    '''
    Calcula el ángulo de altitud del sol.

    Args:
        lat: grados de latitud [deg]
        delta: declinación solar (-23.45 a +23.45) [deg]
        omega: ángulo horario relativo al mediodía, 15*(Hora-12) [deg]

    Returns:
        H_c: ángulo de altitud del sol (0 a 90) [deg]
    '''
    from math import asin, cos, sin, radians, degrees
    H_c = degrees( asin( cos( radians( lat ) ) * cos( radians( delta )  ) * cos( radians( omega ) ) + sin( radians( lat ) ) * sin( radians( delta ) ) ) ) 
    if ( H_c < 0 ):
        H_c = 0
    return H_c

def solar_declination( N:int ):
    '''
    Calcula el ángulo de declinación solar.

    Args:
        N: Día del año (21 de enero = 21, Solsticios en 172 y 355) [adimensional]

    Returns:
        delta: ángulo de declinación solar (-23.45 a +23.45) [deg]
    '''
    from math import sin, radians
    delta = 23.46 * sin( radians( ( 284 + N ) * 360 / 365 ) )
    return delta

def day_of_year( date:datetime ):
    '''
    Calcula el dia del año para una fecha dada.

    Args:
        date: fecha a calcular [datetime(año, mes, dia)]
    
    Returns:
        N: Día del año (21 de enero = 21, Solsticios en 172 y 355) [adimensional]
    '''
    N = ( date - datetime( date.year, 1, 1 ) ).days 
    return N

def azimuth( C, ji ):
    '''
    Calcula el azimut del sol.

    Args: 
        C: constante de acimut solar [deg]
        ji: variable de azimut solar [adimensional]

    Returns:
        Z_c: azimut del sol [deg]
    '''
    from math import atan, degrees
    Z_c = C + degrees( atan( ji ) )
    return Z_c

def azimuth_variable( omega, lat, delta ):
    '''
    Calcula la variable del azimut del sol.

    Args:
        omega: ángulo horario relativo al mediodía, 15*(Hora-12) [deg]
        lat: grados de latitud [deg]
        delta: ángulo de declinación solar (-23.45 a +23.45) [deg]

    Returns:
        ji: variable de azimut solar [adimensional]
    '''
    from math import cos, sin, tan, radians
    ji = sin( radians( omega ) ) / ( sin( radians( lat ) ) * cos( radians( omega ) ) - cos( radians( lat ) ) * tan( radians( delta ) ) )
    return ji

def azimuth_constant( omega, ji ):
    '''
    Calcula la constante del azimut del sol.

    Args:
        omega: ángulo horario relativo al mediodía, 15*(Hora-12) [deg]
        ji: variable de azimut solar [adimensional]

    Returns:
        C: constante de acimut solar [deg]
    '''
    C = 180
    if -180 <= omega < 0 and ji >= 0 :
        C = 0
    elif 0 <= omega < 180 and ji < 0 :
        C = 360
    return C

def hour_angle( hour:int ):
    '''
    Calcula el angulo horario.

    Args:
        hour: hora del dia en formato militar [h]

    Returns:
        omega: ángulo horario relativo al mediodía, 15*(Hora-12) [deg]
    '''
    omega = 15 * ( hour - 12 )
    return omega

def total_heat_flux_density( H_c, industrial_atmosphere:bool ):
    '''
    Calcula la Intensidad total del calor irradiado del sol y del cielo.

    Args:
        H_c: ángulo de altitud del sol (0 a 90) [deg]
        industrial_atmosphere: valor booleano que representa el ambiente industrial. Si es falso, se asume un ambiente claro.

    Returns:
        Q_s: Intensidad total del calor irradiado del sol y del cielo [W/m2]
    '''
    A, B, C, D, E, F, G = -42.2391, 63.8044, -1.9220, 3.46921e-2, -3.61118e-4, 1.94318e-6, -4.07608e-9
    if industrial_atmosphere :
        A, B, C, D, E, F, G = 53.1821, 14.2110, 6.6138e-1, -3.1658e-2, 5.4654e-4, 4.3446e-6, 1.3236e-8
    Q_s = A + B * H_c + C * pow( H_c, 2 ) + D * pow( H_c, 3 ) + E * pow( H_c, 4 ) + F * pow( H_c, 5 ) + G * pow( H_c, 6 )
    return Q_s

def total_heat_flux_intensity( K_solar, Q_s ):
    '''
    Calcula la intensidad total del calor solar y radiado por el cielo corregido por la elevación.
    
    Args:
        K_solar: factor de corrección por altitud del flujo solar [adimensional]
        Q_s: Intensidad total del calor irradiado del sol y del cielo [W/m2]

    Returns:
        Q_se: intensidad total del calor solar y radiado por el cielo corregido por la elevación [W/m2]
    '''
    Q_se = K_solar * Q_s
    return Q_se

def elevation_correction_factor( H_e ):
    '''
    Calcula el factor de corrección por altitud del flujo solar.

    Args:
        H_e: elevación del conductor sobre el nivel del mar [m]

    Returns:
        K_solar: factor de corrección por altitud del flujo solar [adimensional]
    '''
    A, B, C = 1, 1.148e-4, -1.108e-8
    K_solar = A + B * H_e + C * pow( H_e, 2 )
    return K_solar


### Conductor electrical capacity

def conductor_electrical_resistance( R_0, T_0, alpha_T, T_avg ):
    '''
    Calcula la resistividad  del conductor a una temperatura T_avg
        
    Args:
        R_0: Resistividad del conductor a una temperatura inicial T_0 [Ω/m] 
        T_0: temperatura inicial del conductor [°C]
        alpha_T: coeficiente de variación relativa de la resistencia debido a la temperatura [1/°C]
        T_avg: temperatura media del conductor [°C]

    Returns:
        R_T_avg: resistividad  del conductor a una temperatura T_avg [Ω/m]
    '''
    R_T_avg = R_0 * ( 1 + alpha_T * ( T_avg - T_0 ) )
    return R_T_avg

# TRANSIENT #

## Transient conductor temperature

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

## Transient settling time

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

### Conductor heat capacity

def conductor_heat_capacity(m_i:list, C_pi:list):
    '''
    Calcula la capacidad calorífica total del conductor.

    Args:
        m_i: Masa por unidad de longitud del i-ésimo material conductor [kg/m]
        C_pi: Calor específico del i-ésimo material conductor [J/kg-°C] 

    Returns:
        mC_p: Capacidad calorífica total del conductor [J/(m-°C)]
    '''
    mC_p = 0
    m_iC_pi = list( zip( m_i, C_pi ) )
    for mC in m_iC_pi :
        mC_p += mC[0] * mC[1]
    return mC_p