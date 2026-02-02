import pandas as pd
import os
from datetime import timedelta

# --- FUNCIONES DE UTILIDAD ---

def formatear_duracion(tiempo):
    tiempo = str(tiempo).strip()
    try:
        partes = tiempo.split(':')
        if len(partes) == 1: h, m, s = 0, 0, int(partes[0])
        elif len(partes) == 2: h, m, s = 0, int(partes[0]), int(partes[1])
        elif len(partes) == 3: h, m, s = int(partes[0]), int(partes[1]), int(partes[2])
        else: h, m, s = 0, 0, 0
        return timedelta(hours=h, minutes=m, seconds=s)
    except:
        return timedelta(0)

def td_a_string(td):
    total_segundos = int(td.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# --- MÓDULOS DEL PROGRAMA ---

def menu_biblioteca(db):
    while True:
        print("\n" + "-"*25)
        print("📚 MANTENIMIENTO DE BIBLIOTECA")
        print("-"*25)
        print("1. Añadir nuevos temas")
        print("2. Editar/Eliminar temas existentes")
        print("3. Volver al menú principal")
        
        sub_opcion = input("\nSelecciona: ").strip()

        if sub_opcion == '1':
            db = añadir_temas(db)
        elif sub_opcion == '2':
            db = editar_biblioteca(db)
        elif sub_opcion == '3':
            break
    return db

def añadir_temas(db):
    while True:
        busqueda = input("\nArtista (o 'v' para volver): ").strip()
        if busqueda.lower() == 'v': break
        
        coincidencias = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()
        if len(coincidencias) > 0:
            print("Artistas encontrados:")
            for idx, n in enumerate(coincidencias): print(f"{idx+1}. {n}")
            sel = input("Selecciona número (o Enter para nombre nuevo): ")
            artista_final = coincidencias[int(sel)-1] if sel.isdigit() and int(sel) <= len(coincidencias) else busqueda.upper()
        else:
            artista_final = busqueda.upper()

        while True:
            titulo = input(f"  [{artista_final}] Nuevo título (o 'v' para cambiar artista): ").strip().upper()
            if titulo.lower() == 'v': break
            duracion = input("  Duración (MM:SS): ").strip()
            td = formatear_duracion(duracion)
            
            nueva_fila = pd.DataFrame([{'ARTISTA': artista_final, 'TITULO': titulo, 'DURACION': td_a_string(td)}])
            db = pd.concat([db, nueva_fila], ignore_index=True).drop_duplicates()
            print(f"✅ Registrado.")
    return db

def editar_biblioteca(db):
    busqueda = input("\nBusca el artista del tema a editar: ").strip()
    artistas = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()
    
    if len(artistas) == 0:
        print("❌ No se encontró el artista.")
        return db

    for idx, n in enumerate(artistas): print(f"{idx+1}. {n}")
    sel_a = input("Selecciona artista: ")
    if not sel_a.isdigit(): return db
    
    artista_sel = artistas[int(sel_a)-1]
    # Obtenemos los índices originales para poder modificar el DataFrame global
    indices = db[db['ARTISTA'] == artista_sel].index
    temas_artista = db.loc[indices].reset_index()

    print(f"\nTemas de {artista_sel}:")
    for i, fila in temas_artista.iterrows():
        print(f"  {i+1}. {fila['TITULO']} ({fila['DURACION']})")
    
    sel_t = input("\nSelecciona número para EDITAR (o 'e' + número para ELIMINAR, ej: e1): ").strip()
    
    try:
        if sel_t.startswith('e'):
            idx_borrar = int(sel_t[1:]) - 1
            idx_real = temas_artista.loc[idx_borrar, 'index']
            print(f"🗑️ Eliminado: {db.loc[idx_real, 'TITULO']}")
            db = db.drop(idx_real).reset_index(drop=True)
        else:
            idx_edit = int(sel_t) - 1
            idx_real = temas_artista.loc[idx_edit, 'index']
            
            print(f"\nEditando: {db.loc[idx_real, 'TITULO']}")
            nuevo_tit = input("Nuevo título (Enter para mantener): ").strip().upper()
            nueva_dur = input("Nueva duración (Enter para mantener): ").strip()
            
            if nuevo_tit: db.at[idx_real, 'TITULO'] = nuevo_tit
            if nueva_dur: db.at[idx_real, 'DURACION'] = td_a_string(formatear_duracion(nueva_dur))
            print("✅ Cambios guardados.")
    except:
        print("❌ Operación cancelada o error en selección.")
    
    return db

def menu_playlist(db):
    print("\n--- 🎧 CREACIÓN DE PLAYLIST ---")
    seleccionados = []
    tiempo_total = timedelta(0)
    
    while True:
        print(f"\n⏱️ ACUMULADO: {td_a_string(tiempo_total)}")
        busqueda = input("Busca un ARTISTA (o 'q' para finalizar): ").strip()
        if busqueda.lower() == 'q': break
            
        artistas_coincidentes = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()
        if len(artistas_coincidentes) == 0: continue

        for idx, nombre in enumerate(artistas_coincidentes): print(f"{idx + 1} - {nombre}")
        
        sel_art = input("\nSelecciona número: ")
        if not sel_art.isdigit(): continue
        
        artista_elegido = artistas_coincidentes[int(sel_art) - 1]
        canciones = db[db['ARTISTA'] == artista_elegido].reset_index(drop=True)
        
        for i, fila in canciones.iterrows():
            print(f"  {i + 1} > {fila['TITULO']} [{fila['DURACION']}]")
        
        sel_tem = input(f"\nElige un tema (Enter para volver): ")
        if sel_tem.isdigit():
            idx = int(sel_tem) - 1
            if 0 <= idx < len(canciones):
                fila_sel = canciones.iloc[[idx]].copy()
                tiempo_total += formatear_duracion(fila_sel.iloc[0]['DURACION'])
                seleccionados.append(fila_sel)
                print(f"✅ Añadido.")
                
    return seleccionados, tiempo_total

def ejecutar():
    archivo_csv_db = 'playlist.csv'
    archivo_excel_final = 'SESIONES_PINCHADAS.xlsx' # Cambiado al nombre de tu archivo maestro

    db = pd.read_csv(archivo_csv_db) if os.path.exists(archivo_csv_db) else pd.DataFrame(columns=['ARTISTA', 'TITULO', 'DURACION'])

    while True:
        print("\n" + "="*30)
        print("   GESTOR DE MÚSICA v6")
        print("="*30)
        print("1. Biblioteca (Añadir/Editar)")
        print("2. Crear Playlist")
        print("3. Salir")
        
        op = input("\nOpción: ").strip()
        if op == '1':
            db = menu_biblioteca(db)
            db.to_csv(archivo_csv_db, index=False, encoding='utf-8-sig')
        elif op == '2':
            if db.empty: 
                print("⚠️ La biblioteca está vacía.")
                continue
            
            lista, tiempo = menu_playlist(db)
            
            if lista:
                df_final = pd.concat(lista, ignore_index=True)
                # Generamos el nombre de la pestaña con fecha y hora
                nombre_pestaña = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                
                try:
                    # Si el archivo existe, añadimos la pestaña. Si no, lo creamos.
                    if os.path.exists(archivo_excel_final):
                        with pd.ExcelWriter(archivo_excel_final, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            df_final.to_excel(writer, sheet_name=nombre_pestaña, index=False)
                    else:
                        with pd.ExcelWriter(archivo_excel_final, engine='openpyxl') as writer:
                            df_final.to_excel(writer, sheet_name=nombre_pestaña, index=False)
                    
                    print(f"\n✅ Playlist añadida a '{archivo_excel_final}' en la pestaña [{nombre_pestaña}]")
                    print(f"⏱️ Duración total: {td_a_string(tiempo)}")
                except Exception as e:
                    print(f"❌ Error al guardar en Excel: {e}")
                    
        elif op == '3': 
            break

if __name__ == "__main__":
    ejecutar()