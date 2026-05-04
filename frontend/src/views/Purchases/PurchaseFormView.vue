<template>
  <div class="purchase-create-view">
    <div class="view-header mb-4">
      <h2>{{ purchaseId ? 'Editar Compra' : 'Nueva Compra' }}</h2>
      <button class="btn btn-secondary" @click="$emit('close')">← Volver al Historial</button>
    </div>

    <form @submit.prevent="submitPurchase" class="purchase-grid">
      
      <!-- Tarjeta: Cargar PDF Inteligente -->
      <div class="card p-4 mb-4 bg-light" v-if="!purchaseId">
        <h3 class="card-title text-primary"><i class="fas fa-magic"></i> Carga Inteligente de Factura (PDF)</h3>
        <p class="text-muted small">Sube el PDF de la factura y extraeremos los datos del proveedor y los productos automáticamente usando IA.</p>
        <div class="d-flex align-items-center mt-2">
          <input type="file" ref="fileInput" accept=".pdf" class="form-control" style="max-width: 400px; margin-right: 15px;" @change="handleFileSelected" />
          <button type="button" class="btn btn-primary" @click="uploadPdf" :disabled="!selectedFile || isExtracting">
            <span v-if="isExtracting"><i class="fas fa-spinner fa-spin mr-2"></i> Procesando...</span>
            <span v-else><i class="fas fa-upload mr-2"></i> Extraer Datos</span>
          </button>
        </div>
      </div>
      
      <!-- Tarjeta: Datos del Proveedor -->
      <div class="card p-4 mb-4">
        <h3 class="card-title">Datos del Proveedor</h3>
        <div class="form-row align-items-end">
          <div class="form-group mb-0 flex-grow-1">
            <label>Proveedor *</label>
            <select v-model="form.partner_id" required class="form-control">
              <option value="">Seleccionar proveedor...</option>
              <option v-for="p in suppliers" :key="p.id" :value="p.id">
                {{ p.name }} ({{ p.document_id || p.nit || 'S/N' }})
              </option>
            </select>
          </div>
          <div class="ml-3">
            <button type="button" class="btn btn-outline-primary" @click="openPartnerForm">
              <i class="fas fa-user-plus mr-1"></i> + Nuevo
            </button>
          </div>
        </div>

        <div class="form-row-grid mt-3">
          <div class="form-group mb-0">
            <label>Número de Factura *</label>
            <input v-model="form.purchase_number" type="text" required class="form-control" placeholder="Ej: FAC-1234" />
          </div>
          <div class="form-group mb-0">
            <label>Fecha de Compra *</label>
            <input v-model="form.purchase_date" type="date" required class="form-control" />
          </div>
          <div class="form-group mb-0">
            <label>Fecha de Vencimiento</label>
            <input v-model="form.due_date" type="date" class="form-control" />
          </div>
          <div class="form-group mb-0">
            <label>Método de Pago *</label>
            <select v-model="form.payment_method" required class="form-control">
              <option value="CASH">Efectivo</option>
              <option value="BANK_TRANSFER">Transferencia</option>
              <option value="CHECK">Cheque</option>
              <option value="CREDIT">Crédito</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Tarjeta: Agregar Productos -->
      <div class="card p-4 mb-4 bg-light">
        <h3 class="card-title">Agregar Productos</h3>
        <div class="add-item-bar">
          <div class="form-group flex-2 mb-0">
            <select v-model="newItem.product_id" @change="onNewItemProductChange" class="form-control">
              <option value="">Buscar y seleccionar producto...</option>
              <option v-for="prod in products" :key="prod.id" :value="prod.id">
                {{ prod.name }} - Stock: {{ prod.stock_level }}
              </option>
            </select>
          </div>
          <div class="form-group qty-group mb-0">
            <input type="number" v-model.number="newItem.quantity" placeholder="Cant." min="0.01" step="0.01" class="form-control" />
          </div>
          <div class="form-group qty-group mb-0">
            <input type="number" v-model.number="newItem.unit_price" placeholder="Precio" min="0" step="0.01" class="form-control" />
          </div>
          <div class="form-group qty-group mb-0">
            <input type="number" v-model.number="newItem.tax_rate" placeholder="IVA %" min="0" max="100" class="form-control" />
          </div>
          <div class="form-group qty-group mb-0">
            <input type="text" v-model="newItem.serial_number" placeholder="No. Serie (Opcional)" class="form-control" />
          </div>
          <button type="button" class="btn btn-primary" @click="addItem" :disabled="!newItem.product_id">
            Agregar
          </button>
        </div>
      </div>

      <!-- Tarjeta: Detalle de la Compra -->
      <div class="card p-4 mb-4">
        <h3 class="card-title">Detalle de la Compra</h3>
        <table class="detail-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>No. Serie</th>
              <th class="text-right">Precio Unit.</th>
              <th class="text-center">Cantidad</th>
              <th class="text-right">IVA %</th>
              <th class="text-right">Total</th>
              <th class="text-center">Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="form.items.length === 0">
              <td colspan="7" class="text-center text-muted p-4">No hay productos agregados.</td>
            </tr>
            <tr v-for="(item, idx) in form.items" :key="idx">
              <td v-if="!item.product_id">
                <div style="display: flex; gap: 5px; align-items: center;">
                  <select v-model="item.product_id" class="form-control form-control-sm unmatched-select" style="min-width: 150px;">
                    <option value="">⚠️ {{ item.description || 'Sin asignar' }}</option>
                    <option v-for="prod in products" :key="prod.id" :value="prod.id">{{ prod.name }}</option>
                  </select>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="createNewProduct(item)" title="Crear en Inventario" style="padding: 2px 8px;">+</button>
                </div>
              </td>
              <td v-else>{{ getProductName(item.product_id) }}</td>
              <td>
                <input type="text" v-model="item.serial_number" class="form-control form-control-sm" placeholder="Opcional" />
              </td>
              <td class="text-right">
                <input v-if="!item.product_id" type="number" v-model.number="item.unit_price" class="form-control form-control-sm text-right" style="width: 100px; display: inline-block;" />
                <span v-else>{{ formatNumber(item.unit_price) }}</span>
              </td>
              <td class="text-center">
                <input v-if="!item.product_id" type="number" v-model.number="item.quantity" class="form-control form-control-sm text-center" style="width: 80px; display: inline-block;" />
                <span v-else>{{ item.quantity }}</span>
              </td>
              <td class="text-right">
                <input v-if="!item.product_id" type="number" v-model.number="item.tax_rate" class="form-control form-control-sm text-right" style="width: 80px; display: inline-block;" />
                <span v-else>{{ item.tax_rate }}%</span>
              </td>
              <td class="text-right">{{ formatNumber((item.quantity * item.unit_price) * (1 + item.tax_rate/100)) }}</td>
              <td class="text-center">
                <button type="button" class="btn-icon text-danger" @click="removeItem(idx)" title="Eliminar">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Sección de Totales -->
      <div class="totals-section d-flex justify-content-end">
        <div class="totals-box p-4 card" style="min-width: 400px;">
          <div class="total-row">
            <span>Subtotal:</span>
            <span>{{ formatNumber(subtotal) }}</span>
          </div>
          <div class="total-row">
            <span>Impuesto (IVA):</span>
            <span>{{ formatNumber(taxAmount) }}</span>
          </div>
          <div class="total-row">
            <span>Descuento Global:</span>
            <input v-model.number="form.discount_amount" type="number" class="form-control form-control-sm text-right" style="width: 120px;" />
          </div>
          <hr />
          <div class="total-row grand-total text-success mb-3">
            <span>Total:</span>
            <span>{{ formatNumber(totalAmount) }}</span>
          </div>

          <div class="action-buttons mt-4 text-right">
            <button type="button" class="btn btn-secondary mr-2" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn btn-success btn-lg" :disabled="loading">
              {{ loading ? 'Procesando...' : (purchaseId ? 'Actualizar Compra' : 'Registrar Compra') }}
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'PurchaseFormView',
  props: {
    purchaseId: {
      type: Number,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const store = useStore()
    const router = useRouter()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const loading = ref(false)
    const isExtracting = ref(false)
    const selectedFile = ref(null)
    const fileInput = ref(null)
    const suppliers = ref([])
    const products = ref([])

    const form = ref({
      purchase_number: '',
      partner_id: '',
      purchase_date: new Date().toISOString().split('T')[0],
      due_date: '',
      payment_method: 'CASH',
      status: 'ISSUED',
      notes: '',
      discount_amount: 0,
      items: []
    })

    const newItem = ref({
      product_id: '',
      quantity: 1,
      unit_price: 0,
      tax_rate: 19,
      serial_number: ''
    })

    const fetchSuppliers = async () => {
      try {
        const res = await store.dispatch('partners/fetchPartners', {
          companyId: companyId.value,
          partnerType: 'SUPPLIER'
        })
        suppliers.value = res.data
      } catch (err) {
        console.error('Error fetching suppliers:', err)
      }
    }

    const fetchProducts = async () => {
      try {
        const res = await store.dispatch('inventory/fetchProducts', {
          companyId: companyId.value
        })
        products.value = res.data
      } catch (err) {
        console.error('Error fetching products:', err)
      }
    }

    const loadPurchaseData = async () => {
      if (!props.purchaseId) return
      loading.value = true
      try {
        const res = await store.dispatch('purchases/fetchPurchaseById', {
          purchaseId: props.purchaseId,
          companyId: companyId.value
        })
        const purchase = res.data
        form.value = {
          purchase_number: purchase.purchase_number,
          partner_id: purchase.partner_id,
          purchase_date: purchase.purchase_date.split('T')[0],
          due_date: purchase.due_date ? purchase.due_date.split('T')[0] : '',
          payment_method: purchase.payment_method,
          status: purchase.status,
          notes: purchase.notes || '',
          discount_amount: purchase.discount_amount || 0,
          items: purchase.items.map(item => ({
            product_id: item.product_id,
            description: item.description,
            quantity: item.quantity,
            unit_price: item.unit_price,
            tax_rate: item.tax_rate || 0,
            serial_number: item.serial_number || '',
            line_total: item.line_total
          }))
        }
      } catch (err) {
        console.error('Error loading purchase:', err)
        alert('Error al cargar los datos de la compra')
        emit('close')
      } finally {
        loading.value = false
      }
    }

    const onNewItemProductChange = () => {
      const product = products.value.find(p => p.id === newItem.value.product_id)
      if (product) {
        newItem.value.unit_price = product.purchase_price || 0
      }
    }

    const addItem = () => {
      if (!newItem.value.product_id) return
      const product = products.value.find(p => p.id === newItem.value.product_id)
      
      const subtotal = newItem.value.quantity * newItem.value.unit_price
      const tax = subtotal * (newItem.value.tax_rate / 100)
      
      form.value.items.push({
        product_id: newItem.value.product_id,
        description: product.name,
        quantity: newItem.value.quantity,
        unit_price: newItem.value.unit_price,
        tax_rate: newItem.value.tax_rate,
        serial_number: newItem.value.serial_number || '',
        line_total: subtotal + tax
      })

      newItem.value = {
        product_id: '',
        quantity: 1,
        unit_price: 0,
        tax_rate: 19,
        serial_number: ''
      }
    }

    const removeItem = (index) => {
      form.value.items.splice(index, 1)
    }

    const getProductName = (productId) => {
      const p = products.value.find(x => x.id === productId)
      return p ? p.name : 'Unknown'
    }

    const subtotal = computed(() => {
      return form.value.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
    })

    const taxAmount = computed(() => {
      return form.value.items.reduce((sum, item) => {
        const sub = item.quantity * item.unit_price
        return sum + (sub * (item.tax_rate / 100))
      }, 0)
    })

    const totalAmount = computed(() => {
      return subtotal.value + taxAmount.value - (form.value.discount_amount || 0)
    })

    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(value || 0)
    }

    const openPartnerForm = () => {
      // Guardar borrador para no perder datos al ir a crear el proveedor
      sessionStorage.setItem('purchaseDraft', JSON.stringify(form.value))
      router.push('/partners/new?redirect=/purchases')
    }

    const submitPurchase = async () => {
      if (!form.value.purchase_number || !form.value.partner_id || form.value.items.length === 0) {
        alert('Por favor complete los campos requeridos y agregue al menos un producto.')
        return
      }

      // Si hay ítems sin asignar, preguntar si continuar sin ellos
      const unmatched = form.value.items.filter(item => !item.product_id)
      if (unmatched.length > 0) {
        const names = unmatched.map(i => `• ${i.description || 'Sin nombre'}`).join('\n')
        const proceed = confirm(
          `Los siguientes ${unmatched.length} producto(s) del PDF no están asignados en el inventario:\n\n${names}\n\n¿Desea registrar la compra sin incluir estos productos? (Pulse Cancelar para asignarlos primero)`
        )
        if (!proceed) return

        // Filtrar solo los ítems asignados
        form.value.items = form.value.items.filter(item => item.product_id)

        if (form.value.items.length === 0) {
          alert('No hay productos asignados para registrar. Por favor asigne al menos un producto.')
          return
        }
      }

      loading.value = true
      try {
        const purchaseData = {
          purchase_number: form.value.purchase_number,
          partner_id: form.value.partner_id,
          purchase_date: form.value.purchase_date || null,
          due_date: form.value.due_date || null,
          payment_method: form.value.payment_method,
          status: form.value.status || 'ISSUED',
          notes: form.value.notes || null,
          discount_amount: form.value.discount_amount || 0,
          currency: 'COP',
          items: form.value.items.map(item => {
            const qty = parseFloat(item.quantity) || 0
            const unitPrice = parseFloat(item.unit_price) || 0
            const taxRate = parseFloat(item.tax_rate) || 0
            const subtotalItem = qty * unitPrice
            const taxAmount = subtotalItem * (taxRate / 100)
            const lineTotal = subtotalItem + taxAmount

            return {
              product_id: item.product_id || null,
              description: item.description || getProductName(item.product_id) || 'Sin descripción',
              quantity: qty,
              unit_price: unitPrice,
              tax_rate: taxRate,
              tax_amount: taxAmount,
              discount_percent: 0,
              discount_amount: 0,
              line_total: lineTotal,
              serial_number: item.serial_number || null
            }
          })
        }

        if (props.purchaseId) {
          await store.dispatch('purchases/updatePurchase', {
            purchaseId: props.purchaseId,
            purchaseData: purchaseData,
            companyId: companyId.value
          })
        } else {
          await store.dispatch('purchases/createPurchase', {
            purchaseData: purchaseData,
            companyId: companyId.value
          })
        }
        // Limpiar borrador al guardar
        sessionStorage.removeItem('purchaseDraft')
        emit('saved')
      } catch (err) {
        console.error('Error al registrar compra:', err.response?.data)
        alert(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Error al procesar la compra')
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await Promise.all([fetchSuppliers(), fetchProducts()])
      
      // Restaurar borrador si existe y no estamos editando
      const draft = sessionStorage.getItem('purchaseDraft')
      if (draft && !props.purchaseId) {
        try {
          form.value = JSON.parse(draft)

          // Re-intentar match de ítems no asignados con el inventario actualizado
          const normalizeString = (str) => {
            if (!str) return ''
            return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim()
          }

          form.value.items = form.value.items.map(item => {
            if (item.product_id) return item // ya asignado

            let matchedProductId = ''

            // 1. Match por código de barras / serial
            if (item.serial_number) {
              const byBarcode = products.value.find(p => p.barcode === item.serial_number.replace(/\s/g, ''))
              if (byBarcode) matchedProductId = byBarcode.id
            }

            // 2. Match por nombre exacto normalizado
            if (!matchedProductId && item.description) {
              const query = normalizeString(item.description)
              const byName = products.value.find(p => normalizeString(p.name) === query)
              if (byName) matchedProductId = byName.id
            }

            return { ...item, product_id: matchedProductId }
          })
        } catch (e) {
          console.error('Error restaurando borrador', e)
        }
        sessionStorage.removeItem('purchaseDraft')
      }

      // Detectar si acabamos de crear un proveedor y seleccionarlo
      const lastPartnerId = sessionStorage.getItem('lastCreatedPartnerId')
      if (lastPartnerId && !props.purchaseId) {
        form.value.partner_id = parseInt(lastPartnerId)
        sessionStorage.removeItem('lastCreatedPartnerId')
      }

      if (props.purchaseId) {
        await loadPurchaseData()
      }
    })

    const handleFileSelected = (event) => {
      selectedFile.value = event.target.files[0]
    }

    const uploadPdf = async () => {
      if (!selectedFile.value) return
      
      isExtracting.value = true
      const formData = new FormData()
      formData.append('file', selectedFile.value)

      try {
        const res = await store.dispatch('purchases/extractFromPdf', {
          formData,
          companyId: companyId.value
        })
        
        const data = res.data
        if (data.partner_exists) {
          form.value.partner_id = data.partner_data.id
          alert(`Proveedor ${data.partner_data.name} encontrado. Revisa los productos extraídos.`)
        } else {
          // Guardar datos en sessionStorage para el formulario de partner
          sessionStorage.setItem('draftPdfPartnerData', JSON.stringify(data.partner_data))
          alert('Proveedor no encontrado. Serás redirigido para crearlo.')
        }

        if (data.purchase_number) {
          form.value.purchase_number = data.purchase_number
        }

        const normalizeString = (str) => {
          if (!str) return ''
          return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim()
        }

        // Mapear items
        if (data.items && data.items.length > 0) {
          data.items.forEach(item => {
            let matchedProductId = ''
            
            // 1. Intentar hacer match exacto por número de serie (código de barras)
            if (item.serial_number) {
              const exactBarcodeMatch = products.value.find(p => p.barcode === item.serial_number.replace(/\s/g, ''))
              if (exactBarcodeMatch) {
                matchedProductId = exactBarcodeMatch.id
              }
            }

            // 2. Si no hay match por serie, intentar por nombre exacto
            if (!matchedProductId && item.description) {
              const query = normalizeString(item.description)
              const match = products.value.find(p => {
                const pName = normalizeString(p.name)
                // Usar coincidencia exacta para evitar falsos positivos
                return pName === query
              })
              if (match) {
                matchedProductId = match.id
              }
            }

            form.value.items.push({
              product_id: matchedProductId,
              description: item.description,
              quantity: item.quantity || 1,
              unit_price: item.unit_price || 0,
              tax_rate: item.tax_rate || 0,
              serial_number: item.serial_number || '',
              line_total: (item.quantity || 1) * (item.unit_price || 0) * (1 + (item.tax_rate || 0) / 100)
            })
          })
        }
        
        if (!data.partner_exists) {
          // Redirigir a crear proveedor con redirección de vuelta a compras
          // Guardamos el borrador de la compra para no perder los items
          sessionStorage.setItem('purchaseDraft', JSON.stringify(form.value))
          router.push('/partners/new?redirect=/purchases&fromPdf=true')
        }
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al procesar el PDF.')
      } finally {
        isExtracting.value = false
        if (fileInput.value) fileInput.value.value = ''
        selectedFile.value = null
      }
    }

    const createNewProduct = (item) => {
      // Guardar el borrador completo de la compra actual
      sessionStorage.setItem('purchaseDraft', JSON.stringify(form.value))
      
      // Guardar los datos del producto a crear
      const productDraft = {
        name: item.description || '',
        purchase_price: item.unit_price || 0,
        tax_rate: item.tax_rate || 19,
        serial_number: item.serial_number || '',
        supplier_id: form.value.partner_id || null,
        quantity: item.quantity || 1
      }
      sessionStorage.setItem('draftProductData', JSON.stringify(productDraft))
      
      // Redirigir a la creación de producto
      router.push('/inventory/new?redirect=/purchases&fromPdfItem=true')
    }

    return {
      loading,
      isExtracting,
      selectedFile,
      fileInput,
      handleFileSelected,
      uploadPdf,
      createNewProduct,
      suppliers,
      products,
      form,
      newItem,
      subtotal,
      taxAmount,
      totalAmount,
      addItem,
      removeItem,
      getProductName,
      onNewItemProductChange,
      formatNumber,
      submitPurchase,
      openPartnerForm
    }
  }
}
</script>

<style scoped>
.purchase-create-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.form-row {
  display: flex;
  align-items: center;
}

.form-row-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
}

.add-item-bar {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.flex-2 { flex: 2; }
.qty-group { flex: 1; }

.detail-table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table th {
  text-align: left;
  font-size: 0.85rem;
  color: #777;
  border-bottom: 2px solid #eee;
  padding: 10px;
}

.detail-table td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.text-right { text-align: right; }
.text-center { text-align: center; }

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.totals-box {
  background: #fff;
  border: 1px solid #eee;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.grand-total {
  font-size: 1.4rem;
  font-weight: 700;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-primary { background: #3498db; color: #fff; }
.btn-success { background: #2ecc71; color: #fff; }
.btn-secondary { background: #95a5a6; color: #fff; }
.btn-outline-primary { 
  background: transparent; 
  border: 1px solid #3498db; 
  color: #3498db; 
}

.btn-lg {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
}

.ml-3 { margin-left: 1rem; }
.mr-2 { margin-right: 0.5rem; }
.mb-4 { margin-bottom: 1.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.p-4 { padding: 1.5rem; }
.d-flex { display: flex; }
.justify-content-end { justify-content: flex-end; }

/* Selects de ítems no asignados desde PDF */
.unmatched-select {
  border-color: #e67e22 !important;
  background-color: #fff8f0 !important;
  color: #c0392b;
  font-weight: 500;
}
.unmatched-select:focus {
  box-shadow: 0 0 0 2px rgba(230, 126, 34, 0.4) !important;
}
</style>
