<template>
  <div class="accounting-container">
    <div class="accounting-header">
      <h2>Contabilidad</h2>
      <div class="header-actions">
        <router-link to="/accounting/chart-of-accounts" class="btn btn-primary">
          <i class="fas fa-list"></i> Plan de Cuentas
        </router-link>
        <router-link to="/accounting/journal-entries" class="btn btn-secondary">
          <i class="fas fa-book"></i> Asientos Contables
        </router-link>
      </div>
    </div>
    
    <div class="accounting-overview">
      <div class="overview-card">
        <h3>Plan de Cuentas</h3>
        <p>Cuentas contables organizadas por categoría</p>
        <router-link to="/accounting/chart-of-accounts" class="btn btn-sm btn-outline">
          Ver Detalle
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>Asientos Contables</h3>
        <p>Registro de transacciones financieras</p>
        <router-link to="/accounting/journal-entries" class="btn btn-sm btn-outline">
          Ver Detalle
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>Libro Mayor</h3>
        <p>Saldos y movimientos por cuenta contable</p>
        <router-link to="/accounting/libro-mayor" class="btn btn-sm btn-outline">
          Ver Detalle
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>Libro de Ventas</h3>
        <p>Registro de facturas de venta con IVA</p>
        <router-link to="/accounting/libro-ventas" class="btn btn-sm btn-outline">
          Ver Detalle
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>Libro de Compras</h3>
        <p>Registro de facturas de compra con IVA soportado</p>
        <router-link to="/accounting/libro-compras" class="btn btn-sm btn-outline">
          Ver Detalle
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>{{ $t('nav.estadoResultados') }}</h3>
        <p>Resumen de ingresos y gastos</p>
        <router-link to="/accounting/estado-resultados" class="btn btn-sm btn-outline">
          {{ $t('common.viewDetail') }}
        </router-link>
      </div>
      
      <div class="overview-card">
        <h3>{{ $t('nav.balanceGeneral') }}</h3>
        <p>Situación financiera de la empresa</p>
        <router-link to="/accounting/balance-general" class="btn btn-sm btn-outline">
          {{ $t('common.viewDetail') }}
        </router-link>
      </div>
    </div>
    
    <div class="recent-activity">
      <h3>Actividad Reciente</h3>
      <div class="activity-list">
        <div class="activity-item">
          <div class="activity-icon">
            <i class="fas fa-plus-circle text-success"></i>
          </div>
          <div class="activity-content">
            <h4>Nuevo asiento contable creado</h4>
            <p>Asiento #20260001 - Compra de inventario</p>
            <time datetime="2026-03-31T10:30:00">Hoy, 10:30 AM</time>
          </div>
        </div>
        <div class="activity-item">
          <div class="activity-icon">
            <i class="fas fa-edit text-warning"></i>
          </div>
          <div class="activity-content">
            <h4>Asiento contable modificado</h4>
            <p>Asiento #20260000 - Ajuste de inventario</p>
            <time datetime="2026-03-30T15:45:00">Ayer, 3:45 PM</time>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AccountingIndexView'
}
</script>

<style scoped>
.accounting-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.accounting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.accounting-header h2 {
  color: #2c3e50;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-outline {
  background-color: transparent;
  color: #007bff;
  border: 2px solid #007bff;
}

.btn-outline:hover {
  background-color: #007bff;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.accounting-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  text-align: center;
}

.overview-card h3 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 1.1rem;
}

.overview-card p {
  margin: 0 0 15px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.recent-activity {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 25px;
}

.recent-activity h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.activity-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.activity-icon i {
  font-size: 1.25rem;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 5px 0;
  font-size: 1rem;
  color: #495057;
}

.activity-content p {
  margin: 0 0 8px 0;
  color: #6c757d;
  font-size: 0.85rem;
}

.activity-content time {
  display: block;
  color: #999;
  font-size: 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
  .accounting-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .accounting-overview {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
</style>