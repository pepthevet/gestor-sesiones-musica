import pandas as pd
import os
from datetime import timedelta

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

def ejecutar_todo():
    archivo_excel_origen = 'SESIONES_PINCHADAS.xlsx' 
    archivo_csv_db = 'playlist.csv'
    archivo_excel_final = 'mi_playlist_seleccionada.xlsx'

    if not os.path.exists(archivo_excel_origen):
        print(f"❌ Error: No se encuentra '{archivo_excel_origen}'")
        return

    try:
        dict_pestañas = pd.read_excel(archivo_excel_origen, sheet_name=None)
        lista_tablas = []
        for _, df in dict_pestañas.items():
            df.columns = df.columns.str.strip().str.upper()
            cols = ['ARTISTA', 'TITULO', 'DURACION']
            for c in cols:
                if c not in df.columns: df[c] = "N/A"
            df_limpio = df[cols].copy().dropna(subset=['ARTISTA'])
            lista_tablas.append(df_limpio)
        db = pd.concat(lista_tablas, ignore_index=True).drop_duplicates()
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    seleccionados = []
    tiempo_total = timedelta(0)
    
    print("\n" + "="*45)
    print("🎵 GESTOR DE SESIONES v3 🎵")
    print("="*45)

    while True:
        print(f"\n⏱️ ACUMULADO: {td_a_string(tiempo_total)}")
        busqueda = input("Busca un ARTISTA (o 'salir'): ").strip()
        if busqueda.lower() in ['salir', 'exit']: break
        if not busqueda: continue
            
        artistas_coincidentes = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()

        # --- CASO A: EL ARTISTA NO EXISTE ---
        if len(artistas_coincidentes) == 0:
            print(f"⚠️ El artista '{busqueda.upper()}' no está en la base de datos.")
            if input(f"¿Quieres crearlo y añadir un tema? (s/n): ").lower() == 's':
                # Directamente usamos la búsqueda como nombre de artista
                artista_nuevo = busqueda.upper()
                print(f"Artista: {artista_nuevo}")
                nuevo_tit = input("Introduce el TITULO: ").strip().upper()
                nueva_dur = input("Introduce DURACION (MM:SS): ").strip()
                
                td = formatear_duracion(nueva_dur)
                nueva_fila = pd.DataFrame([{'ARTISTA': artista_nuevo, 'TITULO': nuevo_tit, 'DURACION': td_a_string(td)}])
                
                seleccionados.append(nueva_fila)
                db = pd.concat([db, nueva_fila], ignore_index=True)
                tiempo_total += td
                print(f"✅ Registrado y añadido: {nuevo_tit}")
            continue

        # --- CASO B: ARTISTA ENCONTRADO ---
        print("\nArtistas coincidentes:")
        for idx, nombre in enumerate(artistas_coincidentes):
            print(f"{idx + 1} - {nombre}")

        try:
            sel_art = input("\nSelecciona número (o Enter para nueva búsqueda): ")
            if not sel_art: continue
            
            artista_elegido = artistas_coincidentes[int(sel_art) - 1]
            canciones = db[db['ARTISTA'] == artista_elegido].reset_index(drop=True)
            
            print(f"\nTemas de: {artista_elegido}")
            for i, fila in canciones.iterrows():
                print(f"  {i + 1} > {fila['TITULO']} [{fila['DURACION']}]")
            
            idx_nuevo_tema = len(canciones) + 1
            print(f"  {idx_nuevo_tema} > [AÑADIR NUEVO TEMA PARA {artista_elegido}]")

            sel_tem = input(f"\nElige un tema (Enter para volver): ")
            if not sel_tem: continue
            
            opcion_idx = int(sel_tem) - 1

            if opcion_idx == len(canciones):
                # Añadir tema a artista existente
                nuevo_tit = input(f"Nuevo TÍTULO para {artista_elegido}: ").strip().upper()
                nueva_dur = input("DURACIÓN (MM:SS): ").strip()
                td = formatear_duracion(nueva_dur)
                
                nueva_fila = pd.DataFrame([{'ARTISTA': artista_elegido, 'TITULO': nuevo_tit, 'DURACION': td_a_string(td)}])
                seleccionados.append(nueva_fila)
                db = pd.concat([db, nueva_fila], ignore_index=True)
                tiempo_total += td
                print(f"✅ Añadido: {nuevo_tit}")
            elif 0 <= opcion_idx < len(canciones):
                # Seleccionar tema existente
                fila_sel = canciones.iloc[[opcion_idx]].copy()
                dur_td = formatear_duracion(fila_sel.iloc[0]['DURACION'])
                seleccionados.append(fila_sel)
                tiempo_total += dur_td
                print(f"✅ Añadido: {fila_sel.iloc[0]['TITULO']}")
        except:
            print("❌ Selección no válida.")

    # --- GUARDAR ---
    if seleccionados:
        pd.concat(seleccionados, ignore_index=True).to_excel(archivo_excel_final, index=False)
        db.to_csv(archivo_csv_db, index=False, encoding='utf-8-sig')
        print(f"\n🎉 Sesión guardada en {archivo_excel_final}. Total: {td_a_string(tiempo_total)}")
    else:
        print("\nCerrando sin guardar.")

if __name__ == "__main__":
    ejecutar_todo()
