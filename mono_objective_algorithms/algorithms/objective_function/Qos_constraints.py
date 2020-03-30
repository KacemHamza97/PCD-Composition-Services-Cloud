def verifyConstraints(qos, constraints):
    drt = constraints['responseTime'] - qos['responseTime']
    dpr = constraints['price'] - qos['price']
    dav = qos['availability'] - constraints['availability']
    drel = qos['reliability'] - constraints['reliability']

    return drt and dpr and dav and drel
