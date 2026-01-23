import pandas as pd
import os
from datetime import datetime, timedelta

def formatear_duracion(tiempo):
    """Convierte entradas a formato HH:MM:SS y retorna un objeto timedelta"""
    tiempo = str(tiempo).strip()
    try:
        partes = tiempo.split(':')
        if len(partes) == 1:
            h, m, s = 0, 0, int(partes[0])
        elif len(partes) == 2:
            h, m, s = 0, int(partes[0]), int(partes[1])
        elif len(partes) == 3:
            h, m, s = int(partes[0]), int(partes[1]), int(partes[2])
        else:
            h, m, s = 0, 0, 0
        return timedelta(hours=h, minutes=m, seconds=s)
    except:
        return timedelta(0)

def td_a_string(td):
    """Convierte timedelta a string HH:MM:SS"""
    total_segundos = int(td.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

def generar_csv_limpio(archivo_excel, archivo_csv):
    """Lee todas las pestañas del Excel y genera un CSV consolidado"""
    try:
        print("\n🔄 Actualizando base de datos CSV...")
        dict_pestañas = pd.read_excel(archivo_excel, sheet_name=None)
        lista_tablas = []
        
        for _, df in dict_pestañas.items():
            df.columns = df.columns.str.strip().str.upper()
            cols_necesarias = ['ARTISTA', 'TITULO', 'DURACION']
            for col in cols_necesarias:
                if col not in df.columns: df[col] = "N/A"
            
            df_filtrado = df[cols_necesarias].copy()
            df_filtrado = df_filtrado[df_filtrado['ARTISTA'].notna()]
            df_filtrado = df_filtrado[~df_filtrado['ARTISTA'].astype(str).str.contains('TOTAL', case=False)]
            lista_tablas.append(df_filtrado)

        consolidado = pd.concat(lista_tablas, ignore_index=True).drop_duplicates()
        consolidado.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
        print(f"✅ Base de datos '{archivo_csv}' actualizada ({len(consolidado)} temas).")
    except Exception as e:
        print(f"❌ Error al actualizar CSV: {e}")

def ejecutar_todo():
    archivo_excel_origen = 'SESIONES_PINCHADAS.xlsx' 
    archivo_csv_db = 'playlist.csv'
    ahora = datetime.now().strftime("%y%m%d_%H%M%S")
    nombre_pestaña = f"SESION_{ahora}"

    if not os.path.exists(archivo_excel_origen):
        print(f"❌ Error: No se encuentra '{archivo_excel_origen}'")
        return

    # --- CARGA INICIAL ---
    try:
        dict_pestañas = pd.read_excel(archivo_excel_origen, sheet_name=None)
        lista_tablas = []
        for _, df in dict_pestañas.items():
            df.columns = df.columns.str.strip().str.upper()
            for c in ['ARTISTA', 'TITULO', 'DURACION']:
                if c not in df.columns: df[c] = "N/A"
            lista_tablas.append(df[['ARTISTA', 'TITULO', 'DURACION']].copy().dropna(subset=['ARTISTA']))
        db = pd.concat(lista_tablas, ignore_index=True).drop_duplicates()
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return

    seleccionados = []
    tiempo_total = timedelta(0)
    
    print("\n" + "="*45)
    print("🎵 GESTOR DE SESIONES v3.5 🎵")
    print("="*45)

    while True:
        print(f"\n⏱️ ACUMULADO: {td_a_string(tiempo_total)}")
        busqueda = input("Busca un ARTISTA (o 'salir'): ").strip()
        if busqueda.lower() in ['salir', 'exit']: break
        if not busqueda: continue
            
        artistas_coincidentes = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()

        if len(artistas_coincidentes) == 0:
            print(f"⚠️ El artista '{busqueda.upper()}' no existe.")
            if input(f"¿Crear nuevo? (s/n): ").lower() == 's':
                artista_nuevo = busqueda.upper()
                nuevo_tit = input("TITULO: ").strip().upper()
                nueva_dur = input("DURACION (MM:SS): ").strip()
                td = formatear_duracion(nueva_dur)
                nueva_fila = pd.DataFrame([{'ARTISTA': artista_nuevo, 'TITULO': nuevo_tit, 'DURACION': td_a_string(td)}])
                seleccionados.append(nueva_fila)
                db = pd.concat([db, nueva_fila], ignore_index=True)
                tiempo_total += td
            continue

        print("\nCoincidencias:")
        for idx, nombre in enumerate(artistas_coincidentes):
            print(f"{idx + 1} - {nombre}")

        try:
            sel_art = input("\nSelecciona número: ")
            if not sel_art: continue
            
            artista_elegido = artistas_coincidentes[int(sel_art) - 1]
            canciones = db[db['ARTISTA'] == artista_elegido].reset_index(drop=True)
            
            for i, fila in canciones.iterrows():
                print(f"  {i + 1} > {fila['TITULO']} [{fila['DURACION']}]")
            print(f"  {len(canciones) + 1} > [AÑADIR NUEVO TEMA]")

            sel_tem = input(f"\nElige tema: ")
            if not sel_tem: continue
            opcion_idx = int(sel_tem) - 1

            if opcion_idx == len(canciones):
                nuevo_tit = input(f"TÍTULO: ").strip().upper()
                nueva_dur = input("DURACIÓN: ").strip()
                td = formatear_duracion(nueva_dur)
                nueva_fila = pd.DataFrame([{'ARTISTA': artista_elegido, 'TITULO': nuevo_tit, 'DURACION': td_a_string(td)}])
                seleccionados.append(nueva_fila)
                db = pd.concat([db, nueva_fila], ignore_index=True)
                tiempo_total += td
            elif 0 <= opcion_idx < len(canciones):
                fila_sel = canciones.iloc[[opcion_idx]].copy()
                tiempo_total += formatear_duracion(fila_sel.iloc[0]['DURACION'])
                seleccionados.append(fila_sel)
        except:
            print("❌ Error en selección.")

    # --- GUARDADO FINAL ---
    if seleccionados:
        df_sesion = pd.concat(seleccionados, ignore_index=True)
        
        # Guardar en el Excel original como nueva pestaña
        try:
            with pd.ExcelWriter(archivo_excel_origen, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_sesion.to_excel(writer, sheet_name=nombre_pestaña, index=False)
            print(f"\n💾 Pestaña '{nombre_pestaña}' añadida a {archivo_excel_origen}")
            
            # Ejecutar la limpieza y actualización del CSV
            generar_csv_limpio(archivo_excel_origen, archivo_csv_db)
            
        except Exception as e:
            print(f"❌ Error al guardar en Excel: {e}")
    else:
        print("\nCerrando sin cambios.")

if __name__ == "__main__":
    ejecutar_todo()
