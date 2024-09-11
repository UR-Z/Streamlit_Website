import pyodbc
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import os
from rag_functions import snowflake_logging

load_dotenv('../env.env')

def new_function(where_clause_filter) -> str:
            sql_query = f"""
        WITH
            
            cte_GPS_Calculations
            AS
            (
            SELECT 
                TRIM(GISIM) AS GISIM 
                , TRIM(GIEQP#) AS Equipment_Code
                , GISTTS
                , CASE WHEN GIMRDT > 0  
                    THEN CAST(DAYS(CURRENT_DATE) - DAYS(DATE(TO_DATE(CAST(GIMRDT AS VARCHAR(50)),'YYYYMMDD'))) AS INTEGER) 
                                        ELSE 0 
                                        END 
                                    AS Days_Since_Last_Meter_Reading
                , CASE WHEN GIMIDT > 0  
                        THEN CAST(DAYS(CURRENT_DATE) - DAYS(DATE(TO_DATE(CAST(GIMIDT AS VARCHAR(50)),'YYYYMMDD'))) AS INTEGER) 
                                        ELSE 0
                                        END
                                    AS Days_Since_Last_Mile_Reading 
                , CASE WHEN GIPSDT > 0  
                            THEN CAST(DAYS(CURRENT_DATE) - DAYS(DATE(TO_DATE(CAST(GIPSDT AS VARCHAR(50)),'YYYYMMDD'))) AS INTEGER) 
                                        ELSE 0 
                                        END 
                                AS Delta_Pos_day   
                , (CASE WHEN GIMETR > 0 OR GIMETR = 0 AND GIMILE = 0 THEN 'H' ELSE 'M' END) AS Mileage_HOUR_Code  
                
            FROM WSDATA.GPSSIMFL 
                
            WHERE 
                '{where_clause_filter}' IN (GIEQP#,GISIM,LTRIM(GISIM,'0'))--(GIEQP#,GISIM,LTRIM(GISIM,'0'))   ---???????????  FILTER VALUE
                --(TRIM(GIEQP#) = '11261419' OR TRIM(GISIM) = '11261419')
                AND GICMP <> 'ZZ'
            )
            
            
            SELECT
            "ESN#"
            , "Equipment Code"  
            , "Device Status"
            , "Device Model"
            , "Device Package"
            , "Last Ping"
            , "Last Lat/Long Date"
            , "Last Meter Reading Date"
            , "Last Meter Change Date"
            , "Device Health"
            , "Health Reason"
            
            FROM
            (
            SELECT DISTINCT
            sim.GISIM AS "ESN#"
            , sim.Equipment_Code AS "Equipment Code"  
            , sim.GISTTS AS "Device Status"
            , CASE WHEN sim.GIMODL IS NULL OR sim.GIMODL = '' THEN 'None' ELSE sim.GIMODL END AS "Device Model"
            , CASE WHEN sim.GIPKGD IS NULL OR sim.GIPKGD = '' THEN 'None' ELSE sim.GIPKGD END AS "Device Package"
            , CASE WHEN TO_CHAR(sim.GIPGDT) IS NULL OR TO_CHAR(sim.GIPGDT) = '' THEN 'None' ELSE CHAR(sim.GIPGDT,Iso) END AS "Last Ping"
            , CASE WHEN TO_CHAR(sim.GIPSDT) IS NULL OR TO_CHAR(sim.GIPSDT) = '' THEN 'None' ELSE CHAR(sim.GIPSDT,Iso) END AS "Last Lat/Long Date"
            , CASE WHEN TO_CHAR(sim.GIMRDT) IS NULL OR TO_CHAR(sim.GIMRDT) = '' THEN 'None' ELSE CHAR(sim.GIMRDT,Iso) END AS "Last Meter Reading Date"
            , CASE WHEN TO_CHAR(sim.GILMCD) IS NULL OR TO_CHAR(sim.GILMCD) = '' THEN 'None' ELSE CHAR(sim.GILMCD,Iso) END AS "Last Meter Change Date"
            --, ifnull(nhl.No_HOURS_or_LOCATION,0) AS No_HOURS_or_LOCATION
            --, ifnull(can.HOURS_CAN_Override,0) AS HOURS_CAN_Override
            --, ifnull(bat.HOURS_BATTERY_Override,0) AS HOURS_BATTERY_Override 
            --, ifnull(los.LOCATION_LOS_Override,0) AS LOCATION_LOS_Override
            , CASE WHEN((ifnull(nhl.No_HOURS_or_LOCATION,0) -  ifnull(can.Hours_CAN_Override,0) - ifnull(bat.Hours_BATTERY_Override,0) - ifnull(los.Location_LOS_Override,0))) = 0 
                THEN 'HEALTHY' 
                ELSE 'UNHEALTHY' 
                END AS "Device Health"
            , CASE WHEN ifnull(nhl.NO_Hours_or_Miles,0) = 1 AND ifnull(nhl.NO_Location,0) = 1 AND ifnull(bat.HOURS_BATTERY_Override,0) = 1 THEN 'BATTERY Exclusion'
                WHEN ifnull(nhl.NO_Hours_or_Miles,0) = 1 AND ifnull(nhl.NO_Location,0) = 0 AND ifnull(can.HOURS_CAN_Override,0) = 1 THEN 'CANBUS Exclusion'
                WHEN ifnull(nhl.NO_Hours_or_Miles,0) = 1 AND ifnull(nhl.NO_Location,0) = 1 AND ifnull(bat.HOURS_BATTERY_Override,0) = 0 THEN 'NOT reporting HOURS OR LOCATION'
                WHEN ifnull(nhl.NO_Hours_or_Miles,0) = 1 AND ifnull(nhl.NO_Location,0) = 0 AND ifnull(can.HOURS_CAN_Override,0) = 0 THEN 'NOT reporting HOURS'
                WHEN ifnull(nhl.NO_Location,0) = 1 AND ifnull(nhl.NO_Hours_or_Miles,0) = 0 AND ifnull(los.LOCATION_LOS_Override,0) = 1 THEN 'LINE-OF-SIGHT Exclusion'
                WHEN ifnull(nhl.NO_Location,0) = 1 AND ifnull(nhl.NO_Hours_or_Miles,0) = 0 AND ifnull(los.LOCATION_LOS_Override,0) = 0 THEN 'NOT reporting LOCATION'
                WHEN ifnull(nhl.NO_Location,0) = 1 AND ifnull(los.LOCATION_LOS_Override,0) = 1 THEN 'NOT reporting LOCATION'
                ELSE ''
                END
                AS "Health Reason"


            FROM 
            
            --  Sim Numbers to be made accessile for query by users
            (
                SELECT 
                TRIM(gps.GISIM) AS GISIM 
                , TRIM(GIEQP#) AS Equipment_Code
                , gps.GISTTS
                , gps.GIMODL
                , gps.GIPKGD
                , CASE WHEN gps.GIPGDT > 0 
                    THEN DATE(TO_DATE(CAST(gps.GIPGDT AS VARCHAR(50)),'YYYYMMDD'))
                    ELSE NULL 
                    END
                    AS GIPGDT
                , CASE WHEN gps.GIPSDT > 0 
                    THEN DATE(TO_DATE(CAST(gps.GIPSDT     AS VARCHAR(50)),'YYYYMMDD'))
                    ELSE NULL 
                    END
                    AS GIPSDT    
                , CASE WHEN gps.GIMRDT > 0 
                    THEN DATE(TO_DATE(CAST(gps.GIMRDT AS VARCHAR(50)),'YYYYMMDD'))
                    ELSE NULL 
                    END
                    AS GIMRDT
                , CASE WHEN gps.GILMCD > 19000000 -- GISIM '503460' has a value of 10.101 that beraks the > 0 logic
                    THEN DATE(TO_DATE(CAST(gps.GILMCD AS VARCHAR(50)),'YYYYMMDD'))
                    ELSE NULL 
                    END
                    AS GILMCD    
                    
                FROM 
                WSDATA.GPSSIMFL gps
                --LEFT JOIN 
                --WSDATA.GPSMODFL m
                    --ON --m.GLCMP = 'U1'
                    --m.G1MODL = gps.GIMODL
                    --AND m.G1LSRC = gps.GILSRC
                --LEFT JOIN 
                --WSDATA.EQPMASFL eqp
                    --ON --eqp.EMCMP = 'U1'
                    --eqp.EMEQP# = gps.GIEQP#
                --LEFT JOIN 
                --WSDATA.EQPCCMFL cc
                    --ON --cc.ECCMP = 'U1'
                    --cc.ECCATG = eqp.EMCATG
                    --AND cc.ECCLAS = eqp.EMCLAS
                WHERE
            '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                AND GICMP <> 'ZZ'
                --WHERE gps.GICMP = 'U1'
                -- AND gps.GISTTS = 'A' -- Include devices that are Active only
                -- AND gps.GIEQP# <> '' -- Use this to indicate if the device is married to a machine or not.
                -- AND gps.GIMTR2 <> 'Y' -- Exlcude the secondary devices such as EAM
                -- AND m.G1PINS = 'Y' --  Exclude devices that are Permanent installed and not a slap and track device 
                -- AND eqp.EMTYPE IN ('R', 'S') -- Include only devices in type Rental or Subleased
                -- AND eqp.EMSTAT NOT IN ('S', 'J', 'M', 'T', 'V') -- Exclude devices on machines that are Sold, etc.
            ) sim
            
                
            LEFT JOIN 
            -- Select all sim values that qualify as 'Rental Equipment No HOURS or LOCATION - ALL Perm Active Devices Installed on Rental Machines'
            -- Extra lines of filtering added to standard filters used throughout all select statements 
            (
            SELECT
                TRIM(gps.GISIM) AS GISIM
                , gps.GISTTS
                , CASE WHEN
                    (CASE WHEN 
                    mh.Mileage_Hour_Code = 'H' AND (CASE WHEN(mh.Days_Since_Last_Meter_Reading) BETWEEN 1 AND 4 THEN '1' ELSE '0' end) = '0' THEN 'False' 
                    WHEN
                        (CASE WHEN mh.Mileage_Hour_Code = 'M' AND gps.GILSRC = 'GEO' 
                            THEN mh.Days_Since_Last_Mile_Reading  
                            ELSE mh.Days_Since_Last_Meter_Reading END) BETWEEN 1 AND 4 THEN 'True' 
                    ELSE 'False'          
                    END) = 'False'     
                OR
                    (CASE WHEN mh.Delta_Pos_day < 4 THEN 'True' ELSE 'False' END) = 'False'
                THEN 1    
                ELSE 0
                END
                AS No_HOURS_or_LOCATION
                , CASE WHEN(CASE WHEN 
                    mh.Mileage_Hour_Code = 'H' AND (CASE WHEN(mh.Days_Since_Last_Meter_Reading) BETWEEN 1 AND 4 THEN '1' ELSE '0' end) = '0' THEN 'False' 
                    WHEN
                        (CASE WHEN mh.Mileage_Hour_Code = 'M' AND gps.GILSRC = 'GEO' 
                            THEN mh.Days_Since_Last_Mile_Reading  
                            ELSE mh.Days_Since_Last_Meter_Reading END) BETWEEN 1 AND 4 THEN 'True' 
                    ELSE 'False'          
                    END) = 'False'
                THEN 1
                ELSE 0
                END
                AS NO_Hours_or_Miles
                , CASE WHEN (CASE WHEN mh.Delta_Pos_day < 4 THEN 'True' ELSE 'False' END) = 'False'  
                THEN 1
                ELSE 0
                END
                AS NO_Location
                
                FROM 
                WSDATA.GPSSIMFL gps
                LEFT JOIN
                cte_GPS_Calculations mh
                    ON TRIM(gps.GISIM) = mh.GISIM
                    AND gps.GISTTS = mh.GISTTS
            
                WHERE
                '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                AND gps.GICMP <> 'ZZ'
                --gps.GICMP = 'U1'
                --AND gps.GISTTS = 'A'
            )nhl
            ON sim.GISIM = nhl.GISIM    
            AND sim.GISTTS = nhl.GISTTS  --  GISTTS join is needed due to multiple ESN duplication entries - see ESN 00000000004662168805
            

            LEFT JOIN
            -- Select all sim values that qualify as 'HOURS CAN Override - ALL Perm Active Devices Installed on Rental Machines'
            -- Extra lines of filtering added to standard filters used throughout all select statements 
            (
                SELECT
                TRIM(gps.GISIM) AS GISIM
                , gps.GISTTS
                , CASE WHEN
                    (CASE WHEN mh.Mileage_Hour_Code = 'H' AND (CASE WHEN(mh.Days_Since_Last_Meter_Reading) < 4 THEN '1' ELSE '0' end) = '0' THEN 'False' 
                    WHEN
                    (CASE WHEN mh.Mileage_Hour_Code = 'M' AND GILSRC = 'GEO' 
                            THEN mh.Days_Since_Last_Mile_Reading  
                            ELSE mh.Days_Since_Last_Meter_Reading END) < 4 THEN 'True' 
                    ELSE 'False'          
                    END) = 'False'     
                AND 
                    (CASE WHEN mh.Delta_Pos_day < 4 THEN 'True' ELSE 'False' END) = 'True'  
                THEN 1 
                ELSE 0
                END
                AS Hours_CAN_Override
            
                FROM 
                WSDATA.GPSSIMFL gps
                LEFT JOIN
                cte_GPS_Calculations mh
                    ON TRIM(gps.GISIM) = mh.GISIM
                    AND gps.GISTTS = mh.GISTTS
                LEFT JOIN 
                WSDATA.GPSMODFL m
                    ON --m.GLCMP = 'U1'
                    m.G1MODL = gps.GIMODL
                    AND m.G1LSRC = gps.GILSRC
                --LEFT JOIN 
                --WSDATA.EQPMASFL eqp
                    --ON --eqp.EMCMP = 'U1'
                    --eqp.EMEQP# = gps.GIEQP#
                --LEFT JOIN 
                --WSDATA.EQPCCMFL cc
                    --ON --cc.ECCMP = 'U1'
                    --cc.ECCATG = eqp.EMCATG
                    --AND cc.ECCLAS = eqp.EMCLAS
                
                WHERE 
                '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                AND gps.GICMP <> 'ZZ'
                --gps.GICMP = 'U1'
                --AND gps.GISTTS = 'A' -- Include devices that are Active only
                --AND gps.GIEQP# <> '' -- Use this to indicate if the device is married to a machine or not.
                --AND gps.GIMTR2 <> 'Y' -- Exlcude the secondary devices such as EAM
                --AND m.G1PINS = 'Y' --  Exclude devices that are Permanent installed and not a slap and track device 
                --AND eqp.EMTYPE IN ('R', 'S') -- Include only devices in type Rental or Subleased
                --AND eqp.EMSTAT NOT IN ('S', 'J', 'M', 'T', 'V') -- Exclude devices on machines that are Sold, etc.
                AND m.G11939 = 'Y'
                AND gps.GIERYN = 'N'
                AND gps.GILMCD = gps.GIMRDT
            ) can
            ON sim.GISIM = can.GISIM  
            AND sim.GISTTS = can.GISTTS      --  GISTTS join is needed due to multiple ESN duplication entries - see ESN 00000000004662168805


            LEFT JOIN
            -- Select all sim values that qualify as'HOURS BATTERY Override - ALL Perm Active Devices Installed on Rental Machines'
            -- Extra lines of filtering added to standard filters used throughout all select statements 
            (
                SELECT
                TRIM(gps.GISIM) AS GISIM
                , gps.GISTTS
                , CASE WHEN
                    (CASE WHEN mh.Mileage_Hour_Code = 'H' AND (CASE WHEN(mh.Days_Since_Last_Meter_Reading) < 4 THEN '1' ELSE '0' end) = '0' THEN 'False'
                    WHEN
                        (CASE WHEN mh.Mileage_Hour_Code = 'M' AND gps.GILSRC = 'GEO' 
                            THEN mh.Days_Since_Last_Mile_Reading  
                            ELSE mh.Days_Since_Last_Meter_Reading END) < 4 THEN 'True' 
                    ELSE 'False'          
                    END) = 'False' 
                AND
                (CASE WHEN mh.Delta_Pos_day < 4 THEN 'True' ELSE 'False' END) = 'False'
                THEN 1 
                ELSE 0
                END
                AS Hours_Battery_Override
            
                FROM 
                WSDATA.GPSSIMFL gps
                LEFT JOIN
                cte_GPS_Calculations mh
                    ON TRIM(gps.GISIM) = mh.GISIM
                    AND gps.GISTTS = mh.GISTTS
                --LEFT JOIN 
                --WSDATA.GPSMODFL m
                    --ON --m.GLCMP = 'U1'
                    --m.G1MODL = gps.GIMODL
                    --AND m.G1LSRC = gps.GILSRC
                --LEFT JOIN 
                --WSDATA.EQPMASFL eqp
                    --ON --eqp.EMCMP = 'U1'
                    --eqp.EMEQP# = gps.GIEQP#
                --LEFT JOIN 
                --WSDATA.EQPCCMFL cc
                    --ON --cc.eccmp = 'U1'
                    --cc.ECCATG = eqp.EMCATG
                --AND cc.ECCLAS = eqp.EMCLAS
                WHERE 
            '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                    AND gps.GICMP <> 'ZZ'
                --gps.GICMP = 'U1'
                    --gps.gistts = 'A' -- Include devices that are Active only
                    --gps.gieqp# <> '' -- Use this to indicate if the device is married to a machine or not.
                    --gps.gimtr2 <> 'Y' -- Exlcude the secondary devices such as EAM
                    --m.g1pins = 'Y' --  Exclude devices that are Permanent installed and not a slap and track device 
                    --eqp.emtype IN ('R', 'S') -- Include only devices in type Rental or Subleased
                    --eqp.emstat NOT IN ('S', 'J', 'M', 'T', 'V') -- Exclude devices on machines that are Sold, etc.
                    AND gps.GIRBVL BETWEEN .1 AND 9.3
                    AND gps.GIRBDT = gps.GIPGDT
            ) bat
            ON sim.GISIM = bat.GISIM    
            AND sim.GISTTS = bat.GISTTS    --  GISTTS join is needed due to multiple ESN duplication entries - see ESN 00000000004662168805
            

            LEFT JOIN
            -- Select all sim values that qualify as 'LOCATION LOS Override - ALL Perm Active Devices Installed on Rental Machines'
            -- Extra lines of filtering added to standard filters used throughout all select statements 
            (
                SELECT
                TRIM(gps.GISIM) AS GISIM
                , gps.GISTTS
                , CASE WHEN
                    (CASE WHEN mh.Mileage_Hour_Code = 'H' AND (CASE WHEN(mh.Days_Since_Last_Meter_Reading) < 4 THEN '1' ELSE '0' end) = '0' THEN 'False' 
                    WHEN
                        (CASE WHEN mh.Mileage_Hour_Code = 'M' AND gps.GILSRC = 'GEO' 
                            THEN mh.Days_Since_Last_Mile_Reading  
                            ELSE mh.Days_Since_Last_Meter_Reading END) < 4 THEN 'True' 
                    ELSE 'False'          
                    END) = 'True'          
                AND
                (CASE WHEN mh.Delta_Pos_day < 4 THEN 'True' ELSE 'False' END) = 'False'
                THEN 1 
                ELSE 0
                END
                AS Location_LOS_Override
            
                FROM 
                WSDATA.GPSSIMFL gps
                LEFT JOIN
                cte_GPS_Calculations mh
                    ON TRIM(gps.GISIM) = mh.GISIM
                    AND gps.GISTTS = mh.GISTTS
                --LEFT JOIN 
                --WSDATA.GPSMODFL m
                    --ON --m.G1CMP = 'U1'
                    --m.G1MODL = gps.GIMODL
                    --AND m.G1LSRC = gps.GILSRC
                LEFT JOIN 
                WSDATA.EQPMASFL eqp
                    ON eqp.EMCMP <> 'ZZ'
                    AND eqp.EMEQP# = gps.GIEQP#
                --LEFT JOIN 
                --WSDATA.EQPCCMFL cc
                    --ON --cc.ECCMP = 'U1'
                    --cc.ECCATG = eqp.EMCATG
                    --AND cc.ECCLAS = eqp.EMCLAS
                
                WHERE 
                '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                AND gps.gicmp <> 'ZZ'
                -- gps.gicmp = 'U1'
                -- AND gps.gistts = 'A' -- Include devices that are Active only
                -- AND gps.gieqp# <> '' -- Use this to indicate if the device is married to a machine or not.
                -- AND gps.gimtr2 <> 'Y' -- Exlcude the secondary devices such as EAM
                -- AND m.g1pins = 'Y' --  Exclude devices that are Permanent installed and not a slap and track device 
                -- AND eqp.emtype IN ('R', 'S') -- Include only devices in type Rental or Subleased
                -- AND eqp.emstat NOT IN ('S', 'J', 'M', 'T', 'V') -- Exclude devices on machines that are Sold, etc.
                AND eqp.emstat IN ('O', 'U') -- the machine can only be on rent
                AND eqp.emcatg IN(300,310)
                ) los
            ON sim.GISIM = los.GISIM
            AND sim.GISTTS = los.GISTTS      --  GISTTS join is needed due to multiple ESN duplication entries - see ESN 00000000004662168805
            

            UNION ALL
            
                
            -- EQUIPMENT WITHOUT GPS AND NEEDS INSTALL DATA EXTRACT 
            SELECT DISTINCT 
                '' AS ESN#
                ,  TRIM(eqp.emeqp#) AS "Equipment Code"
                , '' "Device Status"
                , '' "Device Model"
                , '' "Device Package"
                , '' AS "Last Ping"
                , '' AS "Last Lat/Long Date"
                , '' AS "Last Meter Reading Date"
                , '' AS "Last Meter Change Date"
                , 'UNHEALTHY' AS "Device Health"
                , CASE gps.ginote
                    WHEN '' THEN 'NI=Need Install'
                    WHEN '3G TARGET' THEN '3G Upgrade'
                    ELSE 'NI=Need Install'
                    END 
                    AS "Health Reason"
            FROM WSDATA.EQPMASFL eqp
            LEFT JOIN WSDATA.EQPCCMFL AS ccl 
                ON ccl.eccmp <> 'ZZ'
                    AND ccl.ECCATG = eqp.emcatg
                    AND ccl.ECCLAS = eqp.emclas
            LEFT JOIN WSDATA.GPSSIMFL gps
                ON gps.gicmp <> 'ZZ'
                AND gps.GIEQP# = eqp.emeqp#
            LEFT JOIN WSDATA.GPSMODFL gpm
            ON gpm.G1CMP <> 'ZZ'
                AND gpm.G1MODL = gps.GIMODL
            AND gpm.g1lsrc = gps.gilsrc
            WHERE 
                '{where_clause_filter}' IN (gps.GIEQP#,gps.GISIM,LTRIM(gps.GISIM,'0'))  ---???????????  FILTER VALUE
                AND eqp.emcmp <> 'ZZ'
                -- eqp.emcmp = 'U1'
                AND eqp.emstat NOT IN ('S', 'J', 'M', 'V', 'T') 
                AND eqp.emtype IN ('R', 'S')
                AND eqp.emrulf <> 'Y' 
                AND (gps.gisim IS NULL OR (gps.ginote = '3G TARGET' AND gps.gilsrc <> 'TRK') OR (gps.gisim IS NOT NULL AND gpm.g1pins <> 'Y'))
                AND ccl.ECGPS = 'Y'
            
            )AllData
                
            --WHERE 
            --'11261419'  IN (AllData."Equipment Code",AllData.ESN#,LTRIM(AllData.ESN#,'0'))
            --AllData."Equipment Code" = '11261419' OR AllData.ESN# = '11261419'

            ORDER BY "Last Ping" DESC
            FETCH FIRST 1 ROW ONLY
        """
            return sql_query



def rentalman_connect(query):
            rm_conn = pyodbc.connect(driver='{IBM i Access ODBC Driver}', system='Query.ur.com',
            user = os.getenv('RM_U'),password = os.getenv('RM_P'))
                                     #,user=os.getenv('RM_U'),password=os.getenv('RM_P'))
            rm_c1 = rm_conn.cursor()

            rm_c1.execute(query)
            results = rm_c1.fetchall()

            df = pd.DataFrame.from_records(results, columns=[x[0] for x in rm_c1.description])

            return df

def Ping():
    st.markdown("<h1 style='text-align: left; color: Black;'>Information Retrieval Tool</h1>", unsafe_allow_html=True)
    if where:=st.chat_input('Enter Equipment Code or Device SIM',key='where'):
        with st.spinner('Thinking...'):
            
            df = rentalman_connect(new_function(where))
            if not df.empty:
                #st.dataframe(df)
                st.write('ESN#:',df['ESN#'][0])
                st.write('Equipment Code:',df['Equipment Code'][0])
                st.write('Device Status:',df['Device Status'][0])
                st.write('Device Model:',df['Device Model'][0])
                st.write('Device Package:',df['Device Package'][0])
                st.write('Last Ping:',df['Last Ping'][0])
                st.write('Last Lat/Long Date:',df['Last Lat/Long Date'][0])
                st.write('Last Meter Reading Date:',df['Last Meter Reading Date'][0])
                st.write('Last Meter Change Date:',df['Last Meter Change Date'][0])
                st.write('Device Health:',df['Device Health'][0])
                st.write('Health Reason:',df['Health Reason'][0])
                snowflake_logging(prompt_id='Ping', model_name='Ping - RentalMan', question=where, answer='Query on RM')
            else:
                st.write('No information found, please ensure your input is void of any typos')