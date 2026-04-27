<template>
  <div class="barcode-scanner">
    <div class="scanner-controls">
      <button @click="startScanning" :disabled="isScanning" class="btn-scan">
        {{ isScanning ? 'Escaneando...' : 'Escanear Código' }}
      </button>
      <button v-if="isScanning" @click="stopScanning" class="btn-stop">
        Detener
      </button>
    </div>
    <div id="barcode-reader" class="reader-container" v-show="isScanning"></div>
    <div v-if="lastScan" class="scan-result">
      <strong>Último escaneo:</strong> {{ lastScan }}
      <button @click="$emit('scanned', lastScan)" class="btn-use">Usar</button>
    </div>
  </div>
</template>

<script>
import { Html5Qrcode } from 'html5-qrcode'

export default {
  name: 'BarcodeScanner',
  props: {
    autoSubmit: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['scanned'],
  data() {
    return {
      isScanning: false,
      lastScan: null,
      html5QrcodeScanner: null,
    }
  },
  methods: {
    async startScanning() {
      try {
        this.isScanning = true
        this.html5QrcodeScanner = new Html5Qrcode('barcode-reader')

        const devices = await Html5Qrcode.getCameras()
        if (!devices || devices.length === 0) {
          this.isScanning = false
          alert('No se encontraron cámaras disponibles')
          return
        }

        const cameraId = devices.find(d => d.label.toLowerCase().includes('back'))?.id || devices[0].id

        await this.html5QrcodeScanner.start(
          cameraId,
          {
            fps: 10,
            qrbox: { width: 250, height: 150 },
            aspectRatio: 1.5,
          },
          (decodedText) => {
            this.onScanSuccess(decodedText)
          },
          () => {}
        )
      } catch (err) {
        console.error('Error al iniciar escáner:', err)
        this.isScanning = false
        alert('No se pudo acceder a la cámara. Verifica los permisos.')
      }
    },
    async stopScanning() {
      if (this.html5QrcodeScanner && this.isScanning) {
        try {
          await this.html5QrcodeScanner.stop()
          this.html5QrcodeScanner.clear()
        } catch (err) {
          console.error('Error al detener escáner:', err)
        }
        this.isScanning = false
      }
    },
    onScanSuccess(decodedText) {
      this.lastScan = decodedText
      if (this.autoSubmit) {
        this.$emit('scanned', decodedText)
        this.stopScanning()
      }
    },
  },
  beforeUnmount() {
    this.stopScanning()
  },
}
</script>

<style scoped>
.barcode-scanner {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.scanner-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.btn-scan, .btn-stop, .btn-use {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-scan {
  background: #4CAF50;
  color: white;
}

.btn-scan:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-stop {
  background: #f44336;
  color: white;
}

.btn-use {
  background: #2196F3;
  color: white;
  margin-left: 0.5rem;
}

.reader-container {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
}

.scan-result {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #e8f5e9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
