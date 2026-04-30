<template>
  <div class="modal-overlay" v-if="show" @click.self="close" style="z-index: 400;">
    <div class="modal modal-lg">
      <div class="modal-header">
        <h3 class="m-0">Armar Equipo</h3>
        <button type="button" class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="alert alert-info mb-3">
          <i class="fas fa-info-circle mr-2"></i>
          Selecciona las partes del inventario. El sistema sumará el precio de costo. Al final, agrega tu ganancia. Las partes se imprimirán en la factura pero sus precios individuales se ocultarán.
        </div>

        <div class="form-group mb-4">
          <label class="font-weight-bold">Nombre del Equipo Armado (para la factura):</label>
          <input type="text" v-model="assemblyName" class="form-control form-control-lg" placeholder="Ej. PC Gamer Core i7, Equipo Servidor Base..." required />
        </div>

        <div class="card bg-light p-3 mb-4 border-0">
          <h5 class="mb-3">Agregar Partes</h5>
          <div class="add-item-bar align-items-end">
            <div class="form-group flex-grow-1 mb-0 mr-2">
              <label>Producto / Componente:</label>
              <select v-model="newPartId" class="form-control">
                <option value="">Buscar y seleccionar producto...</option>
                <option v-for="prod in availableProducts" :key="prod.id" :value="prod.id">
                  {{ prod.name }} - Costo: {{ formatCOP(prod.purchase_price || 0) }} (Stock: {{ prod.stock_level }})
                </option>
              </select>
            </div>
            <div class="form-group mb-0 mr-2" style="width: 100px;">
              <label>Cantidad:</label>
              <input type="number" v-model.number="newPartQty" min="1" class="form-control" />
            </div>
            <button type="button" class="btn btn-primary" @click="addPart" :disabled="!newPartId">
              <i class="fas fa-plus"></i> Añadir
            </button>
          </div>
        </div>

        <table class="data-table mb-4" v-if="parts.length > 0">
          <thead>
            <tr>
              <th>Componente</th>
              <th class="text-center">Cant.</th>
              <th class="text-right">Costo Unit.</th>
              <th class="text-right">Costo Total</th>
              <th class="text-center">Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(part, idx) in parts" :key="idx">
              <td>{{ part.product.name }}</td>
              <td class="text-center">{{ part.quantity }}</td>
              <td class="text-right">{{ formatCOP(part.cost) }}</td>
              <td class="text-right">{{ formatCOP(part.cost * part.quantity) }}</td>
              <td class="text-center">
                <button type="button" class="btn-icon text-danger" @click="removePart(idx)">🗑️</button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-light font-weight-bold">
              <td colspan="3" class="text-right">Costo Total del Equipo:</td>
              <td class="text-right">{{ formatCOP(totalCost) }}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>

        <div v-else class="text-center text-muted p-4 mb-4 border rounded">
          No hay partes seleccionadas. Añade componentes para armar el equipo.
        </div>

        <div class="card p-3 border-primary" v-if="parts.length > 0">
          <h5 class="mb-3 text-primary">Ganancia y Precio Final</h5>
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label>Ganancia Total ($):</label>
                <div class="input-group">
                  <div class="input-group-prepend">
                    <span class="input-group-text">$</span>
                  </div>
                  <input type="number" v-model.number="profit" class="form-control form-control-lg font-weight-bold text-success" placeholder="0" min="0" />
                </div>
              </div>
            </div>
            <div class="col-md-6 d-flex flex-column justify-content-center align-items-end">
              <div class="text-muted mb-1">Precio de Venta Sugerido:</div>
              <div class="h2 mb-0 text-primary">{{ formatCOP(finalPrice) }}</div>
            </div>
          </div>
        </div>

      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="close">Cancelar</button>
        <button type="button" class="btn btn-success btn-lg" @click="confirm" :disabled="parts.length === 0 || !assemblyName.trim()">
          <i class="fas fa-check mr-2"></i> Confirmar y Añadir a Factura
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { formatCOP } from '@/utils/formatters'

export default {
  name: 'EquipoAssemblyModal',
  props: {
    show: { type: Boolean, required: true },
    products: { type: Array, required: true }
  },
  data() {
    return {
      assemblyName: '',
      newPartId: '',
      newPartQty: 1,
      parts: [],
      profit: 0
    }
  },
  computed: {
    availableProducts() {
      // Excluir servicios o productos genéricos si es necesario, por ahora retornamos todos
      return this.products;
    },
    totalCost() {
      return this.parts.reduce((sum, part) => sum + (part.cost * part.quantity), 0);
    },
    finalPrice() {
      return this.totalCost + (Number(this.profit) || 0);
    }
  },
  methods: {
    formatCOP,
    close() {
      this.$emit('close')
      this.reset()
    },
    reset() {
      this.assemblyName = ''
      this.newPartId = ''
      this.newPartQty = 1
      this.parts = []
      this.profit = 0
    },
    addPart() {
      if (!this.newPartId) return;
      const product = this.products.find(p => p.id === this.newPartId);
      if (!product) return;
      
      // Check if already in parts
      const existing = this.parts.find(p => p.product.id === product.id);
      if (existing) {
        existing.quantity += this.newPartQty;
      } else {
        this.parts.push({
          product: product,
          quantity: this.newPartQty,
          cost: Number(product.purchase_price) || 0
        });
      }
      
      this.newPartId = '';
      this.newPartQty = 1;
    },
    removePart(idx) {
      this.parts.splice(idx, 1);
    },
    confirm() {
      if (this.parts.length === 0 || !this.assemblyName.trim()) return;
      
      // Generar un ID único para agrupar estas partes en la factura
      const groupId = 'assembly_' + Date.now().toString() + '_' + Math.random().toString(36).substr(2, 5);
      
      const totalCost = this.totalCost;
      const totalProfit = Number(this.profit) || 0;
      
      const itemsToAddToInvoice = [];
      
      // Calcular la ganancia proporcional para cada parte y agregarla a la lista de items
      this.parts.forEach((part, index) => {
        const lineCost = part.cost * part.quantity;
        
        // Proporción de este componente sobre el costo total
        let proportion = 0;
        if (totalCost > 0) {
          proportion = lineCost / totalCost;
        } else {
          // Si el costo total es 0 (ej. todos los items tienen costo 0), dividir la ganancia equitativamente
          proportion = 1 / this.parts.length;
        }
        
        const lineProfit = totalProfit * proportion;
        // Precio unitario = Costo + Ganancia proporcional (dividido por cantidad para tener el unitario)
        const unitPrice = part.quantity > 0 ? (lineCost + lineProfit) / part.quantity : 0;
        
        // En la factura, el primer componente del grupo puede llevar el nombre del equipo como description
        // O mejor, todos llevan su description normal, y el frontend al imprimir agrupa.
        // Pero para que en la vista "Detalles" el usuario sepa que pertenece a un grupo, podemos prefijar.
        
        let description = `[${this.assemblyName}] ${part.product.name}`;
        
        itemsToAddToInvoice.push({
          product_id: part.product.id,
          description: description,
          quantity: part.quantity,
          unit_price: unitPrice,
          discount: 0,
          apply_tax: true, // Asumimos que los equipos ensamblados llevan IVA
          assembly_group_id: groupId,
          assembly_name: this.assemblyName, // Custom frontend field for grouping logic
          original_product_name: part.product.name
        });
      });
      
      this.$emit('confirm', itemsToAddToInvoice);
      this.close();
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow-y: auto;
  padding: 2rem 0;
  z-index: 1050;
}

.modal {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 95%;
  max-width: 900px;
  padding: 2rem;
  position: relative;
  margin: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #f0f2f5;
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  color: #2c3e50;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  line-height: 1;
  color: #6c757d;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #dc3545;
}

.add-item-bar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #f0f2f5;
}
</style>
