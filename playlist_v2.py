import pandas as pd
import os
from datetime import timedelta

# --- FUNCIONES DE UTILIDAD ---

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

# --- MÓDULOS DEL PROGRAMA ---

def menu_biblioteca(db):
    """Opción 1: Añadir temas a la base de datos sin crear playlist"""
    print("\n--- 📚 GESTIÓN DE BIBLIOTECA ---")
    while True:
        busqueda = input("\nArtista para añadir temas (o 'q' para volver al menú): ").strip()
        if busqueda.lower() == 'q': break
        
        # Normalizamos el nombre del artista (si existe en DB, usamos el existente)
        coincidencias = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()
        if len(coincidencias) > 0:
            print("Artistas encontrados:")
            for idx, n in enumerate(coincidencias): print(f"{idx+1}. {n}")
            sel = input("Selecciona número (o Enter para usar nombre nuevo): ")
            artista_final = coincidencias[int(sel)-1] if sel.isdigit() and int(sel) <= len(coincidencias) else busqueda.upper()
        else:
            artista_final = busqueda.upper()

        while True:
            print(f"\n📍 Añadiendo temas a: {artista_final}")
            titulo = input("  Título del tema (o 'v' para cambiar de artista): ").strip().upper()
            if titulo.lower() == 'v': break
            
            duracion = input("  Duración (MM:SS): ").strip()
            td = formatear_duracion(duracion)
            
            nueva_fila = pd.DataFrame([{'ARTISTA': artista_final, 'TITULO': titulo, 'DURACION': td_a_string(td)}])
            db = pd.concat([db, nueva_fila], ignore_index=True).drop_duplicates()
            print(f"✅ Guardado: {titulo}")
    
    return db

def menu_playlist(db):
    """Opción 2: Crear playlist (tu lógica original mejorada)"""
    print("\n--- 🎧 CREACIÓN DE PLAYLIST ---")
    seleccionados = []
    tiempo_total = timedelta(0)
    
    while True:
        print(f"\n⏱️ ACUMULADO: {td_a_string(tiempo_total)}")
        busqueda = input("Busca un ARTISTA (o 'q' para finalizar): ").strip()
        if busqueda.lower() == 'q': break
        if not busqueda: continue
            
        artistas_coincidentes = db[db['ARTISTA'].str.contains(busqueda, case=False, na=False)]['ARTISTA'].unique()

        if len(artistas_coincidentes) == 0:
            print(f"⚠️ El artista '{busqueda.upper()}' no existe.")
            continue

        print("\nArtistas coincidentes:")
        for idx, nombre in enumerate(artistas_coincidentes):
            print(f"{idx + 1} - {nombre}")

        try:
            sel_art = input("\nSelecciona número: ")
            if not sel_art: continue
            
            artista_elegido = artistas_coincidentes[int(sel_art) - 1]
            canciones = db[db['ARTISTA'] == artista_elegido].reset_index(drop=True)
            
            print(f"\nTemas de: {artista_elegido}")
            for i, fila in canciones.iterrows():
                print(f"  {i + 1} > {fila['TITULO']} [{fila['DURACION']}]")
            
            sel_tem = input(f"\nElige un tema (Enter para volver): ")
            if not sel_tem: continue
            
            idx = int(sel_tem) - 1
            if 0 <= idx < len(canciones):
                fila_sel = canciones.iloc[[idx]].copy()
                dur_td = formatear_duracion(fila_sel.iloc[0]['DURACION'])
                seleccionados.append(fila_sel)
                tiempo_total += dur_td
                print(f"✅ Añadido a playlist: {fila_sel.iloc[0]['TITULO']}")
        except:
            print("❌ Selección no válida.")
            
    return seleccionados, tiempo_total

# --- FLUJO PRINCIPAL ---

def ejecutar():
    archivo_csv_db = 'playlist.csv' # Usamos el CSV como base de datos permanente
    archivo_excel_final = 'mi_playlist_seleccionada.xlsx'

    # Cargar base de datos existente o crear una vacía
    if os.path.exists(archivo_csv_db):
        db = pd.read_csv(archivo_csv_db)
    else:
        db = pd.DataFrame(columns=['ARTISTA', 'TITULO', 'DURACION'])

    while True:
        print("\n" + "="*30)
        print("   GESTOR DE MÚSICA v4")
        print("="*30)
        print("1. Gestionar Biblioteca (Añadir temas)")
        print("2. Crear nueva Playlist")
        print("3. Salir")
        
        opcion = input("\nElige una opción: ").strip()

        if opcion == '1':
            db = menu_biblioteca(db)
            db.to_csv(archivo_csv_db, index=False, encoding='utf-8-sig')
            print("\n💾 Biblioteca actualizada.")
            
        elif opcion == '2':
            if db.empty:
                print("⚠️ La biblioteca está vacía. Añade temas primero.")
                continue
            lista_playlist, tiempo = menu_playlist(db)
            if lista_playlist:
                pd.concat(lista_playlist, ignore_index=True).to_excel(archivo_excel_final, index=False)
                print(f"\n🎉 Playlist guardada. Total: {td_a_string(tiempo)}")
        
        elif opcion == '3':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    ejecutar()