import database_reader as dr

DataBase = dr.TMEDNetDatabase()
top10_max, top10_min, top10_max_year, top10_min_year = DataBase.create_top_tens(2025)

DataBase.mhw_at_5()

print('hey')
