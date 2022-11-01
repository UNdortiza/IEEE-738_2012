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