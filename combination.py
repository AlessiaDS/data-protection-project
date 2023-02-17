def combination(self):
    ''' dgh_path_height:
    sex: 0,1
    zipcode: 0,1,2,3,4,5
    date: 0,1,2,3
    '''

    sex = (0,1)
    zipcode = (0,1,2,3,4,5)
    date = (0,1,2,3)

    quasiComb = []
    for s in sex:
        for z in zipcode:
            for d in date:
                quasiComb.append((s,z,d))
    return quasiComb
    '''tuple= [(0,0,1),(1,0,2),]'''



