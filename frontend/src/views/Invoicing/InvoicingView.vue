<template>
  <div class="invoicing-view">
    <!-- View A: Historial de Facturas -->
    <div v-if="!showForm">
      <div class="view-header">
        <h2>Facturación</h2>
        <button class="btn btn-primary" @click="showForm = true">+ Nueva Factura</button>
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
                <span :class="['badge', `badge-${(invoice.estado_dian || 'draft').toLowerCase()}`]">
                  {{ invoice.estado_dian || 'Borrador' }}
                </span>
              </td>
              <td>{{ new Date(invoice.issue_date).toLocaleDateString() }}</td>
              <td>
                <div class="actions-cell">
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
            <h3 class="card-title mb-0">Agregar Productos</h3>
            <button type="button" class="btn btn-warning font-weight-bold" @click="showAssemblyModal = true">
              <i class="fas fa-tools mr-1"></i> Armar Equipo
            </button>
          </div>
          <div class="add-item-bar">
            <div class="form-group flex-2 mb-0">
              <select v-model="newItem.product_id" @change="onNewItemProductChange" class="form-control">
                <option value="">Buscar y seleccionar producto...</option>
                <option v-for="prod in products" :key="prod.id" :value="prod.id">
                  {{ prod.name }} - {{ formatCOP(prod.sale_price) }}
                </option>
              </select>
            </div>
            <div class="form-group flex-2 mb-0">
              <input type="text" v-model="newItem.description" placeholder="Nota / Descripción" class="form-control" />
            </div>
            <div class="form-group qty-group mb-0">
              <label class="sr-only">Cantidad</label>
              <input type="number" v-model.number="newItem.quantity" placeholder="1" min="1" class="form-control" />
            </div>
            <div class="form-group qty-group mb-0">
              <label class="sr-only">Descuento</label>
              <input type="number" v-model.number="newItem.discount" placeholder="0" min="0" class="form-control" />
            </div>
            <div class="form-group checkbox-group mb-0">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newItem.apply_tax" />
                IVA (19%)
              </label>
            </div>
            <button type="button" class="btn btn-primary" @click="addItem" :disabled="!newItem.product_id">
              Agregar
            </button>
          </div>
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
                  {{ getProductName(item.product_id) }}
                </td>
                <td>
                  <span v-if="item.assembly_name" class="font-weight-bold text-primary mr-1">[{{ item.assembly_name }}]</span>
                  {{ item.description || '-' }}
                </td>
                <td class="text-right">{{ formatCOP(item.unit_price) }}</td>
                <td class="text-center">{{ item.quantity }}</td>
                <td class="text-right">{{ formatCOP(item.discount) }}</td>
                <td class="text-right">{{ formatCOP(getItemSubtotal(item)) }}</td>
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
    <!-- Modal Crear Cliente/Proveedor -->
    <div class="modal-overlay" v-if="showPartnerForm" @click.self="showPartnerForm = false" style="z-index: 300;">
      <div class="modal">
        <h3>Nuevo Cliente/Proveedor</h3>
        <form @submit.prevent="onPartnerSubmit">
          <div class="form-row-grid">
            <div class="form-group">
              <label>NIT/CC:</label>
              <input v-model="partnerForm.nit" required placeholder="Numero de id" />
            </div>
            <div class="form-group">
              <label>DV:</label>
              <input v-model="partnerForm.dv" maxlength="1" placeholder="Solo empresas" />
            </div>
          </div>
          <div class="form-group">
            <label>Nombre o Razón Social:</label>
            <input v-model="partnerForm.name" required />
          </div>
          <div class="form-row-grid">
            <div class="form-group">
              <label>Tipo:</label>
              <select v-model="partnerForm.partner_type" required>
                <option value="CUSTOMER">Cliente</option>
                <option value="SUPPLIER">Proveedor</option>
                <option value="BOTH">Ambos</option>
              </select>
            </div>
            <div class="form-group">
              <label>Responsabilidad Fiscal:</label>
              <select v-model="partnerForm.responsibility_fiscal" required>
                <option value="NO RESPONSABLE">No Responsable</option>
                <option value="RESPONSABLE IVA">Responsable de IVA</option>
              </select>
            </div>
          </div>
          <div class="form-row-grid">
            <div class="form-group">
              <label>Email:</label>
              <input v-model="partnerForm.email" type="email" />
            </div>
            <div class="form-group">
              <label>Teléfono:</label>
              <input v-model="partnerForm.phone" />
            </div>
          </div>
          <div class="form-group">
            <label>Dirección:</label>
            <input v-model="partnerForm.address" />
          </div>
          <div v-if="error" class="error-message p-2 mb-2 bg-danger text-white rounded">{{ error }}</div>
          <div class="form-actions text-right mt-4">
            <button type="button" class="btn btn-secondary mr-2" @click="showPartnerForm = false">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="submittingPartner">
              {{ submittingPartner ? 'Guardando...' : 'Guardar y Usar' }}
            </button>
          </div>
        </form>
      </div>
    </div>


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
      showPartnerForm: false,
      submitting: false,
      submittingPartner: false,
      error: null,
      searchQuery: '',
      partnerForm: {
        nit: '', dv: '', name: '', partner_type: 'CUSTOMER',
        responsibility_fiscal: 'NO RESPONSABLE', email: '', phone: '', address: ''
      },
      form: {
        invoice_type: 'SALE',
        partner_id: '',
        issue_date: new Date().toISOString().split('T')[0],
        notes: '',
        is_paid: true,
        payment_method: 'CASH',
        amount_received: null,
        items: []
      },
      newItem: {
        product_id: '',
        description: '',
        quantity: 1,
        discount: 0,
        apply_tax: true
      },
      showPrintModal: false,
      showAssemblyModal: false,
      selectedInvoiceForPrint: null,
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
      }
    },
    getProductName(productId) {
      const p = this.products.find(x => x.id === productId);
      return p ? p.name : 'Unknown';
    },
    getItemSubtotal(item) {
      return (item.quantity * item.unit_price) - (Number(item.discount) || 0);
    },
    addItem() {
      if (!this.newItem.product_id) return;
      const product = this.products.find(p => p.id === this.newItem.product_id)
      
      this.form.items.push({
        product_id: this.newItem.product_id,
        description: this.newItem.description,
        quantity: this.newItem.quantity || 1,
        unit_price: product ? (product.sale_price || product.price || 0) : 0,
        discount: this.newItem.discount || 0,
        tax_rate: this.newItem.apply_tax ? 19 : 0
      })

      // Reset new item
      this.newItem = {
        product_id: '',
        description: '',
        quantity: 1,
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
          reference: `Factura Venta INV-${Date.now()}`,

          items: this.form.items.map(item => {
            let desc = item.description;
            if (!item.assembly_group_id) {
              const product = this.products.find(p => p.id === item.product_id)
              desc = item.description ? `${product.name} - ${item.description}` : product.name
            }
            const sub = this.getItemSubtotal(item)
            const tax_amt = sub * (item.tax_rate / 100) || 0
            return {
              description: desc,
              product_id: parseInt(item.product_id) || null,
              quantity: item.quantity,
              unit_price: item.unit_price,
              discount: item.discount, 
              tax_rate: item.tax_rate,
              tax_amount: tax_amt,
              line_total: sub + tax_amt,
              assembly_group_id: item.assembly_group_id || null
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
      this.partnerForm.partner_type = this.form.invoice_type === 'SALE' ? 'CUSTOMER' : 'SUPPLIER'
      this.showPartnerForm = true
    },
    async onPartnerSubmit() {
      this.submittingPartner = true
      this.error = null
      try {
        const payload = {
          nit: this.partnerForm.nit,
          dv: this.partnerForm.dv || null,
          name: this.partnerForm.name,
          partner_type: this.partnerForm.partner_type,
          responsibility_fiscal: this.partnerForm.responsibility_fiscal,
          email: this.partnerForm.email || null,
          phone: this.partnerForm.phone || null,
          address: this.partnerForm.address || null,
          city: '',
          department: '',
          country: 'Colombia'
        }
        
        const response = await api.post('/api/v1/partners/', payload, {
          params: { company_id: this.companyId }
        })
        
        const newPartner = response.data
        await this.loadPartners()
        this.form.partner_id = newPartner.id
        this.showPartnerForm = false
        
        this.partnerForm = {
          nit: '', dv: '', name: '', partner_type: 'CUSTOMER',
          responsibility_fiscal: 'NO RESPONSABLE', email: '', phone: '', address: ''
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al crear socio'
      } finally {
        this.submittingPartner = false
      }
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
    }
  },
  async mounted() {
    await Promise.all([
      this.loadInvoices(),
      this.loadPartners(),
      this.loadProducts(),
      this.loadTreasuryAccounts()
    ])
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

.add-item-bar {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}
.flex-2 { flex: 2; }
.qty-group { width: 90px; }
.checkbox-group {
  display: flex;
  align-items: center;
  height: 38px;
  padding: 0 10px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
  font-weight: normal !important;
  cursor: pointer;
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
</style>