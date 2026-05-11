import os
import glob
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
############################### ERROR DE DISTANCIA #################################################
# Carpeta donde están los CSV
csv_dir =  r"/home/usuario/Documentos/inf_robot_verde/CSV_ROBOT"

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_ErrorDist_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

out_dir  = r"/home/usuario/Documentos/inf_robot_verde/CSV_ROBOT"
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Error_Distancia"], label=" Error_Distancia ") #CAMBIAR NOMBRE DE COLUMNA
plt.xlabel("Tiempo [s]")
plt.ylabel("Error_Distancia")
plt.grid(True)
plt.legend()
plt.ylim(df["Error_Distancia"].min(), df["Error_Distancia"].max())
png_path = os.path.join(out_dir, "Error_Distancia.png") #CAMBIAR NOMBRE DE IMAGEN
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")
#############################################  IMU HEADING ##########################################################
# Carpeta donde están los CSV

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_imu_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["imu_heading"], label="imu_heading") 
plt.xlabel("Tiempo [s]")
plt.ylabel("imu_heading")
plt.grid(True)
plt.legend()
plt.ylim(df["imu_heading"].min(), df["imu_heading"].max())

png_path = os.path.join(out_dir, "imu_heading.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")

######################################### IMU ERROR YAW ####################################################
# Carpeta donde están los CSV

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_ImuError_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Imu_Error_yaw"], label="Imu_Error_yaw") 
plt.xlabel("Tiempo [s]")
plt.ylabel("Imu_Error_yaw")
plt.grid(True)
plt.legend()
plt.ylim(df["Imu_Error_yaw"].min(), df["Imu_Error_yaw"].max())

png_path = os.path.join(out_dir, "Imu_Error_yaw.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")
 ####################################### LECTURAS VALIDAS LIDAR CONO ROJO ###############################################
# Carpeta donde están los CSV

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_LecValRojo_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Lecturas_ValidasRojo"], label="Lecturas_ValidasRojo") 
plt.xlabel("Tiempo [s]")
plt.ylabel("Lecturas_ValidasRojo")
plt.grid(True)
plt.legend()
plt.ylim((df["Lecturas_ValidasRojo"].min())-1, (df["Lecturas_ValidasRojo"].max())+1)

png_path = os.path.join(out_dir, "Lecturas_ValidasRojo.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")

 ####################################### LECTURAS VALIDAS LIDAR CONO VERDE ###############################################
# Carpeta donde están los CSV

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_LecValVerde_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Lecturas_ValidasVerde"], label="Lecturas_ValidasVerde") 
plt.xlabel("Tiempo [s]")
plt.ylabel("Lecturas_ValidasVerde")
plt.grid(True)
plt.legend()
plt.ylim(0, df["Lecturas_ValidasVerde"].max())

png_path = os.path.join(out_dir, "Lecturas_ValidasVerde.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")

###################################### LIDAR LEFT DISTANCIA MEDIDA ######################################################
# Carpeta donde están los CSV

# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_LidarLeft_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Lidar_Left"], label="Lidar_Left") 
plt.xlabel("Tiempo [s]")
plt.ylabel("Lidar_Left")
plt.grid(True)
plt.legend()
plt.ylim((df["Lidar_Left"].min())-0.1, (df["Lidar_Left"].max())+0.1)

png_path = os.path.join(out_dir, "Lidar_Left.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")


############################################## OMEGA 1 ###################################################
# Carpeta donde están los CSV
# Buscar el más reciente que empiece por csv_omega2_
pattern = os.path.join(csv_dir, "csv_omega1_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["omega_1"], label="omega_1") 
plt.xlabel("Tiempo [s]")
plt.ylabel("omega_1")
plt.grid(True)
plt.legend()
plt.ylim((df["omega_1"].min())-5, (df["omega_1"].max())+5)

png_path = os.path.join(out_dir, "omega_1.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")


############################################# VELOCIDAD DESEADA #################################################
# Carpeta donde están los CSV
pattern = os.path.join(csv_dir, "csv_VelDes_*.csv")
files = glob.glob(pattern)

if not files:
    raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern}")

# Ordenar por fecha de modificación y quedarte con el último
files.sort(key=os.path.getmtime, reverse=True)
csv_path = files[0]

os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)

# tiempo relativo para que empiece en 0 s
t0 = df["ros_time_s"].iloc[0]
df["t_rel_s"] = df["ros_time_s"] - t0

plt.figure()
plt.plot(df["t_rel_s"], df["Vel_Des"], label="Vel_Des") 
plt.xlabel("Tiempo [s]")
plt.ylabel("Vel_Des")
plt.grid(True)
plt.legend()

plt.ylim((df["Vel_Des"].min())-5, (df["Vel_Des"].max())+5)

png_path = os.path.join(out_dir, "Pos_Des.png") 
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")


###################################### Comparacion Velocidad deseada y Omega


# --- Función para buscar el CSV más reciente dado un patrón ---
def cargar_csv_mas_reciente(csv_dir, patron):
    files = glob.glob(os.path.join(csv_dir, patron))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos con patrón {patron}")
    files.sort(key=os.path.getmtime, reverse=True)
    return pd.read_csv(files[0])

# Carpeta base

# Cargar CSV velocidad deseada
df_vel_des = cargar_csv_mas_reciente(csv_dir, "csv_VelDes_*.csv")

# Cargar CSV omega
df_omega1 = cargar_csv_mas_reciente(csv_dir, "csv_omega1_*.csv")

# Ajustar tiempo relativo (en base al primero de cada serie)
t0_vel = df_vel_des["ros_time_s"].iloc[0]
t0_omega1 = df_omega1["ros_time_s"].iloc[0]
df_vel_des["t_rel_s"] = df_vel_des["ros_time_s"] - t0_vel
df_omega1["t_rel_s"] = df_omega1["ros_time_s"] - t0_omega1

# --- Graficar en la misma figura ---
plt.figure()
plt.plot(df_vel_des["t_rel_s"], df_vel_des["Vel_Des"], label="Posicion deseada [rad/s]", color="orange")
plt.plot(df_omega1["t_rel_s"], df_omega1["omega_1"], label="Posicion medida [rad/s]", color="blue")
plt.xlabel("Tiempo [s]")
plt.ylabel("Posicion deseada vs Posicion [rad/s]")
plt.title("Comparación: Posicion deseada vs Posicion")
plt.grid(True)
plt.legend()

# Ajustar Y desde 0 hasta el máximo de ambas señales
y_max = max(df_vel_des["Vel_Des"].max(), df_omega1["omega_1"].max())
y_min = min(df_vel_des["Vel_Des"].min(), df_omega1["omega_1"].min())
plt.ylim((y_min-10), (y_max+10))

# Guardar figura
png_path = os.path.join(csv_dir, "pos_deseada_vs_omega1.png")
plt.savefig(png_path, dpi=160, bbox_inches="tight")
print(f"✅ Gráfica guardada en: {png_path}")
