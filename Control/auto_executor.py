#!/usr/bin/env python3
"""
⏰ EJECUTOR AUTOMÁTICO CON SCHEDULER
- Ejecución programada del bot
- Automatización completa sin interfaz
- Monitoreo 24/7
- Reintentos automáticos
- Reportes periódicos
"""

import sys
import os
import json
import logging
import threading
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
import schedule
from pathlib import Path

logger = logging.getLogger('AutoExecutor')

# Configurar logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler('CryptoBotPro_Data/logs/auto_executor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class ScheduledExecutor:
    """Ejecutor de tareas programadas"""
    
    def __init__(self, config_path: str = 'config_v20_optimized.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
        self.bot_process = None
        self.last_execution = None
        self.execution_count = 0
        self.error_count = 0
    
    def _load_config(self) -> Dict:
        """Carga configuración"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando config: {e}")
            return {}
    
    def start_bot(self) -> bool:
        """Inicia el bot principal"""
        try:
            logger.info("🚀 Iniciando bot principal...")
            
            # Comando para ejecutar bot
            cmd = [
                sys.executable,
                'Crypto-Pro-Python v34.0.1.2.py'
            ]
            
            # Crear proceso
            self.bot_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.last_execution = datetime.now()
            self.execution_count += 1
            
            logger.info(f"✅ Bot iniciado (PID: {self.bot_process.pid})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error iniciando bot: {e}")
            self.error_count += 1
            return False
    
    def stop_bot(self) -> bool:
        """Detiene el bot"""
        try:
            if self.bot_process and self.bot_process.poll() is None:
                logger.info("🛑 Deteniendo bot...")
                self.bot_process.terminate()
                
                # Esperar a que termine
                try:
                    self.bot_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Bot no respondió, terminando forcibly...")
                    self.bot_process.kill()
                
                logger.info("✅ Bot detenido")
                return True
        except Exception as e:
            logger.error(f"Error deteniendo bot: {e}")
        
        return False
    
    def restart_bot(self) -> bool:
        """Reinicia el bot"""
        logger.info("🔄 Reiniciando bot...")
        self.stop_bot()
        time.sleep(2)
        return self.start_bot()
    
    def is_bot_running(self) -> bool:
        """Verifica si el bot está corriendo"""
        if not self.bot_process:
            return False
        return self.bot_process.poll() is None
    
    def check_bot_health(self) -> Dict[str, Any]:
        """Verifica salud del bot"""
        health = {
            'running': self.is_bot_running(),
            'pid': self.bot_process.pid if self.bot_process else None,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'uptime_minutes': 0,
            'status': 'UNKNOWN'
        }
        
        if health['running']:
            uptime = (datetime.now() - self.last_execution).total_seconds() / 60
            health['uptime_minutes'] = uptime
            health['status'] = '✅ RUNNING'
            
            if self.error_count > 5:
                health['status'] = '⚠️ RUNNING (CON ERRORES)'
        else:
            health['status'] = '❌ STOPPED'
        
        return health
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Recolecta métricas del bot"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'bot_health': self.check_bot_health(),
            'system_info': {}
        }
        
        # Información del sistema
        try:
            import psutil
            metrics['system_info'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            pass
        
        return metrics
    
    def generate_report(self) -> str:
        """Genera reporte de ejecución"""
        
        metrics = self.collect_metrics()
        health = metrics['bot_health']
        
        report = f"""
{'='*60}
REPORTE DE EJECUCIÓN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

SALUD DEL BOT:
- Estado: {health['status']}
- PID: {health['pid']}
- Uptime: {health['uptime_minutes']:.1f} minutos
- Ejecuciones totales: {health['execution_count']}
- Errores totales: {health['error_count']}
- Última ejecución: {health['last_execution']}

INFORMACIÓN DEL SISTEMA:
- CPU: {metrics['system_info'].get('cpu_percent', 'N/A')}%
- Memoria: {metrics['system_info'].get('memory_percent', 'N/A')}%
- Disco: {metrics['system_info'].get('disk_percent', 'N/A')}%

{'='*60}
"""
        
        return report
    
    def run_scheduler(self):
        """Ejecuta scheduler de tareas"""
        
        logger.info("📅 Iniciando scheduler...")
        
        # Programar tareas
        
        # 1. Iniciar bot a las 00:00
        schedule.every().day.at("00:00").do(self.start_bot)
        logger.info("📌 Bot se iniciará diariamente a las 00:00")
        
        # 2. Reinicio cada 24 horas (para limpiar memoria)
        schedule.every(24).hours.do(self.restart_bot)
        logger.info("📌 Bot se reiniciará cada 24 horas")
        
        # 3. Health check cada 30 minutos
        schedule.every(30).minutes.do(self._health_check_job)
        logger.info("📌 Health check cada 30 minutos")
        
        # 4. Reporte cada 2 horas
        schedule.every(2).hours.do(self._report_job)
        logger.info("📌 Reporte cada 2 horas")
        
        # 5. Limpeza de logs cada día
        schedule.every().day.at("02:00").do(self._cleanup_logs_job)
        logger.info("📌 Limpeza de logs a las 02:00")
        
        # Loop del scheduler
        self.running = True
        
        try:
            logger.info("✅ Scheduler activo, esperando tareas...")
            
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler interrumpido por usuario")
        finally:
            self.running = False
            self.stop_bot()
            logger.info("🛑 Scheduler detenido")
    
    def _health_check_job(self):
        """Trabajo de health check"""
        try:
            health = self.check_bot_health()
            
            if not health['running']:
                logger.warning("⚠️ Bot no está corriendo, reiniciando...")
                self.restart_bot()
            else:
                logger.info(f"✅ Bot running: PID {health['pid']}, Uptime: {health['uptime_minutes']:.1f}m")
        except Exception as e:
            logger.error(f"Error en health check: {e}")
    
    def _report_job(self):
        """Trabajo de reporte periódico"""
        try:
            report = self.generate_report()
            logger.info(report)
            
            # Guardar reporte
            report_file = f"CryptoBotPro_Data/logs/execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs('CryptoBotPro_Data/logs', exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
    
    def _cleanup_logs_job(self):
        """Trabajo de limpeza de logs"""
        try:
            logs_dir = 'CryptoBotPro_Data/logs'
            if not os.path.exists(logs_dir):
                return
            
            # Eliminar logs más antiguos de 7 días
            cutoff_time = time.time() - (7 * 24 * 60 * 60)
            
            deleted = 0
            for f in os.listdir(logs_dir):
                file_path = os.path.join(logs_dir, f)
                if os.path.isfile(file_path):
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        deleted += 1
            
            if deleted > 0:
                logger.info(f"🧹 Limpeza: {deleted} archivos de log antiguos eliminados")
        except Exception as e:
            logger.error(f"Error limpiando logs: {e}")


class BotMonitor:
    """Monitor avanzado del bot"""
    
    def __init__(self, executor: ScheduledExecutor):
        self.executor = executor
        self.alerts = []
    
    def monitor_loop(self):
        """Loop de monitoreo continuo"""
        
        logger.info("🔍 Iniciando monitor avanzado...")
        
        try:
            while True:
                health = self.executor.check_bot_health()
                
                # Enviar alertas si es necesario
                if not health['running'] and self.executor.running:
                    self._send_alert("❌ BOT STOPPED", "El bot se ha detenido inesperadamente")
                    self.executor.restart_bot()
                
                if health['error_count'] > 10:
                    self._send_alert("🚨 MULTIPLE ERRORS", 
                                   f"Se han detectado {health['error_count']} errores")
                
                if health.get('uptime_minutes', 0) > 1440:  # Más de 24 horas
                    logger.info("⏱️ Uptime crítico, ejecutando restart...")
                    self.executor.restart_bot()
                
                time.sleep(60)  # Monitorear cada minuto
        
        except KeyboardInterrupt:
            logger.info("Monitor interrumpido")
    
    def _send_alert(self, title: str, message: str):
        """Envía alerta (a Telegram u otro servicio)"""
        alert = f"[{datetime.now().strftime('%H:%M:%S')}] {title}: {message}"
        self.alerts.append(alert)
        logger.warning(alert)


def main():
    """Función principal"""
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║  🤖 CRYPTO BOT PRO - AUTO EXECUTOR                    ║
    ║  Sistema de Ejecución Automática 24/7                 ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Crear ejecutor
    executor = ScheduledExecutor()
    
    # Crear monitor
    monitor = BotMonitor(executor)
    
    # Iniciar threads
    scheduler_thread = threading.Thread(target=executor.run_scheduler, daemon=False)
    monitor_thread = threading.Thread(target=monitor.monitor_loop, daemon=True)
    
    try:
        logger.info("🚀 Iniciando sistema de ejecución automática...")
        
        scheduler_thread.start()
        monitor_thread.start()
        
        # Mantener main thread activo
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n⏹️ Deteniendo sistema...")
        executor.running = False
        executor.stop_bot()
        time.sleep(1)
        logger.info("✅ Sistema detenido")


if __name__ == '__main__':
    try:
        import schedule
    except ImportError:
        print("Instalando schedule...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
        import schedule
    
    main()
