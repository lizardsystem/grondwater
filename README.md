# grondwater
grondwatermodule. Rekent op basis van een bakjesmodel en de dagwaardes van neerslag en verdamping de grondwaterstand uit.

zie ook: http://support.nelen-schuurmans.nl/twiki/bin/view/Support/LizardBOSM03S40

M03S40
------

Grondwatermodule: berekent een schatting van het grondwater.
Input: meteo csv's zoals 20130424-20000-METEO_TL.CSV
Output: DS_RD_GW_HT met een tijdreeks voor default de laatste 90 dagen.

Integratie in BOS
-----------------

(doet systeembeheerder)
Alle stappen controleren of ze werken, dan de volgende stap uitvoeren.

- Draai M03S40 om te testen.
- Inputdirectory is DATA\METEO\ en de files moeten er zoals deze uitzien: 20130424-20000-METEO_TL.CSV
- Outputdirectory is DATABASE\SDB\DS_RD_GW_HT.bin
- In grondwater.cfg is de config te vinden.
- De uitvoer is ook in LOGS\M03S40.log te vinden.

De uitvoer moet er ongeveer zo uitzien:

Grondwatermodule.
Initial ground waterlevel 0.000000
Input dir: meteo
Output filename: grondwater.bin
Output type: bin
Start date: 20130101
End date: 20130401
...
File not found: meteo/20130630-*-METEO_TL.CSV
skipped datetime.datetime(2013, 6, 30, 0, 0)
20130630 {'c_harm': 500.0, 'downpour': 0.0, 'd_harm': 0.0, 'ht': 0.020715598696715538, 'evaporation': 0.0, 'r': 0.0}
writing BOS file grondwater.bin...

Zorg dat hij 1x per dag (bv. om 2 uur in de nacht) meedraait met de dirigent.
Dirigent_ini_mod, na de andere M03 modules.
Als je de module met de hand draait moet je een DS_RD_GW_HT.bin krijgen. Deze file kun je de volgende dag checken of hij in de nacht heeft gedraaid.
Zorg dat de validatie en bijgis modules werken op de ruwe file DS_RD_GW_HT.bin. Zo ontstaat er een DS_VD_GW_HT.bin en een DS_TD_GW_HT.bin.
Nieuwe GROUP/SUBGROUP ID
M02S01 en M02S02: DS_RD_GW_HT toevoegen in m02_checktable, gebruik class "level_prediction"
Controleer nadat je M02S01 en M02S02 draait of je DS_VD_GW_HT.bin en resp. DS_TD_GW_HT.bin krijgt. Controlleer ook de inhoud of er ook waardes in zitten.
Zorg dat DS_TD_GW_HT.bin mee wordt gezonden naar de GUI.
DB_INDEX_VALUE
Velden op 1: SDB_DISP, DISP_TYPE
DB_LINETYPE op 1
Opnieuw opstarten BOS server. De ComManager zorgt voor de acties in DB_INDEX_VALUE. Tijdstap wachten en vervolgens DISPxxx.bin controleren.
Zorg ervoor dat hij in de GUI ook in de grafiek voorkomt.
DS_ID_GRAPH_LINE_DEF: Meteo grafiek,DS_TD_GW_HT,,bruin,0,,,0,,1

Ontwikkeling
------------

Zorgen dat je een M03S40.exe hebt (doet Jack)
cxFreeze 4.3.1 om van python naar exe te komen
path naar c:\python27\scripts
cxfreeze grondwater.py --target-dir=M03S40 --target-name=M03S40.exe
Deze maakt een M03S40.exe samen met python27.dll. Zet deze in de BOS directory.

Zet grondwater.cfg ook erbij. Deze hoort er zo uit te zien:
[model]
# bergingscoefficient [-]
s = 0.05
# drainageweerstand bovenste systeem [d]
c1 = 50
# drainageweerstand onderste systeem [d]
c2 = 500
# bovenste drempelhoogte [m]
d1 = 0.3
# drainagebasis onderste systeem [m]
d2 = 0.0
# maaiveldhoogte [m]
mv = 0.5
