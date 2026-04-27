<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Registrar Pago - {{ purchase?.purchase_number }}</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="submitPayment" class="modal-body">
        <div class="payment-info">
          <div class="info-row">
            <span class="info-label">Total:</span>
            <span class="info-value">${{ formatNumber(purchase?.total_amount || 0) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Pagado:</span>
            <span class="info-value">${{ formatNumber(paidAmount) }}</span>
          </div>
          <div class="info-row highlight">
            <span class="info-label">Saldo Pendiente:</span>
            <span class="info-value">${{ formatNumber(pendingAmount) }}</span>
          </div>
        </div>

        <div class="form-group">
          <label>Método de Pago *</label>
          <select v-model="form.payment_method" required>
            <option value="CASH">Efectivo</option>
            <option value="BANK_TRANSFER">Transferencia Bancaria</option>
            <option value="CHECK">Cheque</option>
            <option value="CREDIT_CARD">Tarjeta de Crédito</option>
          </select>
        </div>

        <div class="form-group">
          <label>Monto *</label>
          <input 
            v-model.number="form.amount" 
            type="number" 
            step="0.01" 
            min="0"
            placeholder="Ingrese el monto"
          />
        </div>

        <div class="form-group">
          <label>Fecha de Pago</label>
          <input v-model="form.payment_date" type="date" />
        </div>

        <div class="form-group">
          <label>Referencia</label>
          <input v-model="form.reference" type="text" placeholder="Número de transacción, cheque, etc." />
        </div>

        <div class="form-group">
          <label>Notas</label>
          <textarea v-model="form.notes" rows="2"></textarea>
        </div>

        <div class="quick-amounts">
          <button 
            type="button" 
            class="quick-amount-btn" 
            @click="form.amount = purchase?.total_amount || 0"
          >
            Pago Total
          </button>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : 'Registrar Pago' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'PaymentModal',
  props: {
    purchase: Object
  },
  emits: ['close', 'paid'],
  setup(props, { emit }) {
    const store = useStore()
    const companyId = computed(() => store.getters['company/selectedCompanyId'])

    const loading = ref(false)

    const form = ref({
      payment_method: 'BANK_TRANSFER',
      amount: 0,
      payment_date: new Date().toISOString().split('T')[0],
      reference: '',
      notes: ''
    })

    const paidAmount = computed(() => {
      return props.purchase?.payments?.reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0
    })

    const pendingAmount = computed(() => {
      return (props.purchase?.total_amount || 0) - paidAmount.value
    })

    onMounted(() => {
      if (form.value.amount === 0) {
        form.value.amount = pendingAmount.value
      }
    })

    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-CO').format(value || 0)
    }

    const submitPayment = async () => {
      const amount = Number(form.value.amount) || 0
      const pending = Number(pendingAmount.value) || 0
      
      if (amount <= 0) {
        alert('Por favor ingrese un monto mayor a 0')
        return
      }
      
      // Se añade un epsilon (0.01) para problemas de precisión de punto flotante
      if (amount > pending + 0.01) {
        alert('El monto no puede exceder el saldo pendiente')
        return
      }

      loading.value = true
      try {
        await store.dispatch('purchases/registerPayment', {
          purchaseId: props.purchase.id,
          paymentData: form.value,
          companyId: companyId.value
        })
        emit('paid')
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al registrar el pago')
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      form,
      paidAmount,
      pendingAmount,
      formatNumber,
      submitPayment
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
  max-width: 500px;
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
  font-size: 18px;
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

.payment-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.info-label {
  color: #7f8c8d;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  color: #2c3e50;
}

.info-row.highlight {
  border-top: 1px solid #ddd;
  margin-top: 8px;
  padding-top: 12px;
}

.info-row.highlight .info-value {
  font-size: 18px;
  color: #e74c3c;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.quick-amounts {
  margin-bottom: 16px;
}

.quick-amount-btn {
  background: #ecf0f1;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: #2c3e50;
}

.quick-amount-btn:hover {
  background: #dfe6e9;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}
</style>