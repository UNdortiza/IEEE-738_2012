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


