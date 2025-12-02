# monitor_silicic_mejorado.py
import requests
import time
from datetime import datetime
import json
import sys
import os

class MonitorSilicicMejorado:
    def __init__(self):
        # TUS URLs REALES de Render
        self.endpoints = {
            'api': 'https://silicic-api.onrender.com',
            'dashboard': 'https://silicic-dashboard.onrender.com'
        }
        self.estadisticas = []
        self.historial = []
        self.timeout = 30  # Timeout para requests
    
    def mostrar_logo(self):
        logo = """
        ╔═══════════════════════════════════════╗
        ║     🌍 SILICIC EARTH MONITOR 1.0     ║
        ║   Sistema Nervioso Planetario Vivo   ║
        ║      Estado: MONITORANDO RENDER      ║
        ╚═══════════════════════════════════════╝
        """
        print(logo)
        print(f"🕐 Hora del sistema: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API: {self.endpoints['api']}")
        print(f"📊 Dashboard: {self.endpoints['dashboard']}")
        print("="*55)
    
    def verificar_servicio(self, nombre, url):
        """Verifica un servicio individual"""
        try:
            start_time = time.time()
            
            if nombre == 'api':
                # Para API, probamos endpoint básico y de estadísticas
                respuesta = requests.get(url, timeout=self.timeout)
                elapsed = time.time() - start_time
                
                if respuesta.status_code == 200:
                    data = respuesta.json()
                    return {
                        'online': True,
                        'status_code': respuesta.status_code,
                        'response_time': elapsed,
                        'message': data.get('message', 'API operativa'),
                        'endpoint': '/'
                    }
                else:
                    return {
                        'online': False,
                        'status_code': respuesta.status_code,
                        'error': f"HTTP {respuesta.status_code}",
                        'response_time': elapsed
                    }
                    
            else:  # dashboard
                respuesta = requests.get(url, timeout=self.timeout)
                elapsed = time.time() - start_time
                
                if respuesta.status_code == 200:
                    # Verificamos si es Streamlit
                    es_streamlit = 'streamlit' in respuesta.text.lower()
                    return {
                        'online': True,
                        'status_code': respuesta.status_code,
                        'response_time': elapsed,
                        'es_streamlit': es_streamlit,
                        'tamano': len(respuesta.text)
                    }
                else:
                    return {
                        'online': False,
                        'status_code': respuesta.status_code,
                        'error': f"HTTP {respuesta.status_code}",
                        'response_time': elapsed
                    }
                
        except requests.exceptions.Timeout:
            return {
                'online': False,
                'error': 'TIMEOUT',
                'response_time': self.timeout
            }
        except requests.exceptions.ConnectionError:
            return {
                'online': False,
                'error': 'CONNECTION_ERROR'
            }
        except Exception as e:
            return {
                'online': False,
                'error': str(e)
            }
    
    def check_health_detallado(self):
        """Verifica salud del sistema completo"""
        print("\n🔍 VERIFICANDO ESTADO DEL SISTEMA SILICIC...")
        print("="*55)
        
        reporte = {
            'timestamp': datetime.now().isoformat(),
            'status': {},
            'estadisticas': None,
            'alertas': [],
            'recomendaciones': []
        }
        
        for name, url in self.endpoints.items():
            print(f"\n📡 Probando {name.upper()}:")
            print(f"   URL: {url}")
            
            resultado = self.verificar_servicio(name, url)
            reporte['status'][name] = resultado
            
            if resultado['online']:
                print(f"   ✅ ONLINE - {resultado.get('status_code', 'N/A')}")
                
                if 'response_time' in resultado:
                    print(f"   ⏱️  Tiempo: {resultado['response_time']:.2f}s")
                
                if name == 'api':
                    # Intentar obtener estadísticas
                    try:
                        stats_url = f"{url}/estadisticas"
                        stats_resp = requests.get(stats_url, timeout=15)
                        if stats_resp.status_code == 200:
                            stats = stats_resp.json()
                            reporte['estadisticas'] = stats
                            print(f"   📊 Evaluaciones: {stats.get('total_evaluaciones', 'N/A')}")
                    except:
                        pass
                        
                elif name == 'dashboard':
                    if resultado.get('es_streamlit'):
                        print(f"   🎯 Confirmado: Streamlit App")
                    else:
                        print(f"   ℹ️  Web funcionando (puede no ser Streamlit)")
            else:
                print(f"   ❌ OFFLINE")
                if 'error' in resultado:
                    print(f"   🐛 Error: {resultado['error']}")
                
                # Recomendaciones específicas
                if resultado.get('error') == 'TIMEOUT':
                    reporte['recomendaciones'].append(
                        f"{name}: Posiblemente durmiendo (Render Free Tier). " +
                        "Espera 50s y reintenta."
                    )
                elif resultado.get('status_code') == 404:
                    reporte['recomendaciones'].append(
                        f"{name}: URL incorrecta o servicio no desplegado."
                    )
        
        return reporte
    
    def generar_resumen(self, reporte):
        """Genera resumen ejecutivo"""
        print("\n" + "="*55)
        print("📊 RESUMEN DEL SISTEMA SILICIC EARTH")
        print("="*55)
        
        # Contar servicios online
        online_count = sum(1 for s in reporte['status'].values() if s.get('online', False))
        total_count = len(reporte['status'])
        
        # Estado general
        if online_count == total_count:
            estado = "✅ ÓPTIMO"
            emoji = "🎉"
            color = "\033[92m"  # Verde
        elif online_count >= 1:
            estado = "⚠️  PARCIAL"
            emoji = "🔄"
            color = "\033[93m"  # Amarillo
        else:
            estado = "❌ CRÍTICO"
            emoji = "🚨"
            color = "\033[91m"  # Rojo
        
        print(f"\n{emoji} ESTADO GENERAL: {color}{estado}\033[0m")
        print(f"   Servicios online: {online_count}/{total_count}")
        print(f"   Hora: {reporte['timestamp'][11:19]}")
        
        # Detalles por servicio
        print("\n🔧 DETALLE POR SERVICIO:")
        for name, status in reporte['status'].items():
            if status.get('online'):
                tiempo = status.get('response_time', 0)
                print(f"   ✅ {name.upper():10} - {tiempo:.2f}s - HTTP {status.get('status_code', 'N/A')}")
            else:
                error = status.get('error', 'Desconocido')
                print(f"   ❌ {name.upper():10} - {error}")
        
        # Estadísticas si disponibles
        if reporte.get('estadisticas'):
            print("\n📈 ESTADÍSTICAS SILICIC:")
            stats = reporte['estadisticas']
            print(f"   📊 Evaluaciones: {stats.get('total_evaluaciones', 0)}")
            print(f"   ⭐ Puntuación: {stats.get('puntuacion_promedio', 0):.2f}")
        
        # Alertas y recomendaciones
        if reporte.get('recomendaciones'):
            print("\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(reporte['recomendaciones'], 1):
                print(f"   {i}. {rec}")
        
        # Consejo específico para Render Free Tier
        if online_count < total_count:
            print("\n💤 NOTA RENDER FREE TIER:")
            print("   Los servicios duermen tras 15min inactivos.")
            print("   La primera petición tarda ~50s en despertarlos.")
            print("   Esto es NORMAL y esperado.")
        
        return {
            'estado_general': estado.replace("✅", "").replace("⚠️", "").replace("❌", "").strip(),
            'online_count': online_count,
            'total_count': total_count,
            'timestamp': reporte['timestamp']
        }
    
    def ejecutar_monitoreo_continuo(self, interval_minutos=5, max_ciclos=None):
        """Monitoreo continuo"""
        print("\n🔄 INICIANDO MONITOREO CONTINUO")
        print(f"   Intervalo: {interval_minutos} minutos")
        print("   Presiona Ctrl+C para detener")
        print("-"*55)
        
        try:
            ciclo = 0
            while True:
                if max_ciclos and ciclo >= max_ciclos:
                    break
                    
                ciclo += 1
                print(f"\n🕒 CICLO {ciclo} - {datetime.now().strftime('%H:%M:%S')}")
                
                reporte = self.check_health_detallado()
                resumen = self.generar_resumen(reporte)
                
                # Guardar en historial
                self.historial.append({
                    'ciclo': ciclo,
                    'timestamp': reporte['timestamp'],
                    'resumen': resumen,
                    'detalles': reporte['status']
                })
                
                # Esperar para siguiente ciclo
                if ciclo < (max_ciclos or 99999):
                    print(f"\n⏳ Esperando {interval_minutos} minutos...")
                    for i in range(interval_minutos * 60, 0, -1):
                        if i % 30 == 0:
                            sys.stdout.write(f"\r   Revisión en {i//60}:{i%60:02d} minutos...")
                            sys.stdout.flush()
                        time.sleep(1)
                    print("\r" + " " * 50 + "\r", end="")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoreo detenido por usuario")
            self.mostrar_resumen_final()
    
    def mostrar_resumen_final(self):
        """Muestra resumen final"""
        if not self.historial:
            print("No hay datos de monitoreo")
            return
        
        print("\n" + "="*55)
        print("📋 RESUMEN FINAL DEL MONITOREO")
        print("="*55)
        
        total_ciclos = len(self.historial)
        print(f"\n📊 Total de ciclos: {total_ciclos}")
        
        if total_ciclos > 0:
            # Calcular disponibilidad
            servicios = list(self.endpoints.keys())
            disponibilidad = {}
            
            for servicio in servicios:
                online_count = sum(1 for h in self.historial 
                                if h['detalles'].get(servicio, {}).get('online', False))
                disponibilidad[servicio] = (online_count / total_ciclos) * 100
            
            print("\n📈 DISPONIBILIDAD POR SERVICIO:")
            for servicio, porcentaje in disponibilidad.items():
                if porcentaje > 90:
                    emoji = "✅"
                elif porcentaje > 70:
                    emoji = "⚠️"
                else:
                    emoji = "❌"
                print(f"   {emoji} {servicio.upper():10}: {porcentaje:.1f}%")
            
            # Último estado
            ultimo = self.historial[-1]
            print(f"\n⏰ Última verificación: {ultimo['timestamp'][11:19]}")
            print(f"🎯 Estado final: {ultimo['resumen']['estado_general']}")
            
            # Guardar reporte
            nombre_archivo = f"reporte_silicic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump({
                        'historial': self.historial,
                        'resumen': {
                            'total_ciclos': total_ciclos,
                            'disponibilidad': disponibilidad,
                            'fecha_generacion': datetime.now().isoformat()
                        }
                    }, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Reporte guardado: {nombre_archivo}")
            except:
                print("\n📝 Nota: No se pudo guardar reporte (ejecución en entorno restringido)")

def main():
    """Función principal"""
    monitor = MonitorSilicicMejorado()
    monitor.mostrar_logo()
    
    print("\nSelecciona modo de operación:")
    print("1. ✅ Verificación única (rápida)")
    print("2. 🔄 Monitoreo continuo (5 min intervalos)")
    print("3. 🧪 Test rápido (3 ciclos)")
    print("4. 📊 Ver historial si existe")
    
    try:
        opcion = input("\nOpción (1-4): ").strip()
        
        if opcion == "1":
            print("\n" + "="*55)
            reporte = monitor.check_health_detallado()
            monitor.generar_resumen(reporte)
            
            # Verificación de conectividad extra
            print("\n🌐 VERIFICACIÓN EXTRA DE CONECTIVIDAD:")
            print("   Tu API:", monitor.endpoints['api'])
            print("   Dashboard:", monitor.endpoints['dashboard'])
            
        elif opcion == "2":
            monitor.ejecutar_monitoreo_continuo(interval_minutos=5)
            
        elif opcion == "3":
            monitor.ejecutar_monitoreo_continuo(interval_minutos=1, max_ciclos=3)
            
        elif opcion == "4":
            monitor.mostrar_resumen_final()
            
        else:
            print("\n⚠️  Opción no válida. Usando verificación única.")
            reporte = monitor.check_health_detallado()
            monitor.generar_resumen(reporte)
            
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        
        # Verificación de emergencia
        print("\n🆘 VERIFICACIÓN DE EMERGENCIA:")
        try:
            r = requests.get("https://silicic-api.onrender.com", timeout=10)
            print(f"   API: {'✅' if r.status_code == 200 else '❌'} ({r.status_code})")
        except:
            print("   API: ❌ No responde")
        
        try:
            r = requests.get("https://silicic-dashboard.onrender.com", timeout=10)
            print(f"   Dashboard: {'✅' if r.status_code == 200 else '❌'} ({r.status_code})")
        except:
            print("   Dashboard: ❌ No responde")

if __name__ == "__main__":
    main()