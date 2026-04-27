<template>
  <div class="print-modal-overlay no-print" v-if="show" @click.self="$emit('close')">
    <div class="print-modal-container">
      <div class="print-modal-header">
        <h3>Vista Previa de Orden de Servicio</h3>
        <div class="print-actions">
          <button @click="printOrder" class="btn btn-primary">
            <i class="fas fa-print"></i> Imprimir
          </button>
          <button @click="$emit('close')" class="btn btn-secondary">Cerrar</button>
        </div>
      </div>
      <div class="print-preview-box">
        <p>Se imprimirá en formato Carta/A4 con el diseño oficial.</p>
      </div>
    </div>
  </div>

  <!-- Area de Impresion -->
  <Teleport to="body">
    <div v-if="show" id="print-area" class="print-content repair-order-layout">
      <!-- Header Section -->
      <div class="print-header">
        <div class="header-left">
          <img v-if="company.logo_url" :src="logoFullUrl" alt="Logo" class="print-logo" />
          <img v-else src="@/assets/logo.png" alt="Logo" class="print-logo" />
        </div>
        <div class="header-right">
          <div class="order-id-top">{{ order.order_number }}</div>
          <div class="company-details">
            <p>{{ company.address }}</p>
            <p>Tel: {{ company.phone }}</p>
            <p>Email: {{ company.email }}</p>
          </div>
        </div>
      </div>

      <div class="title-section">
        <h1>ORDEN DE SERVICIO TÉCNICO</h1>
        <p class="subtitle">Orden #{{ order.id }} - Fecha: {{ formatDate(order.issue_date) }}</p>
      </div>

      <!-- Section: INFORMACION DEL CLIENTE -->
      <div class="print-section">
        <h2 class="section-title">INFORMACIÓN DEL CLIENTE</h2>
        <div class="info-grid-3">
          <div class="info-item"><strong>Cliente:</strong> {{ partner?.name || 'N/A' }}</div>
          <div class="info-item"><strong>Documento:</strong> {{ partner?.nit || partner?.document_number || 'N/A' }}</div>
          <div class="info-item"><strong>Teléfono:</strong> {{ partner?.phone || 'N/A' }}</div>
          <div class="info-item"><strong>Email:</strong> {{ partner?.email || 'N/A' }}</div>
          <div class="info-item full-col"><strong>Dirección:</strong> {{ partner?.address || 'N/A' }}</div>
        </div>
      </div>

      <!-- Section: DETALLES DEL EQUIPO -->
      <div class="print-section">
        <h2 class="section-title">DETALLES DEL EQUIPO</h2>
        <div class="equipment-grid">
          <div class="info-item"><strong>Tipo:</strong> {{ primaryItem?.description || 'N/A' }}</div>
          <div class="info-item"><strong>Número de Serie:</strong> {{ primaryItem?.serial_number || 'N/A' }}</div>
          <div class="info-item"><strong>Marca:</strong> {{ primaryItem?.brand || 'N/A' }}</div>
          <div class="info-item"><strong>Estado Ingreso:</strong> {{ statusLabel }}</div>
          <div class="info-item"><strong>Modelo:</strong> {{ primaryItem?.model || 'N/A' }}</div>
          <div class="info-item"><strong>Técnico:</strong> {{ technicianName }}</div>
        </div>
      </div>

      <!-- Section: DESCRIPCION DE LA FALLA -->
      <div class="print-section">
        <h2 class="section-title">DESCRIPCIÓN DE LA FALLA</h2>
        <div class="text-box">
          {{ order.problem_description || 'No especificada' }}
        </div>
      </div>

      <!-- Section: ACCESORIOS -->
      <div class="print-section">
        <h2 class="section-title">ACCESORIOS RECIBIDOS</h2>
        <div class="text-box">
          {{ order.service_notes || 'Ninguno' }}
        </div>
      </div>

      <!-- Section: ESTADO FISICO -->
      <div class="print-section" v-if="order.diagnosis">
        <h2 class="section-title">ESTADO FÍSICO DEL EQUIPO</h2>
        <div class="text-box">
          {{ order.diagnosis }}
        </div>
      </div>

      <!-- Signature Section -->
      <div class="signature-section">
        <div class="signature-box">
          <div class="signature-line"></div>
          <p>Firma Cliente</p>
        </div>
        <div class="signature-box">
          <div class="signature-line"></div>
          <p>Recibido por</p>
        </div>
      </div>

      <!-- Legal Footer -->
      <div class="legal-footer">
        <ol>
          <li><strong>FINALIZACIÓN DEL SERVICIO:</strong> El cliente tiene un (1) mes calendario para retirar el equipo. Pasado este tiempo, se cobrará un costo de bodegaje de $ 5000 COP diarios. Transcurridos dos (2) meses desde la notificación sin que el equipo sea retirado, se declarará legalmente en estado de abandono, y el taller podrá disponer del bien para recuperar costos de reparación y almacenamiento.</li>
          <li><strong>GARANTÍA:</strong> Se otorga una garantía de noventa (90) días sobre la reparación y repuestos instalados. Esta se anulará por: rotura de sellos de seguridad, contacto con líquidos, sulfatación, golpes, picos de voltaje o intervención técnica de terceros.</li>
          <li><strong>RESPONSABILIDAD DE DATOS:</strong> El taller no se hace responsable por la integridad o pérdida de información, software o licencias. Es obligación del cliente entregar el equipo con una copia de seguridad (backup) previa.</li>
          <li><strong>HABEAS DATA:</strong> Al firmar, el cliente autoriza el tratamiento de sus datos personales para fines comerciales y de servicio, conforme a la Ley 1581 de 2012.</li>
        </ol>
      </div>
    </div>
  </Teleport>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'RepairPrintModal',
  props: {
    show: { type: Boolean, default: false },
    order: { type: Object, required: true },
    partner: { type: Object, default: () => ({}) },
    company: { type: Object, required: true },
    technicians: { type: Array, default: () => [] }
  },
  computed: {
    primaryItem() {
      return this.order.items?.[0] || {}
    },
    statusLabel() {
      const labels = {
        RECEIVED: 'Recibido',
        DIAGNOSIS: 'En Diagnóstico',
        APPROVED: 'Aprobado',
        IN_REPAIR: 'En Reparación',
        WAITING_PARTS: 'Esperando Repuestos',
        READY: 'Listo',
        DELIVERED: 'Entregado',
        CANCELLED: 'Cancelado'
      }
      return labels[this.order.status] || this.order.status
    },
    technicianName() {
      if (!this.order.technician_id || !this.technicians.length) return 'Sin asignar'
      const tech = this.technicians.find(t => t.id === this.order.technician_id)
      return tech ? `${tech.first_name} ${tech.last_name}` : 'Sin asignar'
    },
    logoFullUrl() {
      if (this.company.logo_url) {
        return `${api.defaults.baseURL}${this.company.logo_url}`
      }
      return null
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('es-CO', {
        year: 'numeric', month: '2-digit', day: '2-digit'
      })
    },
    printOrder() {
      const originalTitle = document.title
      const clientName = this.partner?.name || 'Cliente'
      const orderNum = this.order.order_number || this.order.id
      
      // Set title for PDF filename
      document.title = `${clientName}_${orderNum}`
      
      window.print()
      
      // Restore original title after a short delay
      setTimeout(() => {
        document.title = originalTitle
      }, 500)
    }
  }
}
</script>

<style scoped>
.print-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.print-modal-container {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
}

.print-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.print-actions { display: flex; gap: 1rem; }

.print-preview-box {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px dashed #dee2e6;
}

/* Print Area style for screen preview inside modal (optional, usually handled by @page) */
#print-area { display: none; }
</style>

<style>
@media print {
  #app { display: none !important; }
  #print-area {
    display: block !important;
    visibility: visible !important;
    position: absolute !important;
    left: 0 !important; top: 0 !important;
    width: 100% !important;
    padding: 0 !important; margin: 0 !important;
    background: white !important;
    color: #000 !important;
  }
  @page { margin: 1cm; }
}

.repair-order-layout {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
}

.print-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.print-logo {
  width: 200px;
  height: auto;
}

.header-right {
  text-align: right;
}

.order-id-top {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 5px;
}

.company-details p {
  margin: 2px 0;
  font-size: 12px;
  color: #333;
}

.title-section {
  text-align: center;
  margin-bottom: 15px;
}

.title-section h1 {
  font-size: 22px;
  margin: 0;
  text-decoration: underline;
  color: #003366;
}

.title-section .subtitle {
  font-size: 14px;
  margin: 10px 0 0 0;
  color: #555;
}

.print-section {
  margin-bottom: 12px;
}

.section-title {
  font-size: 14px;
  border-left: 4px solid #003366;
  padding-left: 10px;
  margin-bottom: 8px;
  font-weight: bold;
}

.info-grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  padding-left: 14px;
}

.full-col {
  grid-column: 1 / -1;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;
  padding-left: 14px;
}

.equipment-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 40px;
  padding-left: 14px;
}

.info-item {
  font-size: 13px;
}

.text-box {
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 8px;
  min-height: 35px;
  font-size: 13px;
  white-space: pre-wrap;
  margin-left: 14px;
}

.signature-section {
  display: flex;
  justify-content: space-around;
  margin-top: 35px;
  margin-bottom: 20px;
}

.signature-box {
  text-align: center;
  width: 250px;
}

.signature-line {
  border-top: 1px solid #000;
  margin-bottom: 10px;
}

.signature-box p {
  font-size: 13px;
  font-weight: bold;
  margin: 0;
}

.legal-footer {
  font-size: 8.5px;
  color: #444;
  text-align: justify;
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.legal-footer ol {
  padding-left: 20px;
}

.legal-footer li {
  margin-bottom: 4px;
  line-height: 1.3;
}
</style>
