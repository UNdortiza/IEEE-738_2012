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