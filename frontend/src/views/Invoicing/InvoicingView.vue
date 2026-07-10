<template>
  <div class="invoicing-view">
    <!-- View A: Historial de Facturas -->
    <div v-if="!showForm">
      <div class="view-header">
        <h2>Facturación</h2>
        <button class="btn btn-primary" @click="showForm = true">+ Nueva Factura</button>
      </div>

      <!-- Resumen de Facturas Pendientes (Notificación) -->
      <div class="summary-cards" v-if="pendingInvoicesCount > 0">
        <div class="summary-card warning-card">
          <div class="summary-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="summary-content">
            <h3>Facturas Pendientes</h3>
            <p class="summary-value">{{ pendingInvoicesCount }} facturas sin cancelar</p>
          </div>
        </div>
        <div class="summary-card danger-card">
          <div class="summary-icon">
            <i class="fas fa-money-bill-wave"></i>
          </div>
          <div class="summary-content">
            <h3>Total Adeudado</h3>
            <p class="summary-value">{{ formatCOP(pendingInvoicesTotal) }}</p>
          </div>
        </div>
      </div>

      <!-- Barra de búsqueda por nombre -->
      <div class="search-bar-wrapper">
        <div class="search-input-group">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Buscar por cliente o proveedor..."
            aria-label="Buscar factura por nombre de cliente"
          />
          <button v-if="searchQuery" class="search-clear-btn" @click="searchQuery = ''" title="Limpiar búsqueda">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <span class="search-results-count" v-if="searchQuery">
          {{ filteredInvoices.length }} resultado{{ filteredInvoices.length !== 1 ? 's' : '' }}
        </span>
      </div>

      <div v-if="loading" class="loading">Cargando facturas...</div>
      <div v-else>
        <table class="data-table" v-if="invoices.length">
          <thead>
            <tr>
              <th>Número</th>
              <th>Tipo</th>
              <th>Cliente/Proveedor</th>
              <th>Subtotal</th>
              <th>IVA</th>
              <th>Total</th>
              <th>Estado Pago</th>
              <th>Estado DIAN</th>
              <th>Fecha</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in filteredInvoices" :key="invoice.id">
              <td>{{ invoice.invoice_number }}</td>
              <td>{{ invoice.invoice_type === 'SALE' ? 'Venta' : 'Compra' }}</td>
              <td>{{ invoice.partner_name || '-' }}</td>
              <td>{{ formatCOP(invoice.subtotal || invoice.total_amount) }}</td>
              <td>{{ formatCOP(invoice.vat_amount || 0) }}</td>
              <td>{{ formatCOP(invoice.total_amount) }}</td>
              <td>
                <span class="badge" :class="{
                  'badge-success': invoice.status === 'PAID',
                  'badge-warning': invoice.status === 'ISSUED' || invoice.status === 'DRAFT',
                  'badge-secondary': invoice.status === 'CANCELLED'
                }">
                  {{ invoice.status === 'PAID' ? 'Pagada' : (invoice.status === 'CANCELLED' ? 'Anulada' : 'Pendiente') }}
                </span>
              </td>
              <td>
                <span :class="['badge', `badge-${(invoice.estado_dian || 'draft').toLowerCase()}`]">
                  {{ invoice.estado_dian || 'Borrador' }}
                </span>
              </td>
              <td>{{ new Date(invoice.issue_date).toLocaleDateString() }}</td>
              <td>
                <div class="actions-cell">
                  <button v-if="invoice.status !== 'PAID' && invoice.status !== 'CANCELLED'" class="btn-action btn-success" @click="openPaymentModal(invoice)" title="Registrar Pago">
                    <i class="fas fa-hand-holding-usd"></i>
                    <span>Pagar</span>
                  </button>
                  <button class="btn-action btn-view" @click="viewInvoice(invoice)" title="Ver detalle">
                    <i class="fas fa-eye"></i>
                    <span>Ver</span>
                  </button>
                  <button class="btn-action btn-print" @click="fetchAndPrint(invoice, 'standard')" title="Imprimir Carta">
                    <i class="fas fa-print"></i>
                    <span>PDF</span>
                  </button>
                  <button class="btn-action btn-print" @click="fetchAndPrint(invoice, 'pos')" title="Imprimir Ticket">
                    <i class="fas fa-receipt"></i>
                    <span>POS</span>
                  </button>
                  <button v-if="invoice.status !== 'CANCELLED'" class="btn-action btn-danger" @click="confirmCancelInvoice(invoice)" title="Anular">
                    <i class="fas fa-ban"></i>
                    <span>Anular</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else-if="searchQuery && filteredInvoices.length === 0" class="empty">
          No se encontraron facturas para "<strong>{{ searchQuery }}</strong>".
        </p>
        <p v-else class="empty">No hay facturas registradas.</p>
      </div>
    </div>

    <!-- View B: Crear Nueva Factura -->
    <div v-else class="invoice-create-view">
      <div class="view-header mb-4">
        <h2>Nueva Factura</h2>
        <button class="btn btn-secondary" @click="closeForm">← Volver al Historial</button>
      </div>

      <form @submit.prevent="openPOS" class="invoice-grid">
        
        <!-- Tarjeta: Datos del Cliente -->
        <div class="card p-4 mb-4">
          <h3 class="card-title">Datos del Cliente</h3>
          <div class="form-row align-items-end">
            <div class="form-group mb-0 flex-grow-1">
              <label>Cliente / Proveedor:</label>
              <select v-model="form.partner_id" required class="form-control form-control-lg">
                <option value="">Buscar cliente por nombre, apellido o ID...</option>
                <option v-for="p in partners" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ p.nit }})
                </option>
              </select>
            </div>
            <div class="ml-3">
              <button type="button" class="btn btn-outline-primary pt-2 pb-2 pl-4 pr-4" @click="openPartnerForm">
                <i class="fas fa-user-plus mr-1"></i> + Nuevo
              </button>
            </div>
          </div>
          <div class="form-row mt-3">
            <div class="form-group mb-0 flex-grow-1">
              <label>Tipo de Documento:</label>
              <select v-model="form.invoice_type" required class="form-control form-control-sm" style="max-width: 250px;">
                <option value="SALE">Venta</option>
                <option value="PURCHASE">Compra</option>
              </select>
            </div>
            <!-- Wallet Balance Display -->
            <div class="ml-auto text-right" v-if="partnerWallet">
              <div class="wallet-badge" :class="{ 'has-balance': partnerWallet.balance > 0 }">
                <span class="label">Saldo Monedero:</span>
                <span class="value">{{ formatCOP(partnerWallet.balance) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tarjeta: Agregar Productos -->
        <div class="card p-4 mb-4 bg-light">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h3 class="card-title mb-0">Agregar Productos / Servicios</h3>
            <button type="button" class="btn btn-warning font-weight-bold" @click="showAssemblyModal = true">
              <i class="fas fa-tools mr-1"></i> Armar Equipo
            </button>
          </div>

          <!-- Fila 1: Selector de Producto o Modo Servicio Manual -->
          <div class="add-item-row">
            <div class="form-group flex-2 mb-0">
              <label class="form-label-sm">Producto del Inventario (opcional)</label>
              <select v-model="newItem.product_id" @change="onNewItemProductChange" class="form-control">
                <option value="">-- Servicio / Item Manual --</option>
                <option v-for="prod in products" :key="prod.id" :value="prod.id">
                  {{ prod.name }} - {{ formatCOP(prod.sale_price) }}
                </option>
              </select>
            </div>
            <div class="form-group flex-2 mb-0">
              <label class="form-label-sm">Descripción del ítem</label>
              <input type="text" v-model="newItem.description" placeholder="Ej: Mano de obra, Limpieza química..." class="form-control" />
            </div>
          </div>

          <!-- Fila 2: Precio, Cantidad, Descuento, IVA, Botón -->
          <div class="add-item-row add-item-row-2 mt-2">
            <div class="form-group mb-0">
              <label class="form-label-sm">Precio Unitario</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input
                  type="number"
                  v-model.number="newItem.unit_price"
                  placeholder="0"
                  min="0"
                  class="form-control"
                  :disabled="!!newItem.product_id"
                  :title="newItem.product_id ? 'El precio se toma del inventario. Puede editarlo en la tabla de detalle.' : ''"
                />
              </div>
            </div>
            <div class="form-group mb-0">
              <label class="form-label-sm">Cantidad</label>
              <input type="number" v-model.number="newItem.quantity" placeholder="1" min="1" class="form-control" />
            </div>
            <div class="form-group mb-0">
              <label class="form-label-sm">Descuento ($)</label>
              <input type="number" v-model.number="newItem.discount" placeholder="0" min="0" class="form-control" />
            </div>
            <div class="form-group checkbox-group mb-0">
              <label class="form-label-sm">&nbsp;</label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="newItem.apply_tax" />
                IVA (19%)
              </label>
            </div>
            <div class="form-group mb-0">
              <label class="form-label-sm">&nbsp;</label>
              <button
                type="button"
                class="btn btn-primary btn-block"
                @click="addItem"
                :disabled="!newItem.product_id && !newItem.description"
              >
                <i class="fas fa-plus mr-1"></i> Agregar
              </button>
            </div>
          </div>

          <p v-if="!newItem.product_id" class="text-muted mt-2" style="font-size:0.82rem;">
            <i class="fas fa-info-circle"></i>
            Modo <strong>Servicio Manual</strong>: ingresa descripción y precio. No descuenta inventario.
          </p>
        </div>

        <!-- Tarjeta: Detalle de Productos -->
        <div class="card p-4 mb-4">
          <h3 class="card-title">Detalle</h3>
          <table class="detail-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Información Adicional</th>
                <th class="text-right">Precio Unit.</th>
                <th class="text-center">Cantidad</th>
                <th class="text-right">Descuento</th>
                <th class="text-right">Subtotal</th>
                <th class="text-center">Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="form.items.length === 0">
                <td colspan="7" class="text-center text-muted p-4">No hay productos agregados.</td>
              </tr>
              <tr v-for="(item, idx) in form.items" :key="idx" :class="{'bg-light': item.assembly_group_id}">
                <td>
                  <span v-if="item.assembly_group_id" class="badge badge-info mr-2" title="Parte de Equipo Armado"><i class="fas fa-tools"></i></span>
                  <span v-if="!item.product_id" class="badge badge-secondary mr-2">Servicio</span>
                  {{ getProductName(item.product_id) }}
                </td>
                <td>
                  <input type="text" v-model="item.description" class="form-control form-control-sm" placeholder="Descripción..." />
                </td>
                <td class="text-right">
                  <div class="input-group input-group-sm justify-content-end">
                    <span class="input-group-text">$</span>
                    <input type="number" v-model.number="item.unit_price" class="form-control form-control-sm text-right" style="max-width: 120px;" />
                  </div>
                </td>
                <td class="text-center">
                  <input type="number" v-model.number="item.quantity" class="form-control form-control-sm text-center mx-auto" style="max-width: 70px;" min="1" />
                </td>
                <td class="text-right">
                  <input type="number" v-model.number="item.discount" class="form-control form-control-sm text-right ml-auto" style="max-width: 100px;" min="0" />
                </td>
                <td class="text-right font-weight-bold">{{ formatCOP(getItemSubtotal(item)) }}</td>
                <td class="text-center">
                  <button type="button" class="btn-icon text-danger" @click="removeItem(idx)" title="Eliminar">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tarjeta: Totales y Botón Final -->
        <div class="totals-section d-flex justify-content-end">
          <div class="totals-box p-4 card" style="min-width: 450px;">
            <div class="total-row">
              <span>Subtotal:</span>
              <span>{{ formatCOP(subtotal) }}</span>
            </div>
            <div class="total-row text-danger" v-if="globalDiscount > 0">
              <span>Descuento Global:</span>
              <span>- {{ formatCOP(globalDiscount) }}</span>
            </div>
            <div class="total-row">
              <span>Impuesto (19%):</span>
              <span>{{ formatCOP(vatTotal) }}</span>
            </div>
            <hr />
            <div class="total-row grand-total text-success mb-3">
              <span>Total:</span>
              <span>{{ formatCOP(grandTotal) }}</span>
            </div>

            <!-- Wallet Application Toggle -->
            <div v-if="partnerWallet && partnerWallet.balance > 0" class="wallet-apply-box p-3 mb-3">
              <label class="d-flex align-items-center cursor-pointer">
                <input type="checkbox" v-model="applyWalletBalance" class="mr-2 custom-checkbox" />
                <span>Aplicar Saldo Monedero (Disponible: <strong>{{ formatCOP(partnerWallet.balance) }}</strong>)</span>
              </label>
              <div v-if="applyWalletBalance" class="mt-2 pl-4">
                <div class="total-row text-primary font-weight-bold">
                  <span>Monto a aplicar:</span>
                  <span>- {{ formatCOP(walletAmountToApply) }}</span>
                </div>
                <div class="total-row grand-total text-success mt-2" style="font-size: 1.2rem;">
                  <span>Restante a Pagar:</span>
                  <span>{{ formatCOP(remainingTotalAfterWallet) }}</span>
                </div>
              </div>
            </div>

            <!-- Sección Inline de Pago -->
            <div class="payment-inline p-3 bg-light rounded" style="border: 1px dashed #ccc;">
              <div class="form-row-grid mb-2">
                <div class="form-group mb-0">
                  <label>Estado de Pago:</label>
                  <select v-model="form.is_paid" class="form-control form-control-sm">
                    <option :value="true">Pagado</option>
                    <option :value="false">Pendiente (Borrador/Crédito)</option>
                  </select>
                </div>
                <div class="form-group mb-0" v-if="form.is_paid">
                  <label>Método de Pago:</label>
                  <select v-model="form.payment_method" class="form-control form-control-sm">
                    <option value="CASH">Efectivo</option>
                    <option value="TRANSFER">Transferencia</option>
                    <option value="CARD">Tarjeta</option>
                    <option value="WALLET" v-if="partnerWallet && partnerWallet.balance >= grandTotal">Monedero (Saldo: {{ formatCOP(partnerWallet.balance) }})</option>
                  </select>
                </div>
              </div>

              <!-- Calculadora de Cambio si es Efectivo -->
              <div v-if="form.is_paid && form.payment_method === 'CASH'" class="form-group mt-2">
                <label>Monto Recibido (Calculadora de cambio):</label>
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input type="number" v-model.number="form.amount_received" class="form-control form-control-sm" placeholder="0" />
                </div>
                <small class="text-muted d-block mt-1" v-if="changeAmount > 0">
                  Cambio a Devolver: <strong class="text-danger">{{ formatCOP(changeAmount) }}</strong>
                </small>
              </div>
            </div>

            <div class="action-buttons mt-4 text-right">
              <button type="button" class="btn btn-secondary mr-2" @click="closeForm">Cancelar</button>
              <button type="button" class="btn btn-success btn-lg" :disabled="submitting" @click="openPOS">
                <span v-if="submitting">Generando...</span>
                <span v-else>Generar Factura</span>
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Modales Adicionales -->
    <!-- Modal de Impresión -->
    <InvoicePrintModal 
      v-if="showPrintModal"
      :show="showPrintModal"
      :invoice="selectedInvoiceForPrint"
      :company="currentCompany"
      :initialMode="printMode"
      @close="showPrintModal = false"
    />

    <!-- Modal Armar Equipo -->
    <EquipoAssemblyModal 
      v-if="showAssemblyModal"
      :show="showAssemblyModal"
      :products="products"
      @close="showAssemblyModal = false"
      @confirm="onAssemblyConfirm"
    />

    <!-- Modal Registrar Pago -->
    <div v-if="showPaymentModal" class="modal-backdrop">
      <div class="modal-content payment-modal" style="max-width: 450px;">
        <div class="modal-header">
          <h3>Registrar Pago</h3>
          <button class="close-btn" @click="closePaymentModal">&times;</button>
        </div>
        <div class="modal-body" v-if="invoiceToPay">
          <p>Factura: <strong>{{ invoiceToPay.invoice_number }}</strong></p>
          <p>Cliente: <strong>{{ invoiceToPay.partner_name }}</strong></p>
          <p class="mb-4">Monto a pagar: <strong class="text-success" style="font-size: 1.2rem;">{{ formatCOP(invoiceToPay.total_amount) }}</strong></p>
          
          <div class="form-group">
            <label>Método de Pago:</label>
            <select v-model="paymentForm.payment_method" class="form-control" @change="fetchWalletForPayment">
              <option value="CASH">Efectivo</option>
              <option value="TRANSFER">Transferencia / Banco</option>
              <option value="CARD">Tarjeta de Crédito/Débito</option>
              <!-- Show WALLET only if client has enough balance -->
              <option v-if="paymentWallet && paymentWallet.balance >= invoiceToPay.total_amount" value="WALLET">
                Monedero (Saldo: {{ formatCOP(paymentWallet.balance) }})
              </option>
            </select>
            <small v-if="paymentWallet && paymentWallet.balance < invoiceToPay.total_amount" class="text-muted d-block mt-1">
              * El cliente tiene saldo en monedero ({{ formatCOP(paymentWallet.balance) }}), pero no es suficiente para cubrir la factura.
            </small>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePaymentModal">Cancelar</button>
          <button class="btn btn-success font-weight-bold" @click="confirmPayment" :disabled="submittingPayment">
            <span v-if="submittingPayment">Procesando...</span>
            <span v-else>Confirmar Pago</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { formatCOP } from '@/utils/formatters'
import InvoicePrintModal from '@/components/Invoicing/InvoicePrintModal.vue'
import EquipoAssemblyModal from '@/components/Invoicing/EquipoAssemblyModal.vue'

export default {
  name: 'InvoicingView',
  components: {
    InvoicePrintModal,
    EquipoAssemblyModal
  },
  data() {
    return {
      invoices: [],
      partners: [],
      products: [],
      treasuryAccounts: { cash_accounts: [], bank_accounts: [] },
      loading: true,
      showForm: false,
      submitting: false,
      error: null,
      searchQuery: '',
      form: {
        invoice_type: 'SALE',
        partner_id: '',
        issue_date: new Date().toISOString().split('T')[0],
        notes: '',
        is_paid: true,
        payment_method: 'CASH',
        amount_received: null,
        repair_id: null,
        items: []
      },
      newItem: {
        product_id: '',
        description: '',
        quantity: 1,
        unit_price: 0,
        discount: 0,
        apply_tax: true
      },
      showPrintModal: false,
      showAssemblyModal: false,
      showPaymentModal: false,
      selectedInvoiceForPrint: null,
      invoiceToPay: null,
      paymentForm: {
        payment_method: 'CASH',
        payment_account_id: null
      },
      paymentWallet: null,
      submittingPayment: false,
      printMode: 'standard',
      partnerWallet: null,
      applyWalletBalance: false
    }
  },
  watch: {
    'form.partner_id': function(newVal) {
      if (newVal) {
        this.fetchPartnerWallet(newVal)
        this.applyWalletBalance = false
      } else {
        this.partnerWallet = null
        this.applyWalletBalance = false
      }
    }
  },
  computed: {
    filteredInvoices() {
      if (!this.searchQuery.trim()) return this.invoices
      const q = this.searchQuery.trim().toLowerCase()
      return this.invoices.filter(inv =>
        (inv.partner_name || '').toLowerCase().includes(q)
      )
    },
    pendingInvoices() {
      return this.invoices.filter(inv => inv.status === 'DRAFT' || inv.status === 'ISSUED')
    },
    pendingInvoicesCount() {
      return this.pendingInvoices.length
    },
    pendingInvoicesTotal() {
      return this.pendingInvoices.reduce((sum, inv) => sum + Number(inv.total_amount), 0)
    },
    selectedPartnerName() {
      if (!this.form.partner_id) return 'Cliente Generales';
      const p = this.partners.find(x => x.id === this.form.partner_id);
      return p ? p.name : 'Cliente Generales';
    },
    currentCompany() {
      return this.$store.getters['company/getCompany'] || {}
    },
    companyId() {
      return this.currentCompany.id || 1
    },
    subtotal() {
      return this.form.items.reduce((sum, item) => {
        return sum + this.getItemSubtotal(item)
      }, 0)
    },
    globalDiscount() {
      return this.form.items.reduce((sum, item) => sum + (Number(item.discount) || 0), 0)
    },
    vatTotal() {
      return this.form.items.reduce((sum, item) => {
        const sub = this.getItemSubtotal(item)
        return sum + (sub * (item.tax_rate / 100))
      }, 0)
    },
    grandTotal() {
      return this.subtotal + this.vatTotal
    },
    walletAmountToApply() {
      if (!this.applyWalletBalance || !this.partnerWallet) return 0;
      return Math.min(this.partnerWallet.balance, this.grandTotal);
    },
    remainingTotalAfterWallet() {
      return this.grandTotal - this.walletAmountToApply;
    },
    changeAmount() {
      if (!this.form.amount_received || this.form.amount_received <= this.remainingTotalAfterWallet) return 0;
      return this.form.amount_received - this.remainingTotalAfterWallet;
    }
  },
  methods: {
    formatCOP,
    async loadInvoices() {
      try {
        const response = await api.get('/api/v1/invoicing/', {
          params: { company_id: this.companyId }
        })
        this.invoices = response.data
      } catch (err) {
        console.error('Error loading invoices:', err)
      }
    },
    async loadPartners() {
      try {
        const response = await api.get('/api/v1/partners/', {
          params: { company_id: this.companyId }
        })
        this.partners = response.data
      } catch (err) {
        console.error('Error loading partners:', err)
      }
    },
    async fetchPartnerWallet(partnerId) {
      try {
        const response = await api.get('/api/v1/wallet/', {
          params: { company_id: this.companyId }
        })
        // Find the wallet for this partner
        const wallets = response.data || []
        this.partnerWallet = wallets.find(w => w.partner_id === parseInt(partnerId)) || null
        
        // If wallet doesn't have enough balance and it was selected, reset to CASH
        if (this.form.payment_method === 'WALLET' && (!this.partnerWallet || this.partnerWallet.balance < this.grandTotal)) {
          this.form.payment_method = 'CASH'
        }
      } catch (err) {
        console.error('Error fetching wallet:', err)
        this.partnerWallet = null
      }
    },
    async loadProducts() {
      try {
        const response = await api.get('/api/v1/inventory/', {
          params: { company_id: this.companyId }
        })
        this.products = response.data
      } catch (err) {
        console.error('Error loading products:', err)
      }
    },
    async loadTreasuryAccounts() {
      try {
        const response = await api.get('/api/v1/treasury/summary/', {
          params: { company_id: this.companyId }
        })
        this.treasuryAccounts = response.data || { cash_accounts: [], bank_accounts: [] }
      } catch (err) {
        console.error('Error loading treasury accounts:', err)
      }
    },
    onNewItemProductChange() {
      const product = this.products.find(p => p.id === this.newItem.product_id)
      if (product) {
        this.newItem.description = ''
        // Auto-rellenar el número de serie con el barcode del producto.
        // En inventario, productos serializados usan el barcode como su número de serie único.
        this.newItem.serial_number = product.barcode || ''
      } else {
        this.newItem.serial_number = ''
      }
    },
    getProductName(productId) {
      if (!productId) return 'Servicio / Mano de Obra';
      const p = this.products.find(x => x.id === productId);
      return p ? p.name : 'Desconocido';
    },
    getItemSubtotal(item) {
      return (item.quantity * item.unit_price) - (Number(item.discount) || 0);
    },
    addItem() {
      if (!this.newItem.product_id && !this.newItem.description) {
        alert("Debe seleccionar un producto o ingresar una descripción para el servicio manual.");
        return;
      }
      
      const product = this.newItem.product_id ? this.products.find(p => p.id === this.newItem.product_id) : null;
      const unitPrice = product ? (product.sale_price || product.price || 0) : (this.newItem.unit_price || 0);
      
        this.form.items.push({
          product_id: this.newItem.product_id || null,
          description: this.newItem.description || (product ? product.name : ''),
          quantity: this.newItem.quantity || 1,
          unit_price: unitPrice,
          discount: this.newItem.discount || 0,
          tax_rate: this.newItem.apply_tax ? 19 : 0,
          serial_number: this.newItem.serial_number || null
        })

      // Reset new item
      this.newItem = {
        product_id: '',
        description: '',
        quantity: 1,
        unit_price: 0,
        discount: 0,
        apply_tax: true
      }
    },
    onAssemblyConfirm(assembledItems) {
      // Add all items generated from the assembly modal to the invoice
      assembledItems.forEach(item => {
        this.form.items.push(item);
      });
    },
    removeItem(idx) {
      this.form.items.splice(idx, 1)
    },
    closeForm() {
      this.showForm = false;
      this.form.items = [];
      this.form.partner_id = '';
      this.form.is_paid = true;
      this.form.payment_method = 'CASH';
      this.form.amount_received = null;
      this.error = null;
    },
    async openPOS() {
      if (!this.form.partner_id) {
        alert("Por favor, seleccione un Cliente/Proveedor antes de generar la factura.");
        return;
      }
      if (this.form.items.length === 0) {
        alert("Agregue al menos un producto a la factura.");
        return;
      }

      this.submitting = true
      this.error = null
      
      // Auto-assign account logic exactly like the POS modal would do
      let paymentAccountType = null;
      let paymentAccountId = null;
      
      if (this.form.is_paid && this.form.payment_method !== 'CREDIT') {
        if (this.form.payment_method === 'CASH') {
          if (this.treasuryAccounts.cash_accounts?.length > 0) {
            paymentAccountType = 'CASH';
            paymentAccountId = this.treasuryAccounts.cash_accounts[0].id;
          }
        } else {
          if (this.treasuryAccounts.bank_accounts?.length > 0) {
            paymentAccountType = 'BANK';
            paymentAccountId = this.treasuryAccounts.bank_accounts[0].id;
          }
        }
      }

      try {
        const payload = {
          invoice_type: this.form.invoice_type,
          partner_id: parseInt(this.form.partner_id),
          issue_date: new Date(this.form.issue_date).toISOString(),
          total_amount: this.grandTotal,
          
          is_paid: this.form.is_paid,
          payment_method: this.form.is_paid ? this.form.payment_method : 'CREDIT',
          amount_paid: this.form.is_paid ? this.grandTotal : 0,
          payment_account_type: paymentAccountType,
          payment_account_id: paymentAccountId,
          wallet_amount_applied: this.walletAmountToApply,
          repair_id: this.form.repair_id,
          reference: `Factura Venta INV-${Date.now()}`,

          items: this.form.items.map(item => {
            let desc = item.description || '';
            if (!item.assembly_group_id) {
              if (item.product_id) {
                // Producto del inventario: combinar nombre del producto con descripción adicional
                const product = this.products.find(p => p.id === item.product_id)
                const productName = product ? product.name : ''
                desc = item.description ? `${productName} - ${item.description}` : productName
              }
              // Si NO hay product_id (servicio manual), usar la descripción tal cual
            }
            const sub = this.getItemSubtotal(item)
            const tax_amt = sub * ((item.tax_rate || 0) / 100)
        return {
          description: desc,
          product_id: item.product_id ? parseInt(item.product_id) : null,
          quantity: item.quantity,
          unit_price: item.unit_price,
          discount: item.discount,
          tax_rate: item.tax_rate || 0,
          tax_amount: tax_amt,
          line_total: sub + tax_amt,
          assembly_group_id: item.assembly_group_id || null,
          serial_number: item.serial_number || null
        }
          })
        }
        await api.post('/api/v1/invoicing/with-items/', payload, {
          params: { company_id: this.companyId }
        })
        
        this.closeForm()
        await this.loadInvoices()
        await this.loadTreasuryAccounts()
      } catch (err) {
        const detail = err.response?.data?.detail
        if (Array.isArray(detail)) {
          alert(detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('\n'))
        } else if (typeof detail === 'string') {
          alert(detail)
        } else {
          alert('Error al crear la factura y pago')
        }
      } finally {
        this.submitting = false
      }
    },
    viewInvoice(invoice) {
      this.fetchAndPrint(invoice, 'standard')
    },
    async fetchAndPrint(invoice, mode) {
      try {
        const res = await api.get(`/api/v1/invoicing/${invoice.id}`, {
          params: { company_id: this.companyId }
        })
        this.selectedInvoiceForPrint = res.data
        this.printMode = mode
        // Ensure partner data is available for print
        if (!this.selectedInvoiceForPrint.partner_name) {
          this.selectedInvoiceForPrint.partner_name = invoice.partner_name
        }
        this.selectedInvoiceForPrint.partner_nit = invoice.partner_nit || ''
        this.selectedInvoiceForPrint.partner_address = invoice.partner_address || ''
        this.selectedInvoiceForPrint.partner_phone = invoice.partner_phone || ''
        
        this.showPrintModal = true
        // Set mode in next tick or after modal opens
        this.$nextTick(() => {
          // This might need a ref to the modal to set mode directly or via a prop
          // For now we rely on the modal's internal mode which defaults to standard
        })
      } catch (err) {
        console.error('Error fetching invoice for print:', err)
        alert('Error al obtener los detalles de la factura')
      }
    },
    openPartnerForm() {
      // Save current form state to session storage so we don't lose it
      sessionStorage.setItem('invoicingDraftForm', JSON.stringify(this.form));
      sessionStorage.setItem('invoicingShowForm', 'true');
      this.$router.push('/partners/new?redirect=/invoicing');
    },
    async confirmCancelInvoice(invoice) {
      const message = `¡ADVERTENCIA! Anular la factura ${invoice.invoice_number} revertirá el stock de inventario y generará un asiento contable de reversión. ¿Desea continuar?`
      if (!confirm(message)) return

      try {
        await api.post(`/api/v1/invoicing/${invoice.id}/cancel`, null, {
          params: { company_id: this.companyId }
        })
        alert('Factura anulada con éxito')
        await this.loadInvoices()
        await this.loadTreasuryAccounts()
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al anular la factura')
      }
    },
    async openPaymentModal(invoice) {
      this.invoiceToPay = invoice;
      this.paymentForm = { payment_method: 'CASH', payment_account_id: null };
      this.paymentWallet = null;
      this.showPaymentModal = true;
      await this.fetchWalletForPayment();
    },
    closePaymentModal() {
      this.showPaymentModal = false;
      this.invoiceToPay = null;
    },
    async fetchWalletForPayment() {
      if (!this.invoiceToPay) return;
      try {
        const response = await api.get('/api/v1/wallet/', {
          params: { company_id: this.companyId }
        });
        const wallets = response.data || [];
        this.paymentWallet = wallets.find(w => w.partner_id === parseInt(this.invoiceToPay.partner_id)) || null;
      } catch (err) {
        console.error('Error fetching wallet for payment:', err);
      }
    },
    async confirmPayment() {
      if (!this.invoiceToPay) return;
      this.submittingPayment = true;
      try {
        await api.post(`/api/v1/invoicing/${this.invoiceToPay.id}/pay`, this.paymentForm, {
          params: { company_id: this.companyId }
        });
        alert('Pago registrado correctamente');
        this.closePaymentModal();
        await this.loadInvoices();
        await this.loadTreasuryAccounts();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al registrar el pago');
      } finally {
        this.submittingPayment = false;
      }
    }
  },
  async mounted() {
    await Promise.all([
      this.loadInvoices(),
      this.loadPartners(),
      this.loadProducts(),
      this.loadTreasuryAccounts()
    ])

    // Restore draft if exists
    const draft = sessionStorage.getItem('invoicingDraftForm');
    const showDraft = sessionStorage.getItem('invoicingShowForm');
    if (draft && showDraft === 'true') {
      try {
        this.form = JSON.parse(draft);
        this.showForm = true;
      } catch (e) {
        console.error('Error parsing draft invoice form', e);
      }
      sessionStorage.removeItem('invoicingDraftForm');
      sessionStorage.removeItem('invoicingShowForm');
    }

    const lastPartnerId = sessionStorage.getItem('lastCreatedPartnerId');
    if (lastPartnerId) {
      this.form.partner_id = parseInt(lastPartnerId);
      this.showForm = true; // ensure form is visible
      sessionStorage.removeItem('lastCreatedPartnerId');
    }
    
    // Handle Repair Order redirection
    const repairId = this.$route.query.repair_id;
    if (repairId) {
      this.loading = true;
      try {
        const response = await api.get(`/api/v1/repair/${repairId}`, {
          params: { company_id: this.companyId }
        });
        const repair = response.data;
        
        this.form.partner_id = repair.partner_id;
        this.form.repair_id = parseInt(repairId);
        this.form.notes = `Orden de Reparación #${repair.order_number}`;
        
        // Map repair items to invoice items
        this.form.items = (repair.items || [])
          .filter(item => {
            // Filtrar ítem de identificación del equipo: costo 0 y sin producto asociado
            return !(Number(item.unit_cost) === 0 && !item.product_id);
          })
          .map(item => {
            return {
              product_id: item.product_id,
              description: item.description,
              quantity: item.quantity,
              unit_price: Number(item.unit_cost),
              discount: Number(item.discount) || 0,
              tax_rate: 19 // Default tax rate for Colombian invoices
            };
          });
        
        this.showForm = true;
      } catch (err) {
        console.error('Error fetching repair order:', err);
        alert('Error al cargar datos de la orden de reparación');
      }
    }

    this.loading = false
  }
}
</script>

<style scoped>
.invoicing-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: 1px solid #eaeaea;
}
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1.25rem;
  color: #333;
}
.bg-light {
  background-color: #f8f9fa !important;
}

.d-flex { display: flex; }
.justify-content-end { justify-content: flex-end; }
.align-items-end { align-items: flex-end; }
.flex-grow-1 { flex-grow: 1; }
.mb-0 { margin-bottom: 0 !important; }
.mb-4 { margin-bottom: 1.5rem !important; }
.mt-3 { margin-top: 1rem !important; }
.mt-4 { margin-top: 1.5rem !important; }
.p-4 { padding: 1.5rem !important; }
.mr-2 { margin-right: 0.5rem !important; }
.ml-3 { margin-left: 1rem !important; }
.pr-4 { padding-right: 1.5rem; }
.pl-4 { padding-left: 1.5rem; }
.pt-2 { padding-top: 0.5rem; }
.pb-2 { padding-bottom: 0.5rem; }
.text-right { text-align: right; }
.center { text-align: center; }
.text-danger { color: #dc3545; }
.text-success { color: #28a745; }
.text-muted { color: #6c757d; }

.form-row {
  display: flex;
}
.form-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: border-color 0.15s;
}
.form-control:focus {
  border-color: #80bdff;
  outline: 0;
}
.form-control-lg {
  padding: 0.75rem 1rem;
  font-size: 1.1rem;
}

.btn-outline-primary {
  color: #007bff;
  border: 1px solid #007bff;
  background: white;
  border-radius: 4px;
}
.btn-outline-primary:hover {
  background: #007bff;
  color: white;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.actions-cell {
  display: flex;
  justify-content: center;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-view {
  background-color: #f0f7ff;
  color: #007bff;
  border-color: #cce5ff;
}

.btn-print {
  background-color: #f6ffed;
  color: #52c41a;
  border-color: #b7eb8f;
}

.btn-print:hover {
  background-color: #52c41a;
  color: white;
  border-color: #52c41a;
}

.btn-view:hover {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-view i {
  font-size: 0.9rem;
}

.btn-danger {
  background-color: #fff1f0;
  color: #f5222d;
  border-color: #ffa39e;
}

.btn-danger:hover {
  background-color: #f5222d;
  color: white;
  border-color: #f5222d;
}

.add-item-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}
.add-item-row-2 {
  align-items: flex-end;
}
.add-item-row .form-group {
  min-width: 100px;
}
.flex-2 { flex: 2; min-width: 180px; }
.qty-group { width: 90px; }
.form-label-sm {
  display: block;
  font-size: 0.78rem;
  color: #666;
  margin-bottom: 0.3rem;
  font-weight: 500;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
  height: 38px;
  font-weight: normal !important;
  cursor: pointer;
}
.btn-block {
  width: 100%;
  white-space: nowrap;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.detail-table th {
  padding: 10px;
  border-bottom: 2px solid #eee;
  color: #666;
  font-weight: 600;
  text-align: left;
}
.detail-table th.text-center, .detail-table td.text-center { text-align: center; }
.detail-table th.text-right, .detail-table td.text-right { text-align: right; }
.detail-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
}

.totals-box {
  min-width: 350px;
  background: #fdfdfd;
}
.total-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 0.95rem;
}
.grand-total {
  font-size: 1.25rem;
  font-weight: bold;
}

.input-group {
  display: flex;
  align-items: center;
}
.input-group-text {
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  color: #495057;
  text-align: center;
  white-space: nowrap;
  background-color: #e9ecef;
  border: 1px solid #ced4da;
  border-radius: 0.25rem 0 0 0.25rem;
}
.input-group .form-control {
  border-radius: 0 0.25rem 0.25rem 0;
}
.payment-inline label {
  font-weight: 600;
}
.d-block { display: block; }

/* Modals re-used for Partner Form */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

/* Base Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.data-table th, .data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
}
.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #4a5568;
}
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 500;
}
.badge-draft { background: #fefcbf; color: #744210; }
.badge-paid { background: #c6f6d5; color: #22543d; }

/* === Search Bar === */
.search-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.search-input-group {
  position: relative;
  flex: 1;
  max-width: 420px;
}
.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
  pointer-events: none;
  font-size: 0.9rem;
}
.search-input {
  width: 100%;
  padding: 0.55rem 2.5rem 0.55rem 2.4rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff;
  box-sizing: border-box;
}
.search-input:focus {
  outline: none;
  border-color: #4c9be8;
  box-shadow: 0 0 0 3px rgba(76, 155, 232, 0.15);
}
.search-clear-btn {
  position: absolute;
  right: 0.7rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
  border-radius: 50%;
  line-height: 1;
  transition: color 0.15s;
}
.search-clear-btn:hover {
  color: #e53e3e;
}
.search-results-count {
  font-size: 0.82rem;
  color: #6c757d;
  white-space: nowrap;
}

.wallet-badge {
  display: inline-flex;
  flex-direction: column;
  background: #f8f9fa;
  padding: 8px 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}
.wallet-badge.has-balance {
  background: #e8f5e9;
  border-color: #a5d6a7;
}
.wallet-badge .label {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
  font-weight: bold;
}
.wallet-badge .value {
  font-size: 1.1rem;
  font-weight: 800;
  color: #2e7d32;
}

.ml-auto { margin-left: auto !important; }

.wallet-apply-box {
  background: #f0f7ff;
  border: 1px solid #c2e0ff;
  border-radius: 12px;
  margin-top: 10px;
}
.wallet-apply-box:hover {
  border-color: #007bff;
}
.cursor-pointer { cursor: pointer; }
.custom-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
.font-weight-bold { font-weight: bold; }

/* === Summary / Notification Cards === */
.summary-cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  min-width: 260px;
  flex: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  animation: slideIn 0.3s ease;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.warning-card {
  background: linear-gradient(135deg, #fff8e1, #ffe57f33);
  border: 1px solid #ffe082;
}
.danger-card {
  background: linear-gradient(135deg, #ffebee, #ff5252 10%);
  border: 1px solid #ef9a9a;
}
.summary-icon {
  font-size: 2rem;
  opacity: 0.7;
}
.warning-card .summary-icon { color: #f59e0b; }
.danger-card  .summary-icon { color: #ef4444; }
.summary-content h3 {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #555;
}
.summary-value {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #1a202c;
}

/* === Payment status badges === */
.badge-success  { background: #d1fae5; color: #065f46; }
.badge-warning  { background: #fef3c7; color: #92400e; }
.badge-secondary { background: #e2e8f0; color: #4a5568; }

/* === Pay button === */
.btn-success {
  background-color: #f0fff4;
  color: #276749;
  border: 1px solid #9ae6b4;
}
.btn-success:hover {
  background-color: #38a169;
  color: white;
  border-color: #38a169;
}

/* === Payment Modal === */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.payment-modal {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  overflow: hidden;
  width: 90%;
}
.payment-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #1a365d, #2b6cb0);
  color: white;
}
.payment-modal .modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
}
.payment-modal .close-btn {
  background: none;
  border: none;
  color: rgba(255,255,255,0.8);
  font-size: 1.6rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  transition: color 0.15s;
}
.payment-modal .close-btn:hover { color: white; }
.payment-modal .modal-body {
  padding: 1.5rem;
}
.payment-modal .modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}
</style>