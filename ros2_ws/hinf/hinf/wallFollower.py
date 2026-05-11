#!/usr/bin/env python3
# wall_follower_steer.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os, csv
from datetime import datetime
from collections import deque  # ← PATCH: buffer para reanudación

class WallFollowerSteer(Node):
    def __init__(self):
        super().__init__('wall_follower_steer_fuzzy')

        # ---- CSV (igual que tenías) ----
        self.declare_parameter('csv_dir', os.path.expanduser('~/CSV_ROBOT'))
        self.declare_parameter('ErrorDist_base', 'csv_ErrorDist')
        csv_dir  = self.get_parameter('csv_dir').value
        os.makedirs(csv_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(csv_dir, f"{self.get_parameter('ErrorDist_base').value}_{ts}.csv")
        self.csv_ErrorDist = open(path, 'w', newline='', buffering=1)
        self.writer_ErrorDist = csv.writer(self.csv_ErrorDist)
        self.writer_ErrorDist.writerow(['ros_time_s', 'Error_Distancia'])
        self.get_logger().info(f'Error_Distancia → {path}')

        # ---- Parámetros de control ----
        self.declare_parameter('in_topic', 'lidarLeft')
        self.declare_parameter('out_topic', 'velocidad_deseada')
        self.declare_parameter('setpoint', 1.15)                   ###base
        self.declare_parameter('angle_limit_deg', 45.0)
        self.declare_parameter('dtheta_max_deg', 20.0)

        self.in_topic  = self.get_parameter('in_topic').value
        self.out_topic = self.get_parameter('out_topic').value
        self.setpoint  = float(self.get_parameter('setpoint').value)
        self.AMAX      = float(self.get_parameter('angle_limit_deg').value)
        self.DTHMAX    = float(self.get_parameter('dtheta_max_deg').value)

        # ---- IO ROS ----
        self.sub_dist = self.create_subscription(Float32, self.in_topic, self.cb_lidar, 10)
        self.pub_out  = self.create_publisher(Float32, self.out_topic, 10)
        self.sub_posts= self.create_subscription(Float32, 'Postes', self.cb_posts, 10)
        self.sub_imu  = self.create_subscription(Float32, 'imu_heading', self.cb_imu, 10)
        self.pub_imu_target = self.create_publisher(Float32, 'imu_target_deg', 10)

        # ---- Fuzzy ----
        self._build_fuzzy()

        # ---- Estado ----
        self.steer_prev = 0.0
        self.last_dist  = None
        self.postes     = 0
        self.imu_deg    = 0.0
        self.row_parity = 0 
        # Máquina de estados
        self.mode = 'FOLLOW'      # FOLLOW → PREPARE → TURNING → STOPPED
        self.t_enter = self.get_clock().now()

        # Ventana IMU para parar
        self.imu_win_lo = 180.0
        self.imu_win_hi = 200.0

        # ---- PATCH: Parámetros y buffer para reanudar por estabilidad de LiDAR ----
        self.row_parity = 0                   # 0: sube (objetivo 0°), 1: baja (objetivo 180°)
        self.max_rows = 3        # recorrerá tres filas
        self.row_count = 1       # empieza en la fila 1
        self.initial_imu_params = {}  # guardaremos aquí los valores iniciales para restaurarlos

        self.stop_hold_s = 0.4  # STOP brevísimo: 0.4 s (ajústalo si quieres)
        self.dist_buf = deque(maxlen=10)   # ~0.5 s si el lazo corre a 20 Hz
        self.resume_min_m       = 0.2      # distancia mínima razonable al muro
        self.resume_max_m       = 2.5      # máxima razonable
        self.resume_span_thresh = 0.08     # variación máxima en la ventana (m)
        self.resume_need        = 8        # muestras válidas mínimas en la ventana

        # Timer del lazo (20 Hz aprox.)
        self.create_timer(0.05, self.control_loop)

        self.get_logger().info(
            f'WallFollower listo | in:{self.in_topic} → out:{self.out_topic} | '
            f'setpoint={self.setpoint:.2f} m, sat=±{self.AMAX:.1f}°, dθ_max={self.DTHMAX:.1f}°/ciclo'
        )

    # ---------- Fuzzy ----------
    def _build_fuzzy(self):
        self.err = ctrl.Antecedent(np.arange(-1.0, 1.001, 0.001), 'error')
        self.delta = ctrl.Consequent(np.arange(-45.0, 45.01, 0.01), 'delta')
        self.err['NL'] = fuzz.trimf(self.err.universe, [-1.00, -0.10, -0.02])
        self.err['NS'] = fuzz.trimf(self.err.universe, [-0.06, -0.02,  0.00])
        self.err['Z']  = fuzz.trimf(self.err.universe, [-0.01,  0.00,  0.01])
        self.err['PS'] = fuzz.trimf(self.err.universe, [ 0.00,  0.02,  0.06])
        self.err['PL'] = fuzz.trimf(self.err.universe, [ 0.02,  0.10,  1.00])
        self.delta['LL'] = fuzz.trimf(self.delta.universe, [-45, -45, -20])
        self.delta['LS'] = fuzz.trimf(self.delta.universe, [-25, -10,   0])
        self.delta['Z']  = fuzz.trimf(self.delta.universe, [  -3,   0,   3])
        self.delta['RS'] = fuzz.trimf(self.delta.universe, [   0,  10,  25])
        self.delta['RL'] = fuzz.trimf(self.delta.universe, [  20,  45,  45])
        rules = [
            ctrl.Rule(self.err['NL'], consequent=self.delta['LL']),
            ctrl.Rule(self.err['NS'], consequent=self.delta['LS']),
            ctrl.Rule(self.err['Z'],  consequent=self.delta['Z']),
            ctrl.Rule(self.err['PS'], consequent=self.delta['RS']),
            ctrl.Rule(self.err['PL'], consequent=self.delta['RL']),
        ]
        self.sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

    # ---------- Callbacks de entrada ----------
    def cb_imu(self, msg: Float32):
        # Normaliza IMU a [0,360)
        self.imu_deg = float(msg.data) % 360.0

    def cb_posts(self, msg: Float32):
        self.postes = int(float(msg.data))

    def cb_lidar(self, msg: Float32):
        # Solo guardo la última distancia; el control lo hace control_loop()
        self.last_dist = float(msg.data)

        # ---- PATCH: alimentar buffer para reanudar por estabilidad ----
        d = self.last_dist
        if d is not None and self.resume_min_m <= d <= self.resume_max_m:
            self.dist_buf.append(d)
        else:
            self.dist_buf.clear()

    # ---------- Lazo principal NO bloqueante ----------
    def control_loop(self):
        now = self.get_clock().now()
        tsec = (now - self.t_enter).nanoseconds / 1e9

        if self.mode == 'FOLLOW':
            # Cambiar a PREPARE cuando alcance 4 postes
            if self.postes >= 5:
                # poner 0° y anunciar el siguiente rumbo objetivo al LiDAR
                self._publish_angle(0.0)

                # Avanza al siguiente surco si aún quedan filas por recorrer
                if self.row_count < self.max_rows:
                    self.row_parity ^= 1
                    self.row_count += 1
                    self.target_deg = 180.0 if self.row_parity else 0.0
                    self.pub_imu_target.publish(Float32(data=self.target_deg))
                    self.get_logger().warn(f'🎯 Maniobra hacia fila {self.row_count}: objetivo IMU {self.target_deg:.1f}°')
                else:
                    self.get_logger().warn("🟢 Última fila alcanzada. Manteniendo fuzzy activo.")
                    return


                self.mode = 'PREPARE'
                self.t_enter = now
                return
            # Control de pared normal
            if self.last_dist is None:
                return
            e = self.setpoint - self.last_dist
            self.sim.input['error'] = e
            self.sim.compute()
            steer = float(self.sim.output['delta'])
            steer = float(np.clip(steer, -self.AMAX, self.AMAX))
            dtheta = steer - self.steer_prev
            if dtheta >  self.DTHMAX: steer = self.steer_prev + self.DTHMAX
            if dtheta < -self.DTHMAX: steer = self.steer_prev - self.DTHMAX
            self.steer_prev = steer
            self._publish_angle(steer)
            # CSV de error (igual que antes)
            if self.csv_ErrorDist and not self.csv_ErrorDist.closed:
                t = self.get_clock().now().nanoseconds / 1e9
                self.writer_ErrorDist.writerow([f'{t:.9f}', f'{float(e):.6f}'])
            return

        if self.mode == 'PREPARE':
            # Mantén 0° durante ~5 s sin bloquear
            self._publish_angle(0.0)
            if tsec >= 5.0:
                self.mode = 'TURNING'
                self.t_enter = now
            return

        if self.mode == 'TURNING':
            # Publica -45° continuamente hasta entrar a la ventana IMU
            # Dirección del giro según fila
            if self.row_parity == 90:
                self._publish_angle(0.0)  # segunda fila: giro a la izquierda
            else:
                self._publish_angle(-35.0)   # tercera fila: giro a la derecha
                
            if self._imu_in_window(self.imu_deg, self.imu_win_lo, self.imu_win_hi):
                # Parar
                self._publish_angle(0.0)
                self._publish_angle(90.0)  # ESP32 apaga propulsión
                self.mode = 'STOPPED'
                self.t_enter = now
            return

        if self.mode == 'STOPPED':
            # Mantener STOP (por seguridad)
            self._publish_angle(90.0)
            # ---- PATCH: reanudar cuando el LiDAR “ve” pared estable ----
            # salir del STOP por tiempo máximo
            if tsec >= self.stop_hold_s:
                self._publish_angle(0.0)   # saca al ESP32 del STOP
                self.steer_prev = 0.0                
                # Restaurar parámetros IMU originales al volver al fuzzy
                if self.row_parity == 0:
                    self.pub_imu_target.publish(Float32(data=0.0))
                    self.get_logger().info("🔁 Restaurando referencia IMU original (0°).")
                self.mode = 'FOLLOW'
                self.t_enter = now
                return

            if self._dist_stable():
                span = max(self.dist_buf) - min(self.dist_buf)
                mean_d = sum(self.dist_buf) / len(self.dist_buf)
                self.get_logger().warn(
                    f"Reanudando FOLLOW: dist≈{mean_d:.2f} m, span={span:.3f} m"
                )
                self.dist_buf.clear()
                self.steer_prev = 0.0
                self._publish_angle(0.0)   # saca al ESP32 del STOP
                self.mode = 'FOLLOW'
                self.t_enter = now
            return

    # ---------- Utilidades ----------
    def _imu_in_window(self, deg, lo, hi):
        d = deg % 360.0
        return lo <= d <= hi

    # ---- PATCH: estabilidad de distancia ----
    def _dist_stable(self) -> bool:
        if len(self.dist_buf) < self.resume_need:
            return False
        span = max(self.dist_buf) - min(self.dist_buf)
        return span <= self.resume_span_thresh

    def _publish_angle(self, val_deg: float):
        self.pub_out.publish(Float32(data=float(val_deg)))
        self.get_logger().info(f"Steer: {val_deg:.2f}")  # si molesta, comenta esta línea

    def destroy_node(self):
        try:
            if self.csv_ErrorDist and not self.csv_ErrorDist.closed:
                self.csv_ErrorDist.flush(); self.csv_ErrorDist.close()
        except Exception:
            pass
        super().destroy_node()

def main():
    rclpy.init()
    node = WallFollowerSteer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
