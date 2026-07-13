<template>
  <div class="print-modal-overlay no-print" v-if="show" @click.self="$emit('close')">
    <div class="print-modal-container">
      <div class="print-modal-header">
        <h3>Vista Previa de Impresión</h3>
        <div class="print-actions">
          <button @click="printInvoice" class="btn btn-primary">
            <i class="fas fa-print"></i> Imprimir
          </button>
          <button @click="$emit('close')" class="btn btn-secondary">Cerrar</button>
        </div>
      </div>
      <div class="print-mode-selector">
        <label :class="{ active: mode === 'standard' }">
          <input type="radio" v-model="mode" value="standard" /> Formato Normal (Carta/A4)
        </label>
        <label :class="{ active: mode === 'pos' }">
          <input type="radio" v-model="mode" value="pos" /> Formato POS (Ticket 80mm)
        </label>
      </div>
    </div>
  </div>

  <!-- Area de Impresion - Teleported to body for total isolation -->
  <Teleport to="body">
    <div v-if="show" id="print-area" :class="['print-content', mode]">
      <!-- Layout Standard (A4/Letter) matching the provided image -->
      <div v-if="mode === 'standard'" class="standard-layout">
        <!-- Top Header Row -->
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
              <div class="box-title">FACTURA DE VENTA</div>
              <div class="box-content">
                N° <span class="invoice-num">{{ invoice.invoice_number }}</span>
              </div>
            </div>
            <p class="date-label">Fecha: {{ formatDateShort(invoice.issue_date) }}</p>
          </div>
        </div>

        <div class="blue-divider"></div>

        <!-- User Information Section -->
        <div class="section-block">
          <div class="section-header">
            <span class="bar"></span>
            <h2 class="section-title">INFORMACIÓN DEL CLIENTE</h2>
          </div>
          <div class="client-info-grid">
            <div class="info-item"><strong>Cliente:</strong> {{ invoice.partner_name }}</div>
            <div class="info-item"><strong>Teléfono:</strong> {{ invoice.partner_phone || partnerPhone || 'N/A' }}</div>
            <div class="info-item"><strong>Identificación:</strong> {{ invoice.partner_nit || 'N/A' }}</div>
          </div>
        </div>

        <!-- Invoice Details Section -->
        <div class="section-block">
          <div class="section-header">
            <span class="bar"></span>
            <h2 class="section-title">DETALLES DE LA FACTURA</h2>
          </div>
          <table class="details-table">
            <thead>
              <tr>
                <th class="col-desc">Descripción</th>
                <th class="col-serie">Info. Serie</th>
                <th class="col-qty text-center">Cant.</th>
                <th class="col-price text-right">P. Unitario</th>
                <th class="col-desc-amount text-right">Desc.</th>
                <th class="col-subtotal text-right">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="(item, idx) in groupedItems" :key="idx">
                <!-- If it is a group -->
                <template v-if="item.isGroup">
                  <tr class="font-weight-bold bg-light">
                    <td>{{ item.description }}</td>
                    <td>-</td>
                    <td class="text-center">1</td>
                    <td class="text-right">{{ formatNumber(item.unit_price) }}</td>
                    <td class="text-right">{{ formatNumber(item.discount) }}</td>
                    <td class="text-right">{{ formatNumber(item.line_total) }}</td>
                  </tr>
                  <!-- List the parts below without prices -->
                  <tr v-for="part in item.parts" :key="part.id" class="text-muted small">
                    <td style="padding-left: 20px;">- {{ part.description }}</td>
                    <td>{{ part.serial_number || '' }}</td>
                    <td class="text-center">{{ part.quantity }}</td>
                    <td class="text-right">-</td>
                    <td class="text-right">-</td>
                    <td class="text-right">-</td>
                  </tr>
                </template>
                <!-- If it is a regular item -->
                <tr v-else>
                  <td>{{ item.description }}</td>
                  <td>{{ item.serial_number || '' }}</td>
                  <td class="text-center">{{ item.quantity }}</td>
                  <td class="text-right">{{ formatNumber(item.unit_price) }}</td>
                  <td class="text-right">{{ formatNumber(item.discount || 0) }}</td>
                  <td class="text-right">{{ formatNumber(item.line_total) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <!-- Totals Section -->
        <div class="totals-flex">
          <div class="totals-labels">
            <p>Subtotal:</p>
            <p>Impuesto ({{ invoice.tax_rate || 19 }}%):</p>
            <p class="bold-text">TOTAL:</p>
            <p>Total Pagado:</p>
          </div>
          <div class="totals-values">
            <p>{{ formatCOP(calculateSubtotal) }}</p>
            <p>{{ formatCOP(invoice.vat_amount || calculateVAT) }}</p>
            <p class="bold-text">{{ formatCOP(invoice.total_amount) }}</p>
            <p>{{ formatCOP(invoice.total_amount) }}</p>
          </div>
        </div>

        <!-- Signature Section -->
        <div class="signature-row">
          <div class="signature-box">
            <div class="line"></div>
            <p>Firma Cliente</p>
          </div>
          <div class="signature-box">
            <div class="line"></div>
            <p>Recibido / Entregado</p>
          </div>
        </div>

        <!-- Legal Disclaimer -->
        <div v-if="company.invoice_footer_note" class="legal-disclaimer">
          <p style="white-space: pre-line;">{{ company.invoice_footer_note }}</p>
        </div>

        <!-- Pie de Página de Contacto -->
        <div v-if="company.address || company.phone || company.website || company.email" class="invoice-footer">
          <div class="footer-divider"></div>
          <div class="footer-contact">
            <span v-if="company.address" class="footer-item">
              <i class="footer-icon">📍</i>
              {{ company.address }}
            </span>
            <span v-if="company.address && company.phone" class="footer-sep">|</span>
            <span v-if="company.phone" class="footer-item">
              <i class="footer-icon">📞</i>
              Tel: {{ company.phone }}
            </span>
            <span v-if="(company.address || company.phone) && company.website" class="footer-sep">|</span>
            <span v-if="company.website" class="footer-item">
              <i class="footer-icon">🌐</i>
              {{ company.website }}
            </span>
            <span v-if="(company.address || company.phone || company.website) && company.email" class="footer-sep">|</span>
            <span v-if="company.email" class="footer-item">
              <i class="footer-icon">✉</i>
              {{ company.email }}
            </span>
          </div>
        </div>
      </div>

      <!-- Layout POS (Ticket) - Simplified -->
      <div v-else class="pos-layout">
        <div class="pos-header">
          <img v-if="company.logo_url" :src="logoFullUrl" alt="Logo" class="pos-logo" />
          <img v-else src="@/assets/logo.png" alt="Logo" class="pos-logo" />
          <h2 class="pos-company-name">{{ company.name }}</h2>
          <p>NIT: {{ company.nit }}</p>
          <p>{{ company.address }}</p>
        </div>
        <div class="pos-divider">********************************</div>
        <div class="pos-meta">
          <p>FACTURA: {{ invoice.invoice_number }}</p>
          <p>FECHA: {{ formatDateShort(invoice.issue_date) }}</p>
          <p>CLIENTE: {{ invoice.partner_name }}</p>
        </div>
        <div class="pos-divider">--------------------------------</div>
        <div class="pos-items">
          <template v-for="(item, idx) in groupedItems" :key="idx">
            <div v-if="item.isGroup" class="pos-item">
              <div><strong>{{ item.description }}</strong></div>
              <div v-for="part in item.parts" :key="part.id" style="padding-left: 5px; font-size: 10px;">
                - {{ part.description }}
              </div>
              <div class="pos-item-data">
                1 x {{ formatNumber(item.unit_price) }} = {{ formatNumber(item.line_total) }}
              </div>
            </div>
            <div v-else class="pos-item">
              <div>{{ item.description }}</div>
              <div v-if="item.serial_number" style="font-size: 10px; color: #555;">
                Serie: {{ item.serial_number }}
              </div>
              <div class="pos-item-data">
                {{ item.quantity }} x {{ formatNumber(item.unit_price) }} = {{ formatNumber(item.line_total) }}
              </div>
            </div>
          </template>
        </div>
        <div class="pos-divider">--------------------------------</div>
        <div class="pos-totals">
          <div class="pos-row"><span>TOTAL:</span> <span>{{ formatCOP(invoice.total_amount) }}</span></div>
        </div>
        <div class="pos-divider">================================</div>
        <div class="pos-contact">
          <p v-if="company.address">📍 {{ company.address }}</p>
          <p v-if="company.phone">📞 Tel: {{ company.phone }}</p>
          <p v-if="company.website">🌐 {{ company.website }}</p>
          <p v-if="company.email">✉ {{ company.email }}</p>
        </div>
        <div v-if="company.invoice_footer_note" class="pos legal-disclaimer" style="font-size: 8px; text-align: justify; margin: 5px 0; white-space: pre-line;">
          {{ company.invoice_footer_note }}
        </div>
        <div class="pos-divider">================================</div>
        <div class="pos-footer">¡Gracias por su compra!</div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import api from '@/services/api'
import { formatCOP, formatNumber } from '@/utils/formatters'

export default {
  name: 'InvoicePrintModal',
  props: {
    show: { type: Boolean, default: false },
    invoice: { type: Object, required: true },
    company: { type: Object, required: true },
    initialMode: { type: String, default: 'standard' }
  },
  data() {
    return {
      mode: this.initialMode
    }
  },
  computed: {
    groupedItems() {
      if (!this.invoice.items) return [];
      const groups = {};
      const result = [];
      
      this.invoice.items.forEach(item => {
        if (item.assembly_group_id) {
          if (!groups[item.assembly_group_id]) {
            let groupName = "Equipo Ensamblado";
            // Try to extract name from [Name] format in description
            const match = item.description.match(/^\[(.*?)\]/);
            if (match) {
              groupName = "Equipo: " + match[1];
            }
            groups[item.assembly_group_id] = {
              isGroup: true,
              description: groupName,
              parts: [],
              unit_price: 0,
              discount: 0,
              line_total: 0
            };
            result.push(groups[item.assembly_group_id]);
          }
          const g = groups[item.assembly_group_id];
          
          // Clean the description for the part (remove the [Name] prefix if present)
          const cleanItem = { ...item };
          const match = item.description.match(/^\[.*?\]\s*(.*)/);
          if (match) {
            cleanItem.description = match[1];
          }
          
          g.parts.push(cleanItem);
          g.unit_price += (parseFloat(item.unit_price) * parseFloat(item.quantity));
          g.discount += parseFloat(item.discount || 0);
          g.line_total += parseFloat(item.line_total);
        } else {
          result.push({ isGroup: false, ...item });
        }
      });
      return result;
    },
    calculateSubtotal() {
      if (!this.invoice.items) return 0;
      return this.invoice.items.reduce((acc, item) => acc + (parseFloat(item.quantity) * parseFloat(item.unit_price)), 0);
    },
    calculateVAT() {
      if (!this.invoice.items) return 0;
      return this.invoice.items.reduce((acc, item) => acc + (parseFloat(item.tax_amount) || 0), 0);
    },
    partnerPhone() {
      // Small helper to get phone if available in partner_detailed
      return this.invoice.partner?.phone || '';
    },
    regimenLabel() {
      const labels = {
        COMUN: 'RÉGIMEN COMÚN',
        SIMPLE: 'RÉGIMEN SIMPLE DE TRIBUTACIÓN',
        ESPECIAL: 'RÉGIMEN ESPECIAL',
        NO_RESPONSABLE: 'NO RESPONSABLE DE IVA'
      };
      return labels[this.company.regimen] || this.company.regimen || '';
    },
    logoFullUrl() {
      if (this.company.logo_url) {
        return `${api.defaults.baseURL}${this.company.logo_url}`
      }
      return null
    }
  },
  methods: {
    formatCOP,
    formatNumber,
    formatDateShort(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-CO', {
        year: 'numeric', month: '2-digit', day: '2-digit'
      });
    },
    printInvoice() {
      window.print();
    }
  },
  watch: {
    show: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.originalTitle = document.title;
          const num = this.invoice.invoice_number || this.invoice.id;
          document.title = `Factura_${num}`;
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
/* Modal UI Styles (Screen Only) */
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
  transition: all 0.2s;
  border: 2px solid transparent;
}

.print-mode-selector label:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.print-mode-selector label.active { border-color: #007bff; background: #e7f1ff; }

/* Print Area (Hidden on screen) */
#print-area { display: none; }
</style>

<style>
/* Global Print Styles - Final fix using Teleport isolation */
@media print {
  /* Hide the entire application UI */
  #app {
    display: none !important;
  }

  /* Show only the print area which is now at the body level */
  #print-area {
    display: block !important;
    visibility: visible !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    background: white !important;
  }

  /* Ensure page backgrounds are handled correctly */
  @page {
    margin: 1cm;
  }
  
  .pos-layout {
    width: 80mm !important;
    margin: 0 auto !important;
    padding: 5mm !important;
  }
}

/* STANDARD LAYOUT STYLES (Print and Screen Preview) */
.standard-layout {
  font-family: Arial, sans-serif;
  color: #000;
  max-width: 100%;
  margin: 0 auto;
  line-height: 1.4;
}

.invoice-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.header-left { flex: 1; }
.main-logo { width: 300px; height: auto; margin-bottom: 10px; }
.slogan { font-size: 11px; color: #003366; margin: 0; }
.slogan-bold { font-size: 11px; color: #003366; font-weight: bold; margin: 0; }

.header-right { text-align: right; }
.owner-name { font-size: 16px; color: #003366; margin: 0 0 5px 0; font-weight: bold; }
.nit-info { font-size: 11px; color: #003366; margin: 0 0 15px 0; }

.invoice-box {
  border: 2px solid #003366;
  border-radius: 8px;
  padding: 8px 15px;
  display: inline-block;
  min-width: 180px;
  text-align: center;
}

.box-title { font-size: 12px; font-weight: bold; color: #003366; border-bottom: 1px solid #003366; padding-bottom: 4px; margin-bottom: 4px; }
.box-content { font-size: 16px; color: #003366; font-weight: bold; }
.invoice-num { color: #cc0000; }
.date-label { font-size: 12px; margin: 8px 0 0 0; }

.blue-divider { height: 2px; background-color: #003366; margin: 15px 0; }

.section-block { margin-bottom: 25px; }
.section-header { display: flex; align-items: center; margin-bottom: 12px; }
.bar { width: 4px; height: 20px; background-color: #003366; margin-right: 10px; }
.section-title { font-size: 14px; margin: 0; color: #000; letter-spacing: 0.5px; }

.client-info-grid {
  display: flex;
  flex-wrap: wrap;
  padding-left: 15px;
}

.info-item { width: 50%; font-size: 13px; margin-bottom: 5px; }

.details-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
.details-table th { padding: 8px 10px; border: 1px solid #ddd; background: #fff; font-size: 12px; text-align: left; }
.details-table td { padding: 8px 10px; border: 1px solid #ddd; font-size: 12px; height: 35px; }

.text-center { text-align: center; }
.text-right { text-align: right; }

.totals-flex {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  gap: 30px;
}

.totals-labels { text-align: right; font-size: 14px; color: #333; }
.totals-values { text-align: right; font-size: 14px; color: #000; min-width: 120px; }
.totals-labels p, .totals-values p { margin: 5px 0; }
.bold-text { font-weight: bold; }

.signature-row {
  display: flex;
  justify-content: flex-start;
  margin-top: 50px;
  gap: 100px;
}

.signature-box { text-align: center; font-size: 13px; font-weight: bold; }
.signature-box .line { border-top: 1px solid #000; width: 220px; margin-bottom: 8px; }

.legal-disclaimer {
  margin-top: 40px;
  padding-top: 15px;
  border-top: 2px solid #003366;
  font-size: 9px;
  color: #444;
  text-align: justify;
}

/* Pie de Página de Contacto - Standard Layout */
.invoice-footer {
  margin-top: 20px;
}
.footer-divider {
  height: 2px;
  background: linear-gradient(to right, #003366, #0066cc, #003366);
  margin-bottom: 10px;
  border-radius: 2px;
}
.footer-contact {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 10px;
  background-color: #f0f4ff;
  border-radius: 6px;
  font-size: 9.5px;
  color: #003366;
  font-weight: 500;
}
.footer-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
}
.footer-icon {
  font-style: normal;
  font-size: 10px;
}
.footer-sep {
  color: #003366;
  opacity: 0.4;
  font-weight: 300;
}

/* POS LAYOUT */
.pos-layout { width: 80mm; font-family: 'Courier New', monospace; font-size: 12px; }
.pos-logo { width: 60mm; height: auto; margin-bottom: 10px; }
.pos-row { display: flex; justify-content: space-between; }
.pos-contact { font-size: 10px; text-align: center; margin: 5px 0; }
.pos-contact p { margin: 2px 0; }
</style>
