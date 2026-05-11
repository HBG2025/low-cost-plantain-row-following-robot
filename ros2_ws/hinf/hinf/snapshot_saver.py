#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nodo ROS 2: guarda una foto cada N segundos desde un tópico de imagen.
Parámetros:
  - interval_sec (float, default 5.0)   -> intervalo entre fotos
  - out_dir      (str,   default ~/SNAPSHOTS) -> carpeta de salida
  - topic        (str,   default /image) -> tópico de suscripción
  - quality      (int,   default 90)     -> calidad JPEG 0..100
Salida:
  - Archivos .jpg con timestamp en out_dir
  - CSV con ros_time_s, header_stamp_s, filename
"""

import os
import csv
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class SnapshotSaver(Node):
    def __init__(self):
        super().__init__('snapshot_saver')

        # Parámetros
        self.declare_parameter('interval_sec', 1.0)
        self.declare_parameter('out_dir', os.path.expanduser('~/SNAPSHOTS'))
        self.declare_parameter('topic', '/image')
        self.declare_parameter('quality', 90)

        self.interval = float(self.get_parameter('interval_sec').value)
        self.out_dir = str(self.get_parameter('out_dir').value)
        self.topic = str(self.get_parameter('topic').value)
        self.quality = int(self.get_parameter('quality').value)

        os.makedirs(self.out_dir, exist_ok=True)

        # CSV de log
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_path = os.path.join(self.out_dir, f'snapshots_{ts}.csv')
        self.csv_file = open(self.csv_path, 'w', newline='', buffering=1)
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['ros_time_s', 'header_stamp_s', 'filename'])

        self.get_logger().info(
            f"Guardando en {self.out_dir} | CSV: {self.csv_path} | "
            f"cada {self.interval:.2f}s | topic: {self.topic} | quality: {self.quality}"
        )

        self.bridge = CvBridge()
        self.last_save_t = 0.0
        self.postes = 0.0

        # Suscripción
        self.sub = self.create_subscription(Image, self.topic, self.cb_image, 10)
        self.sub_posts= self.create_subscription(Float32, 'Postes', self.cb_posts, 10)

        # Permite cambiar parámetros en caliente (interval_sec, quality)
        self.create_timer(1.0, self._refresh_params)

    def cb_posts(self, msg: Float32):
        self.postes = int(float(msg.data))
        

    def _refresh_params(self):
        new_interval = float(self.get_parameter('interval_sec').value)
        new_quality = int(self.get_parameter('quality').value)
        if abs(new_interval - self.interval) > 1e-6:
            self.interval = new_interval
            self.get_logger().info(f'Nuevo interval_sec = {self.interval:.2f} s')
        if new_quality != self.quality:
            self.quality = max(0, min(100, new_quality))
            self.get_logger().info(f'Nuevo quality = {self.quality}')

    def cb_image(self, msg: Image):
        # Tiempo ROS seguro para alinear con otros nodos
        now_ros = self.get_clock().now().nanoseconds / 1e9
        if (now_ros - self.last_save_t) < self.interval:
            return
        self.last_save_t = now_ros

        # Convertir a OpenCV (BGR8) y guardar JPEG
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().warn(f'cv_bridge error: {e}')
            return

        hdr_stamp = 0.0
        try:
            hdr_stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        except Exception:
            pass

        fname = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}_{self.postes}.jpg"
        fpath = os.path.join(self.out_dir, fname)

        try:
            cv2.imwrite(fpath, cv_img, [cv2.IMWRITE_JPEG_QUALITY, int(self.quality)])
            self.csv_writer.writerow([f'{now_ros:.9f}', f'{hdr_stamp:.9f}', fname])
            self.get_logger().info(f'📸 Guardada {fname}')
        except Exception as e:
            self.get_logger().warn(f'No pude guardar {fpath}: {e}')

    def destroy_node(self):
        try:
            if self.csv_file and not self.csv_file.closed:
                self.csv_file.flush()
                self.csv_file.close()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = SnapshotSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
