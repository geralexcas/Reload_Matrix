<template>
  <div class="modal-overlay">
    <div class="pos-modal">
      <div class="modal-header">
        <h3>💰 Cobro y Facturación</h3>
        <button class="close-btn" @click="$emit('cancel')">&times;</button>
      </div>
      
      <div class="pos-body">
        <div class="pos-totals">
          <div class="pos-total-row big-total">
            <span>Total a Pagar</span>
            <span class="amount">${{ formatCOP(totalAmount) }}</span>
          </div>
        </div>

        <form @submit.prevent="confirmPayment" class="pos-form">
          <div class="form-group">
            <label>Forma de Pago</label>
            <div class="payment-methods">
              <button 
                type="button" 
                :class="['pm-btn', form.payment_method === 'CASH' ? 'active' : '']"
                @click="setPaymentMethod('CASH')"
              >
                💵 Efectivo
              </button>
              <button 
                type="button" 
                :class="['pm-btn', form.payment_method === 'BANK_TRANSFER' ? 'active' : '']"
                @click="setPaymentMethod('BANK_TRANSFER')"
              >
                🏦 Transferencia
              </button>
              <button 
                type="button" 
                :class="['pm-btn', form.payment_method === 'CREDIT_CARD' ? 'active' : '']"
                @click="setPaymentMethod('CREDIT_CARD')"
              >
                💳 Tarjeta
              </button>
              <button 
                type="button" 
                :class="['pm-btn', form.payment_method === 'CREDIT' ? 'active' : '']"
                @click="setPaymentMethod('CREDIT')"
              >
                ⏳ Crédito / Borrador
              </button>
            </div>
          </div>

          <!-- <div class="form-group" v-if="cashAccounts.length > 1 || bankAccounts.length > 1"> -->
          <!-- Oculto para automatismo: se autoselecciona la primera cuenta según el método de pago -->
          <div v-show="false" class="pos-details-container">
            <div class="form-group">
              <label>Cuenta de Destino</label>
              <select v-model="selectedAccountStr">
                <option value="">Seleccionar cuenta destino...</option>
                <optgroup label="Cajas (Efectivo)">
                  <option v-for="c in cashAccounts" :key="'cash_'+c.id" :value="'CASH:'+c.id">
                    {{ c.name }}
                  </option>
                </optgroup>
                <optgroup label="Cuentas Bancarias (Transferencias/Tarjetas)">
                  <option v-for="b in bankAccounts" :key="'bank_'+b.id" :value="'BANK:'+b.id">
                    {{ b.bank_name }} - {{ b.account_number }}
                  </option>
                </optgroup>
              </select>
            </div>
          </div>

          <div v-show="form.payment_method !== 'CREDIT'" class="pos-details-container">
            <!-- Efectivo specific fields -->
            <div v-if="form.payment_method === 'CASH'" class="cash-calc-grid">
              <div class="form-group">
                <label>Efectivo Recibido</label>
                <input 
                  type="number" 
                  step="0.01"
                  v-model.number="amountReceived" 
                  @input="calculateChange"
                  class="big-input text-success" 
                  min="0"
                  required
                />
              </div>
              <div class="form-group">
                <label>Cambio a Devolver</label>
                <input 
                  type="text" 
                  :value="formatCOP(changeAmount)" 
                  class="big-input text-danger" 
                  readonly 
                />
              </div>
            </div>

            <!-- Transfer/Card specific fields -->
            <div v-if="['BANK_TRANSFER', 'CREDIT_CARD', 'CHECK'].includes(form.payment_method)" class="form-group">
              <label>Número de Referencia / Comprobante</label>
              <input v-model="form.reference" type="text" placeholder="# de transacción o comprobante" />
            </div>

            <div class="form-group" v-if="form.payment_method !== 'CASH'">
              <label>Monto a Pagar</label>
              <input type="number" v-model.number="form.amount" :max="totalAmount" :min="0" step="0.01" required />
            </div>
          </div>

          <!-- Alert if incomplete payment -->
          <div v-if="form.payment_method !== 'CREDIT' && isPartialPayment" class="alert-warning">
            ⚠️ El monto ingresado (${{ formatCOP(effectiveAmount) }}) es menor al total. La factura quedará en estado de pago parcial.
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('cancel')">Cancelar</button>
            <button type="submit" class="btn btn-success" :disabled="!isValid">
              Facturar y Registrar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { formatCOP } from '@/utils/formatters'

export default {
  name: 'POSPaymentModal',
  props: {
    totalAmount: {
      type: Number,
      required: true
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const store = useStore()

    const form = ref({
      payment_method: 'CASH',
      amount: props.totalAmount,
      reference: ''
    })

    const selectedAccountStr = ref('')
    const amountReceived = ref(props.totalAmount)
    const changeAmount = ref(0)

    const cashAccounts = computed(() => store.getters['treasury/getCashAccounts'] || [])
    const bankAccounts = computed(() => store.getters['treasury/getBankAccounts'] || [])
    const companyId = computed(() => store.getters['company/selectedCompanyId'] || 1)

    const setPaymentMethod = (method) => {
      form.value.payment_method = method
      form.value.amount = props.totalAmount
      form.value.reference = ''
      amountReceived.value = props.totalAmount
      calculateChange()
      
      // Auto-select based on method
      if (method === 'CASH' && cashAccounts.value.length > 0) {
        selectedAccountStr.value = 'CASH:' + cashAccounts.value[0].id
      } else if (['BANK_TRANSFER', 'CREDIT_CARD'].includes(method) && bankAccounts.value.length > 0) {
        selectedAccountStr.value = 'BANK:' + bankAccounts.value[0].id
      } else {
        selectedAccountStr.value = ''
      }
    }

    const calculateChange = () => {
      if (form.value.payment_method === 'CASH') {
         form.value.amount = amountReceived.value >= props.totalAmount ? props.totalAmount : amountReceived.value || 0;
         changeAmount.value = (amountReceived.value || 0) > props.totalAmount ? (amountReceived.value - props.totalAmount) : 0;
      } else {
         changeAmount.value = 0;
      }
    }

    const effectiveAmount = computed(() => {
        return form.value.payment_method === 'CASH' ? form.value.amount : (form.value.amount || 0)
    })

    const isPartialPayment = computed(() => {
        return effectiveAmount.value < props.totalAmount
    })

    const isValid = computed(() => {
      if (form.value.payment_method === 'CREDIT') return true;
      if (!selectedAccountStr.value) return false;
      if (effectiveAmount.value <= 0) return false;
      return true;
    })

    onMounted(async () => {
      try {
        await store.dispatch('treasury/fetchCashAccounts', { skip: 0, limit: 10 })
        await store.dispatch('treasury/fetchBankAccounts', { skip: 0, limit: 10 })
      } catch (err) {
        console.error("Error loading account data for POS", err)
      }
      setPaymentMethod('CASH') // set defaults based on loaded accounts
    })

    const confirmPayment = () => {
      let is_paid = false;
      let payment_account_type = null;
      let payment_account_id = null;
      
      if (form.value.payment_method !== 'CREDIT') {
        is_paid = true;
        const [accType, accId] = selectedAccountStr.value.split(':');
        // El Backend espera ACCOUNT_TYPE (CASH o BANK)
        payment_account_type = accType;
        payment_account_id = parseInt(accId);
      }

      emit('confirm', {
         is_paid: is_paid,
         payment_method: form.value.payment_method,
         amount_paid: effectiveAmount.value,
         payment_account_type,
         payment_account_id,
         reference: form.value.reference
      })
    }

    return {
      form,
      amountReceived,
      changeAmount,
      selectedAccountStr,
      cashAccounts,
      bankAccounts,
      setPaymentMethod,
      calculateChange,
      formatCOP,
      isPartialPayment,
      effectiveAmount,
      isValid,
      confirmPayment
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.pos-modal {
  background: #fff;
  border-radius: 12px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden;
}

.modal-header {
  background: #f8f9fa;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
}

.pos-body {
  padding: 20px;
}

.pos-totals {
  background: #2c3e50;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.pos-total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pos-total-row.big-total {
  font-size: 1.2rem;
  font-weight: 600;
}

.pos-total-row .amount {
  color: #2ecc71;
  font-size: 1.8rem;
}

.payment-methods {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.pm-btn {
  padding: 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
  color: #555;
}

.pm-btn:hover {
  background: #f8f9fa;
  border-color: #bdc3c7;
}

.pm-btn.active {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #1565c0;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.pos-details-container {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #ddd;
}

.cash-calc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.9rem;
  color: #7f8c8d;
  font-weight: 500;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
}

.big-input {
  font-size: 1.25rem !important;
  font-weight: bold;
}

.text-success { color: #27ae60; }
.text-danger { color: #e74c3c; }

.alert-warning {
  background: #fff3cd;
  color: #856404;
  padding: 12px;
  border-radius: 6px;
  margin-top: 16px;
  font-size: 0.9rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.btn-secondary { background: #95a5a6; color: white; }
.btn-success { background: #27ae60; color: white; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
