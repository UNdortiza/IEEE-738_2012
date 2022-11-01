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