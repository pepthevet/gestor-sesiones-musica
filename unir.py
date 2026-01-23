import pandas as pd

def generar_csv_limpio():
    archivo_excel = 'SESIONES_PINCHADAS.xlsx'  # Tu archivo con muchas pestañas
    archivo_salida = 'playlist.csv'       # El nombre que espera el segundo script

    try:
        print("Leyendo archivo Excel...")
        # Leer todas las pestañas
        dict_pestañas = pd.read_excel(archivo_excel, sheet_name=None)
        
        lista_tablas = []
        
        for nombre, df in dict_pestañas.items():
            # 1. Limpiar nombres de columnas (quitar espacios y poner en MAYÚSCULAS)
            df.columns = df.columns.str.strip().str.upper()
            
            # 2. Verificar que tiene las columnas necesarias
            columnas_necesarias = ['ARTISTA', 'TITULO', 'DURACION']
            # Si faltan columnas, las crea vacías para que no de error al unir
            for col in columnas_necesarias:
                if col not in df.columns:
                    df[col] = "N/A"
            
            # 3. Solo nos quedamos con las columnas que nos importan
            df_filtrado = df[columnas_necesarias].copy()
            
            # 4. Eliminar filas que son "TOTAL" o están vacías
            df_filtrado = df_filtrado[df_filtrado['ARTISTA'].notna()]
            df_filtrado = df_filtrado[~df_filtrado['ARTISTA'].astype(str).str.contains('TOTAL', case=False)]
            
            lista_tablas.append(df_filtrado)

        # Unir todas las tablas
        consolidado = pd.concat(lista_tablas, ignore_index=True)

        # Eliminar duplicados exactos
        consolidado.drop_duplicates(inplace=True)

        # Guardar como CSV limpio
        # Usamos utf-8-sig para que Excel no rompa los acentos
        consolidado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print(f"--- ¡Éxito! ---")
        print(f"Archivo '{archivo_salida}' generado correctamente.")
        print(f"Total de canciones únicas: {len(consolidado)}")

    except Exception as e:
        print(f"Error procesando el Excel: {e}")

if __name__ == "__main__":
    generar_csv_limpio()