<template>
  <div class="modal-overlay">
    <div class="modal-content modal-lg">
      <div class="modal-header">
        <h2>Detalle de Compra - {{ purchase?.purchase_number }}</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Fecha:</span>
            <span class="detail-value">{{ formatDate(purchase?.purchase_date) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Proveedor:</span>
            <span class="detail-value">{{ purchase?.partner?.name || 'N/A' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Método de Pago:</span>
            <span class="detail-value">{{ purchase?.payment_method }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Estado:</span>
            <span :class="['badge', getStatusClass(purchase?.status)]">
              {{ purchase?.status }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fecha Vencimiento:</span>
            <span class="detail-value">{{ formatDate(purchase?.due_date) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Notas:</span>
            <span class="detail-value">{{ purchase?.notes || 'N/A' }}</span>
          </div>
        </div>

        <div class="items-section">
          <h3>Items de la Compra</h3>
          <table class="items-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio Unit.</th>
                <th>Desc %</th>
                <th>IVA %</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in purchase?.items" :key="index">
                <td>{{ item.description || item.product?.name || 'N/A' }}</td>
                <td>{{ item.quantity }}</td>
                <td>${{ formatNumber(item.unit_price) }}</td>
                <td>{{ item.discount_percent }}%</td>
                <td>{{ item.tax_rate }}%</td>
                <td class="text-right">${{ formatNumber(item.line_total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="totals-section">
          <div class="total-row">
            <span>Subtotal:</span>
            <span>${{ formatNumber(purchase?.subtotal) }}</span>
          </div>
          <div class="total-row">
            <span>IVA:</span>
            <span>${{ formatNumber(purchase?.tax_amount) }}</span>
          </div>
          <div class="total-row">
            <span>Descuento:</span>
            <span>-${{ formatNumber(purchase?.discount_amount) }}</span>
          </div>
          <div class="total-row total-final">
            <span>Total:</span>
            <span>${{ formatNumber(purchase?.total_amount) }}</span>
          </div>
        </div>

        <div v-if="purchase?.payments?.length > 0" class="payments-section">
          <h3>Pagos Registrados</h3>
          <table class="payments-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Método</th>
                <th>Referencia</th>
                <th>Monto</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(payment, index) in purchase?.payments" :key="index">
                <td>{{ formatDate(payment.payment_date) }}</td>
                <td>{{ payment.payment_method }}</td>
                <td>{{ payment.reference || 'N/A' }}</td>
                <td class="text-right">${{ formatNumber(payment.amount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3" class="text-right"><strong>Total Pagado:</strong></td>
                <td class="text-right"><strong>${{ formatNumber(paidAmount) }}</strong></td>
              </tr>
              <tr>
                <td colspan="3" class="text-right"><strong>Saldo Pendiente:</strong></td>
                <td class="text-right"><strong class="text-danger">${{ formatNumber(pendingAmount) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'PurchaseDetailModal',
  props: {
    purchase: Object
  },
  emits: ['close'],
  setup(props) {
    const paidAmount = computed(() => {
      return props.purchase?.payments?.reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0
    })

    const pendingAmount = computed(() => {
      return (props.purchase?.total_amount || 0) - paidAmount.value
    })

    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-CO').format(value || 0)
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('es-CO')
    }

    const getStatusClass = (status) => {
      const classes = {
        'DRAFT': 'badge-secondary',
        'ISSUED': 'badge-primary',
        'PAID': 'badge-success',
        'PARTIAL': 'badge-warning',
        'OVERDUE': 'badge-danger',
        'CANCELLED': 'badge-dark'
      }
      return classes[status] || 'badge-secondary'
    }

    return {
      paidAmount,
      pendingAmount,
      formatNumber,
      formatDate,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
}

.modal-lg {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #7f8c8d;
}

.detail-value {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  width: fit-content;
}

.badge-primary { background: #3498db; color: white; }
.badge-success { background: #27ae60; color: white; }
.badge-warning { background: #f39c12; color: white; }
.badge-danger { background: #e74c3c; color: white; }
.badge-secondary { background: #95a5a6; color: white; }
.badge-dark { background: #34495e; color: white; }

.items-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.items-section h3,
.payments-section h3 {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 12px;
}

.items-table,
.payments-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
}

.items-table th,
.items-table td,
.payments-table th,
.payments-table td {
  padding: 10px;
  border: 1px solid #ecf0f1;
  font-size: 13px;
}

.items-table th,
.payments-table th {
  background: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
}

.text-right {
  text-align: right;
}

.text-danger {
  color: #e74c3c;
}

.totals-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  color: #2c3e50;
}

.total-final {
  font-size: 18px;
  font-weight: 600;
  border-top: 2px solid #ecf0f1;
  padding-top: 12px;
  margin-top: 8px;
}

.payments-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.payments-table tfoot {
  background: #f8f9fa;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}
</style>