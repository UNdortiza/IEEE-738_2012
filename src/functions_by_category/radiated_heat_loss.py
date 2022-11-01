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