## running gams files from Dagnachttarief_inclusief_local_realistisch_geen_curtail
import gams
import os
def init():
    global t1
    ws=gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.ShowLog)
    t1 = ws.add_job_from_file("Dagnachttarief_inclusief_local_realistisch_geen_curtail.gms")
    t1.run()
def run():

    ##Defines needed empty lists
    zfrlst=[]
    pricelst=[]
    pconvlst=[]
    tfrilst=[]
    thouselst=[]
    pvwlst=[]
    tilst=[]
    ti2lst=[]
    ti3lst=[]
    ti4lst=[]
    wmlst=[]
    tialst=[]
    tia2lst=[]
    tia3lst=[]
    dwlst=[]
    ploclst=[]
    curtlst=[]
    prtotlst=[]
    ## Saves needed variables in list

    ## zfrlst: returns 0 if fridge is off, 1 if fridge is on.

    for rec in t1.out_db["zfr"]:
        zfrlst+=[rec.level]
    ## pricelst: returns value of price at given quarter
        
    for k in t1.out_db["price"]:
        pricelst+= [k.value]
    ## pconvlst: returns used power at give quarter (in Watt) without local energy!
        
    for rec2 in t1.out_db["P_conv"]:
        pconvlst+= [rec2.level]
    ## tfrilst: returns temperature of fridge in Kelvin
        
    for rec3 in t1.out_db["T_frigo"]:
        tfrilst+=[rec3.level]
    ## thouselst: returns temperature of house in Kelvin
        
    for rec4 in t1.out_db["T_house"]:
        thouselst+=[rec4.level]
    ## pvwlst: returns needed power for heating to work. Is included in P_Conv.
        
    for rec5 in t1.out_db["P_vw"]:
        pvwlst+=[rec5.level]
    ## Defines needed helpvariables to define washing machine cycle
        
    for rec6 in t1.out_db["ti"]:
        tilst+=[rec6.level]

    for rec7 in t1.out_db["ti2"]:
        ti2lst+=[rec7.level]

    for rec8 in t1.out_db["ti3"]:
        ti3lst+=[rec8.level]

    for rec9 in t1.out_db["ti4"]:
        ti4lst+=[rec9.level]
    ##wmslt: returns 1 if washing machine is working, 0 if not.
        
    wmlst = [sum(x) for x in zip(tilst,ti2lst,ti3lst,ti4lst)]
    ##defines dishwasher helpvariables

    for rec10 in t1.out_db["tia"]:
        tialst+=[rec10.level]

    for rec11 in t1.out_db["tia2"]:
        tia2lst+=[rec11.level]

    for rec12 in t1.out_db["tia3"]:
        tia3lst+= [rec12.level]
        
    ##dwlst: returns 1 if dishwasher is working in time-interval, 0 if not.
    dwlst = [sum(x) for x in zip(tialst, tia2lst, tia3lst)]
## ploclst: returns the amount of local produced energy in given quarter, in Watt.
##
    for rec13 in t1.out_db["P_local"]:
        ploclst+=[rec13.value]
        
##prtotlst: returns total price of energy consumption of one day under given variables
    for rec15 in t1.out_db["y"]:
        prtotlst+= [rec15.level]


    return zfrlst, tfrilst, thouselst, pvwlst, wmlst, dwlst, pricelst
