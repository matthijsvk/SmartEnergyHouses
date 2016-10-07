* T01 = 06:00, T24 = 12:00, T48 = 18:00, T96 = 00:00
* daytime pricing is assumed from 07:00 until 22:00
sets
t                quarters during 24h                                             /T01*T96/
twm(t)           quarters not allowed as starting quarter for washing machine    /T94*T96/
Alias(t,ta);

Parameters
price_1(t)         price of energy per watt with correct ratios
                                                /T01 54, T02 54, T03 54, T04 54, T05 69, T06 69, T07 69, T08 69, T09 69, T10 69,
                                                 T11 69, T12 69, T13 69, T14 69, T15 69, T16 69, T17 69, T18 69, T19 69, T20 69,
                                                 T21 69, T22 69, T23 69, T24 69, T25 69, T26 69, T27 69, T28 69, T29 69, T30 69,
                                                 T31 69, T32 69, T33 69, T34 69, T35 69, T36 69, T37 69, T38 69, T39 69, T40 69,
                                                 T41 69, T42 69, T43 69, T44 69, T45 69, T46 69, T47 69, T48 69, T49 69, T50 69,
                                                 T51 69, T52 69, T53 69, T54 69, T55 69, T56 69, T57 69, T58 69, T59 69, T60 69,
                                                 T61 69, T62 69, T63 69, T64 69, T65 54, T66 54, T67 54, T68 54, T69 54, T70 54,
                                                 T71 54, T72 54, T73 54, T74 54, T75 54, T76 54, T77 54, T78 54, T79 54, T80 54,
                                                 T81 54, T82 54, T83 54, T84 54, T85 54, T86 54, T87 54, T88 54, T89 54, T90 54,
                                                 T91 54, T92 54, T93 54, T94 54, T95 54, T96 54 /

dcat1(t)         category1 demand(fixed) in  Watt.
                                                  /T01 1000, T02 440, T03 281, T04 300, T05 2826, T06 413, T07 610, T08 400, T09 530, T10 17,
                                                  T11 44, T12 80, T13 185, T14 225, T15 230, T16 225, T17 225, T18 44, T19 44, T20 44,
                                                  T21 44, T22 44, T23 44, T24 44, T25 44, T26 44, T27 44, T28 44, T29 44, T30 185,
                                                  T31 309, T32 448, T33 2973, T34 448, T35 536, T36 536, T37 44, T38 44, T39 44, T40 44,
                                                  T41 44, T42 44, T43 44, T44 44, T45 44, T46 44, T47 44, T48 356, T49 232, T50 362,
                                                  T51 1975, T52 8735, T53 513, T54 570, T55 921, T56 3329, T57 3589, T58 1128, T59 895, T60 903,
                                                  T61 803, T62 613, T63 44, T64 44, T65 44, T66 44, T67 44, T68 44, T69 44, T70 44,
                                                  T71 44, T72 44, T73 44, T74 44, T75 44, T76 312, T77 291, T78 44, T79 44, T80 44,
                                                  T81 44, T82 44, T83 44, T84 44, T85 44, T86 44, T87 44, T88 44, T89 44, T90 44,
                                                  T91 44, T92 44, T93 44, T94 44, T95 44, T96 338/ ;
Parameter price(t)               price in µ€ per Watt rescaled to realastic values;
                                 price(t) = price_1(t)/3.6;
Parameters
wmd(ta)          demand of washing machine       /T01 500, T02 400, T03 400, T04 600/
wmnc             number of cycli of washing m.   /1/
awmd(ta)         demand of dishwasher            /T01 150, T02 100, T03 60/
awmnc            number of cycli of dishwasher   /1/

dcat3(t)         demand of cat3
Plocal(t)       local produced energy in Watt   /T01 10, T02 15, T03 30, T04 45, T05 55, T06 60, T07 64, T08 68, T09 75, T10 87,
                                                  T11 98, T12 100, T13 105, T14 117, T15 129, T16 136, T17 145, T18 160, T19 172, T20 180,
                                                  T21 192, T22 195, T23 197, T24 200, T25 200, T26 195, T27 189, T28 180, T29 165, T30 150,
                                                  T31 148, T32 145, T33 135, T34 129, T35 127, T36 109, T37 103, T38 100, T39 98, T40 95,
                                                  T41 93, T42 92, T43 88, T44 79, T45 73, T46 59, T47 56, T48 53, T49 43, T50 39, T51 32,
                                                  T52 28, T53 24, T54 17, T55 09, T56 0, T57 0, T58 0, T59 0,
                                                  T60 0, T61 0, T62 0, T63 0, T64 0, T65 0, T66 0, T67 0, T68 0, T69 0,
                                                  T70 0, T71 0, T72 0, T73 0, T74 0, T75 0, T76 0, T77 0, T78 0, T79 0,
                                                  T80 0, T81 0, T82 0, T83 0, T84 0, T85 0, T86 0, T87 0, T88 0, T89 0,
                                                  T90 0, T91 0, T92 0, T93 0, T94 0, T95 0, T96 0 /

parameter P_local(t) local produced energy in Watt;
P_local(t) = Plocal(t)*10;
*All temperatures are in Kelvin (K).
;
scalar nb_wm             number of washing machines                      /1/ ;
scalar nb_awm            number of dishwashers                           /1/;
scalar T_outside         outside temperature (assumed constant)          /283/    ;
scalar T_fr_min          minimal temperature allowed of fridge           /268/ ;
scalar T_fr_max          maximal temperature allowed of fridge           /278/;
scalar P_frigo           constant power of fridge                        /200/ ;
scalar wmdur             duration of washing machine cycle (quarters)    /4/
scalar awmdur            duration of dishwasher cycle (quarters)         /1/
scalar T_h_min           minimal temperature allowed in house            /293/ ;
scalar T_h_max           maximal temperature allowed in house            /298/;
scalar P_vw_max          maximal power of heating possible               /2000/;
scalar tstep             timestep in seconds of one cyclus               /900/;
scalar price_Curt        price of curtailed energy in € per Watt         /0/;



Variables
y                        Objective function in euros
z                        Objective function in µ€

;

Positive variables
P_conv(t)                conventional power supply
P_cat1(t)                demand of appliances of cat1
P_cat2(t)                demand of appliances of cat2
P_cat3(t)                demand of appliances of cat3
P_cat4(t)                demand of appliances of cat4
Curt(t)                  Curtailment
T_frigo(t)               temperature in fridge
T_house(t)               temperature in house
P_vw(t)                  Power used per quarter by heating


;

Integer variables
ti(t)                    start time for cycle washing machine
ti2(t)                   start time for cycle washing machine
ti3(t)                   start time for cycle washing machine
ti4(t)                   start time for cycle washing machine
tia(t)                   start time for cycle dishwasher
tia2(t)                  start time for cycle dishwasher
tia3(t)                  start time for cycle dishwasher

zfr(t)                   returns 0 if not working and returns 1 if cooling in that quarter
zvw(t)                   returns 0 if not working and returns 1 if heating in that quarter

;

Equations
yeq                      Objective function in euros
zeq                      Objective function in microeuros
balance(t)               electricity balance equation
wmnceq                   makes sure washing machine works the right amount of times
cat1(t)                  demand for appliances of cat1
ti2eq(t)                 start of part 2 of the washing machine load curve
ti3eq(t)                 start of part 3 of the washing machine load curve
ti4eq(t)                 start of part 4 of the washing machine load curve
cat2(t)                  demand for appliances of cat2
cat3(t)                  demand for appliances of cat3
cat4(t)                  demand for appliances of cat4
nmdewmeq(t)              ensures that only one washing machine is working at a certain time
awmnceq                  makes sure dishwasher works the right amount of times
tia2eq(t)                start of part 2 of the dishwasher load curve
tia3eq(t)                start of part 3 of the dishwasher load curve
nmdeawmeq(t)             ensures that only one dishwasher works the needed amount of cycles

T_frigo_eq(t)            defines the allowed temperature interval of fridge (sets bound)
diff_frigo(t)            the differential equation with regard to the fridge
T_frigo_eq2(t)           defines the allowed temperature interval of fridge (sets bound)
T_frigot01(t)            defines starting temperature of fridge
dcat3_eq(t)              defines the category 3 demand fucntion
zfr_lo(t)                ensures that zfr doesn't return a value lower than zero
zfr_up(t)                ensures that zfr doesn't return a value higher than one

T_house_eq(t)            defines the allowed temperature interval of house (sets bound)
T_house_t01(t)           defines the starting temperature of house

diff_vw(t)               the differential equation with regard to the fridge
T_house_eq2(t)           defines the allowed temperature interval of house (sets bound)

P_vw_eq(t)               defines the equation of the power of the heating


;
yeq..                    y =e= z/1000000;
zeq ..                   z =e= sum(t,P_conv(t)*price(t))+sum(t,Curt(t)*price_Curt);
balance(t) ..            P_conv(t)+P_local(t) =e= P_cat1(t)+P_cat2(t)+P_cat3(t)+P_cat4(t)+Curt(t);
cat1(t)..                P_cat1(t) =e= dcat1(t);
wmnceq ..                wmnc =e= sum(t$(ord(t)<card(t)-(wmdur-2)),ti(t));
cat2(t)..                P_cat2(t) =e=   wmd('T01')*ti(t)
                                 + wmd('T02')*ti2(t)
                                 + wmd('T03')*ti3(t)
                                 + wmd('T04')*ti4(t)
                                 + awmd('T01')*tia(t)
                                 + awmd('T02')*tia2(t)
                                 + awmd('T03')*tia3(t);
ti2eq(t) ..              ti2(t+1)=e= ti(t);
ti3eq(t) ..              ti3(t+2) =e= ti(t);
ti4eq(t) ..              ti4(t+3)=e= ti(t);
nmdewmeq(t)..            ti(t)+ti2(t)+ti3(t)+ti4(t)=l= nb_wm;


T_frigo_eq(t) ..                 T_fr_min =l= T_frigo(t) ;
T_frigo_eq2(t) ..                T_frigo(t)=l= T_fr_max ;
cat3(t)..                        P_cat3(t)=e= zfr(t)*P_frigo ;
dcat3_eq(t)..                    dcat3(t)=e= zfr(t)*P_frigo ;
diff_frigo(t)$(ord(t)<card(t)).. T_frigo(t+1)=e=(T_frigo(t))+((1/18000)*tstep*(T_house(t)-T_frigo(t)))-((3/180000)*tstep*(P_frigo*(zfr(t))));
T_frigot01(t)..                  T_frigo('T01')=e= T_fr_max ;
zfr_lo(t)..                      zfr(t)=g=0;
zfr_up(t) ..                     zfr(t)=l=1 ;
awmnceq ..                       awmnc =e= sum(t$(ord(t)<card(t)-(awmdur-1)),tia(t));
tia2eq(t) ..                     tia2(t+1)=e= tia(t);
tia3eq(t) ..                     tia3(t+2) =e= tia(t);
nmdeawmeq(t)..                    tia(t)+tia2(t)+tia3(t)=l= nb_awm;

cat4(t) ..                       P_cat4(t)=e=P_vw(t)   ;
T_house_eq(t) ..                 T_h_min =l= T_house(t);
T_house_eq2(t) ..                T_house(t)=l= T_h_max   ;
diff_vw(t)$(ord(t)<card(t))..    T_house(t+1)=e=(T_house(t))-((1/9000)*tstep*(-T_outside+T_house(t)))+(3/1800000)*tstep*P_vw(t);
P_vw_eq(t)..                     P_vw(t) =l= P_vw_max;
T_house_t01(t)..                 T_house('T01')=e=T_h_min  ;






model AC apliance committment    /
         zeq, yeq
         balance,cat1,cat2,ti2eq,ti3eq,ti4eq,
         wmnceq,nmdewmeq,T_frigo_eq,diff_frigo,
         T_frigo_eq2,cat3,T_frigot01,zfr_lo,zfr_up,
         T_house_eq,
         T_house_eq2,
         cat4,diff_vw,T_house_t01, P_vw_eq,
         awmnceq,
         tia2eq,
         tia3eq,
         nmdeawmeq/ ;
solve AC using mip minimizing y;

display dcat1,P_conv.l, ti.l,T_frigo.l,zfr.l,P_cat3.l,P_cat4.l,T_house.l, P_vw.l,y.l;
