<template>
  <div class="print-modal-overlay no-print" v-if="show" @click.self="$emit('close')">
    <div class="print-modal-container">
      <div class="print-modal-header">
        <h3>Vista Previa: Recibo de Caja</h3>
        <div class="print-actions">
          <button @click="printReceipt" class="btn btn-primary">
            <i class="fas fa-print"></i> Imprimir
          </button>
          <button @click="$emit('close')" class="btn btn-secondary">Cerrar</button>
        </div>
      </div>
      <div class="print-mode-selector">
        <label :class="{ active: mode === 'standard' }">
          <input type="radio" v-model="mode" value="standard" /> Formato Carta
        </label>
        <label :class="{ active: mode === 'pos' }">
          <input type="radio" v-model="mode" value="pos" /> Formato POS (Ticket)
        </label>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="show" id="print-area" :class="['print-content', mode]">
      <!-- Standard Layout (A4/Letter) -->
      <div v-if="mode === 'standard'" class="standard-layout">
        <div class="invoice-top-row">
          <div class="header-left">
            <img v-if="company.logo_url" :src="logoFullUrl" alt="Logo" class="main-logo" />
            <img v-else src="@/assets/logo.png" alt="Logo" class="main-logo" />
            <p v-if="company.slogan" class="slogan">{{ company.slogan }}</p>
          </div>
          <div class="header-right">
            <div class="owner-info">
              <h1 class="owner-name">{{ company.legal_representative || company.name }}</h1>
              <p class="nit-info">NIT: {{ company.nit }}-{{ company.dv || '0' }} / {{ regimenLabel }}</p>
            </div>
            
            <div class="invoice-box">
              <div class="box-title">RECIBO DE CAJA / ANTICIPO</div>
              <div class="box-content">
                N° <span class="invoice-num">{{ transaction.id.toString().padStart(6, '0') }}</span>
              </div>
            </div>
            <p class="date-label">Fecha: {{ formatDateShort(transaction.created_at) }}</p>
          </div>
        </div>

        <div class="blue-divider"></div>

        <div class="section-block">
          <div class="section-header">
            <span class="bar"></span>
            <h2 class="section-title">DATOS DEL CLIENTE</h2>
          </div>
          <div class="client-info-grid">
            <div class="info-item"><strong>Cliente:</strong> {{ partnerName }}</div>
            <div class="info-item"><strong>Identificación:</strong> {{ partnerNit || 'N/A' }}</div>
          </div>
        </div>

        <div class="section-block receipt-details">
          <div class="section-header">
            <span class="bar"></span>
            <h2 class="section-title">DETALLE DEL ABONO / INGRESO</h2>
          </div>
          <div class="receipt-body card p-4">
            <p class="concept-text"><strong>Concepto:</strong> {{ transaction.description || 'Abono general a cuenta' }}</p>
            <div class="amount-line">
              <span>Monto Recibido:</span>
              <span class="amount-value">{{ formatCOP(transaction.amount) }}</span>
            </div>
            <div class="amount-words mt-3" v-if="amountInWords">
              <strong>Son:</strong> {{ amountInWords }}
            </div>
          </div>
        </div>

        <div class="signature-row" style="margin-top: 100px;">
          <div class="signature-box">
            <div class="line"></div>
            <p>Firma del Cliente</p>
          </div>
          <div class="signature-box">
            <div class="line"></div>
            <p>Recibido por (Sello y Firma)</p>
            <p class="cashier-name" v-if="currentUser">Cajero: {{ currentUser.full_name || currentUser.username }}</p>
          </div>
        </div>

        <div class="footer-note mt-5 text-center">
          <p><em>Este documento es un comprobante de ingreso de dinero a favor del cliente en su monedero electrónico.</em></p>
        </div>
        <div v-if="company.invoice_footer_note" class="legal-disclaimer">
          <p style="white-space: pre-line;">{{ company.invoice_footer_note }}</p>
        </div>
      </div>

      <!-- POS Layout (Ticket) -->
      <div v-else class="pos-layout">
        <div class="pos-header">
          <img v-if="company.logo_url" :src="logoFullUrl" alt="Logo" class="pos-logo" />
          <h2 class="pos-company-name">{{ company.name }}</h2>
          <p>NIT: {{ company.nit }}</p>
        </div>
        <div class="pos-divider">********************************</div>
        <div class="pos-meta">
          <p>RECIBO N°: {{ transaction.id.toString().padStart(6, '0') }}</p>
          <p>FECHA: {{ formatDateShort(transaction.created_at) }}</p>
          <p>CLIENTE: {{ partnerName }}</p>
          <p v-if="currentUser">CAJERO: {{ currentUser.full_name || currentUser.username }}</p>
        </div>
        <div class="pos-divider">--------------------------------</div>
        <div class="pos-items">
          <p><strong>CONCEPTO:</strong></p>
          <p>{{ transaction.description || 'Abono a cuenta' }}</p>
        </div>
        <div class="pos-divider">--------------------------------</div>
        <div class="pos-totals">
          <div class="pos-row"><span>TOTAL RECIBIDO:</span> <span>{{ formatCOP(transaction.amount) }}</span></div>
        </div>
        <div v-if="company.address || company.phone || company.website || company.email" class="pos-contact">
          <p v-if="company.address">📍 {{ company.address }}</p>
          <p v-if="company.phone">📞 {{ company.phone }}</p>
          <p v-if="company.website">🌐 {{ company.website }}</p>
          <p v-if="company.email">✉ {{ company.email }}</p>
        </div>
        <div v-if="company.invoice_footer_note" style="font-size: 8px; text-align: justify; margin: 5px 0; white-space: pre-line;">
          {{ company.invoice_footer_note }}
        </div>
        <div class="pos-footer" style="margin-top: 20px;">
          ¡Gracias por su confianza!
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import api from '@/services/api'
import { formatCOP } from '@/utils/formatters'

export default {
  name: 'WalletReceiptModal',
  props: {
    show: { type: Boolean, default: false },
    transaction: { type: Object, required: true },
    partnerName: { type: String, default: 'Cliente' },
    partnerNit: { type: String, default: '' },
    company: { type: Object, required: true }
  },
  data() {
    return {
      mode: 'standard'
    }
  },
  computed: {
    currentUser() {
      return this.$store.getters['auth/getUser']
    },
    logoFullUrl() {
      if (this.company.logo_url) {
        return `${api.defaults.baseURL}${this.company.logo_url}`
      }
      return null
    },
    amountInWords() {
      return '';
    },
    regimenLabel() {
      const labels = {
        COMUN: 'RÉGIMEN COMÚN',
        SIMPLE: 'RÉGIMEN SIMPLE DE TRIBUTACIÓN',
        ESPECIAL: 'RÉGIMEN ESPECIAL',
        NO_RESPONSABLE: 'NO RESPONSABLE DE IVA'
      };
      return labels[this.company.regimen] || this.company.regimen || '';
    }
  },
  methods: {
    formatCOP,
    formatDateShort(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-CO', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
      });
    },
    printReceipt() {
      window.print();
    }
  },
  watch: {
    show: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.originalTitle = document.title;
          const num = this.transaction.id.toString().padStart(6, '0');
          document.title = `Recibo_Caja_${num}`;
        } else if (this.originalTitle) {
          document.title = this.originalTitle;
        }
      }
    }
  },
  beforeUnmount() {
    if (this.originalTitle) {
      document.title = this.originalTitle;
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
}
.print-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.print-actions { display: flex; gap: 1rem; }
.print-mode-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f1f3f5;
  padding: 1.5rem;
  border-radius: 12px;
}
.print-mode-selector label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  background: white;
}
.print-mode-selector label.active { border-color: #007bff; background: #e7f1ff; }
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
    background: white !important;
  }
  
  /* Remove browser headers/footers for POS */
  @page {
    margin: 0;
  }
  
  .pos-layout {
    width: 80mm !important;
    margin: 0 auto !important;
    padding: 5mm !important;
  }
}

.pos-layout {
  width: 80mm;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #000;
  margin: 0 auto;
  background: white;
}
.pos-header { text-align: center; margin-bottom: 10px; }
.pos-logo { width: 50mm; height: auto; margin-bottom: 5px; }
.pos-company-name { font-size: 16px; font-weight: bold; margin: 0; }
.pos-divider { text-align: center; margin: 5px 0; }
.pos-meta p { margin: 2px 0; }
.pos-items { margin: 10px 0; }
.pos-totals { font-weight: bold; font-size: 14px; }
.pos-footer { text-align: center; margin-top: 20px; font-style: italic; }

.invoice-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}
.header-left { flex: 1; }
.main-logo { width: 180px; height: auto; margin-bottom: 5px; }
.slogan { font-size: 10px; color: #003366; margin: 0; }
.slogan-bold { font-size: 10px; color: #003366; font-weight: bold; margin: 0; }

.header-right { text-align: right; }
.owner-name { font-size: 15px; color: #003366; margin: 0 0 3px 0; font-weight: bold; }
.nit-info { font-size: 10px; color: #003366; margin: 0 0 10px 0; }

.invoice-box {
  border: 1px solid #003366;
  border-radius: 6px;
  padding: 5px 10px;
  display: inline-block;
  min-width: 150px;
  text-align: center;
}
.box-title { font-size: 10px; font-weight: bold; color: #003366; border-bottom: 1px solid #003366; padding-bottom: 2px; margin-bottom: 2px; }
.box-content { font-size: 14px; color: #003366; font-weight: bold; }
.invoice-num { color: #cc0000; }
.date-label { font-size: 11px; margin: 5px 0 0 0; }

.blue-divider { height: 1.5px; background-color: #003366; margin: 10px 0; }

.section-block { margin-bottom: 15px; }
.section-header { display: flex; align-items: center; margin-bottom: 8px; }
.bar { width: 3px; height: 15px; background-color: #003366; margin-right: 8px; }
.section-title { font-size: 13px; margin: 0; color: #000; font-weight: bold; }

.client-info-grid {
  display: flex;
  flex-wrap: wrap;
  padding-left: 10px;
}
.info-item { width: 50%; font-size: 12px; margin-bottom: 3px; }

.signature-row {
  display: flex;
  justify-content: space-around;
  margin-top: 120px;
}
.signature-box { text-align: center; font-size: 12px; }
.signature-box .line { border-top: 1px solid #000; width: 200px; margin-bottom: 5px; }
.cashier-name { font-size: 10px; color: #666; margin-top: 4px; }

.receipt-body {
  border: 1px solid #003366;
  border-radius: 8px;
  padding: 15px;
}
.concept-text { font-size: 1rem; margin-bottom: 10px; }
.amount-line {
  display: flex;
  justify-content: space-between;
  font-size: 1.3rem;
  font-weight: 800;
  color: #003366;
  border-top: 1px solid #eee;
  padding-top: 8px;
}
.footer-note { color: #666; font-size: 0.8rem; }

.legal-disclaimer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #003366;
  font-size: 8px;
  color: #444;
  text-align: justify;
}

.pos-contact {
  font-size: 10px;
  text-align: center;
  margin: 5px 0;
}
.pos-contact p { margin: 2px 0; }
</style>
