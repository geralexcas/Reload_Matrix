<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <h1 v-if="!isCollapsed">Reload Matrix</h1>
      <h1 v-else>RM</h1>
      <button class="collapse-btn" @click="$emit('toggle')">
        {{ isCollapsed ? '☰' : '✕' }}
      </button>
    </div>
    <TrialProgressBar v-if="company" :company="company" />
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <span class="nav-icon">📊</span>
        <span v-if="!isCollapsed">Dashboard</span>
      </router-link>
      <template v-if="hasCompany">
        <router-link to="/companies" class="nav-item" active-class="active">
          <span class="nav-icon">🏢</span>
          <span v-if="!isCollapsed">Empresa</span>
        </router-link>
        <router-link to="/partners" class="nav-item" active-class="active">
          <span class="nav-icon">👥</span>
          <span v-if="!isCollapsed">Socios</span>
        </router-link>
      </template>
      <router-link v-if="hasCompany" to="/inventory" class="nav-item" active-class="active">
        <span class="nav-icon">📦</span>
        <span v-if="!isCollapsed">Inventario</span>
      </router-link>
      <router-link v-if="hasCompany" to="/invoicing" class="nav-item" active-class="active">
        <span class="nav-icon">📄</span>
        <span v-if="!isCollapsed">Facturación</span>
      </router-link>
      <div v-if="hasCompany" class="nav-group">
        <div class="nav-item has-submenu" @click="toggleMenu('accounting')" :class="{ 'submenu-open': expandedMenus.accounting }">
          <span class="nav-icon">📒</span>
          <span v-if="!isCollapsed">Contabilidad</span>
          <span v-if="!isCollapsed" class="submenu-arrow">▶</span>
        </div>
        <transition name="slide">
          <div v-show="expandedMenus.accounting && !isCollapsed" class="submenu-items">
            <router-link to="/accounting" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📊</span>
              <span>Resumen</span>
            </router-link>
            <router-link to="/accounting/libro-mayor" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📖</span>
              <span>Libro Mayor</span>
            </router-link>
            <router-link to="/accounting/libro-ventas" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📈</span>
              <span>Libro Ventas</span>
            </router-link>
            <router-link to="/accounting/libro-compras" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📉</span>
              <span>Libro Compras</span>
            </router-link>
            <div class="nav-section-divider">
              <span>Reportes Tributarios</span>
            </div>
            <router-link to="/accounting/declaracion-iva" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">🏛️</span>
              <span>Declaración IVA</span>
            </router-link>
            <router-link to="/accounting/reporte-retenciones" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📋</span>
              <span>Retenciones</span>
            </router-link>
            <router-link to="/accounting/reporte-ingresos" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">💹</span>
              <span>Ingresos</span>
            </router-link>
            <router-link to="/accounting/reporte-egresos" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">💸</span>
              <span>Egresos</span>
            </router-link>
            <router-link to="/accounting/reporte-patrimonio" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">⚖️</span>
              <span>Patrimonio</span>
            </router-link>
          </div>
        </transition>
      </div>

      <router-link v-if="hasCompany" to="/repair" class="nav-item" active-class="active">
        <span class="nav-icon">🔧</span>
        <span v-if="!isCollapsed">Reparación</span>
      </router-link>
      <router-link v-if="hasCompany" to="/wallet" class="nav-item" active-class="active">
        <span class="nav-icon">💰</span>
        <span v-if="!isCollapsed">Monedero</span>
      </router-link>
      <router-link v-if="hasCompany" to="/purchases" class="nav-item" active-class="active">
        <span class="nav-icon">🛒</span>
        <span v-if="!isCollapsed">Compras</span>
      </router-link>
      <router-link v-if="hasCompany" to="/purchases/accounts-payable" class="nav-item" active-class="active">
        <span class="nav-icon">📋</span>
        <span v-if="!isCollapsed">Cuentas por Pagar</span>
      </router-link>

      <div v-if="hasCompany && isSuperuser" class="nav-group">
        <div class="nav-item has-submenu" @click="toggleMenu('treasury')" :class="{ 'submenu-open': expandedMenus.treasury }">
          <span class="nav-icon">🏦</span>
          <span v-if="!isCollapsed">Tesorería</span>
          <span v-if="!isCollapsed" class="submenu-arrow">▶</span>
        </div>
        <transition name="slide">
          <div v-show="expandedMenus.treasury && !isCollapsed" class="submenu-items">
            <router-link to="/treasury" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📊</span>
              <span>Resumen</span>
            </router-link>
            <router-link to="/treasury/bank-accounts" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">🏛️</span>
              <span>Cuentas Bancarias</span>
            </router-link>
            <router-link to="/treasury/cash-accounts" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">💵</span>
              <span>Cuentas de Caja</span>
            </router-link>
            <router-link to="/treasury/transactions" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📋</span>
              <span>Transacciones</span>
            </router-link>
            <router-link to="/treasury/transfers" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">🔄</span>
              <span>Transferencias</span>
            </router-link>
            <router-link to="/treasury/checks" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📝</span>
              <span>Cheques</span>
            </router-link>
            <router-link to="/treasury/cash-flow" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">📊</span>
              <span>Flujo de Caja</span>
            </router-link>
            <router-link to="/treasury/reconciliations" class="nav-item nav-sub" active-class="active">
              <span class="nav-icon">✅</span>
              <span>Conciliación Bancaria</span>
            </router-link>
          </div>
        </transition>
      </div>
      <template v-if="hasCompany && isSuperuser">
        <div v-if="!isCollapsed" class="nav-section-divider">
          <span>Administración</span>
        </div>
        <router-link to="/admin/backups" class="nav-item" active-class="active">
          <span class="nav-icon">💾</span>
          <span v-if="!isCollapsed">Respaldos</span>
        </router-link>
        <router-link to="/admin/users" class="nav-item" active-class="active">
          <span class="nav-icon">👤</span>
          <span v-if="!isCollapsed">Usuarios</span>
        </router-link>
      </template>
      <template v-if="isPlatformAdmin">
        <div v-if="!isCollapsed" class="nav-section-divider platform-section">
          <span>Plataforma</span>
        </div>
        <router-link to="/platform/tenants" class="nav-item" active-class="active">
          <span class="nav-icon">🏢</span>
          <span v-if="!isCollapsed">Empresas</span>
        </router-link>
        <router-link to="/platform/tenants/create" class="nav-item" active-class="active">
          <span class="nav-icon">➕</span>
          <span v-if="!isCollapsed">Crear Empresa</span>
        </router-link>
      </template>
    </nav>
  </aside>
</template>

<script>
import { computed, ref, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import TrialProgressBar from '@/components/common/TrialProgressBar.vue'

export default {
  name: 'SidebarNav',
  components: {
    TrialProgressBar
  },
  props: {
    isCollapsed: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const store = useStore()
    const route = useRoute()
    const user = computed(() => store.getters['auth/user'])
    const company = computed(() => {
      const c = store.getters['company/getCompany'];
      console.log('SidebarNav company from store:', c);
      return c;
    })
    const isSuperuser = computed(() => user.value?.is_superuser || false)
    const isPlatformAdmin = computed(() => store.getters['auth/isPlatformAdmin'])
    const hasCompany = computed(() => store.getters['auth/hasCompany'])

    const expandedMenus = ref({
      accounting: false,
      treasury: false
    })

    const checkActiveRoutes = () => {
      if (route.path.startsWith('/accounting')) {
        expandedMenus.value.accounting = true
      }
      if (route.path.startsWith('/treasury')) {
        expandedMenus.value.treasury = true
      }
    }

    onMounted(() => {
      checkActiveRoutes()
    })

    watch(() => route.path, () => {
      checkActiveRoutes()
    })

    const toggleMenu = (menu) => {
      expandedMenus.value[menu] = !expandedMenus.value[menu]
    }

    return {
      isSuperuser,
      isPlatformAdmin,
      hasCompany,
      company,
      expandedMenus,
      toggleMenu
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #eee;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #333;
}

.sidebar-header h1 {
  font-size: 1.2rem;
  margin: 0;
  white-space: nowrap;
}

.collapse-btn {
  background: none;
  border: none;
  color: #eee;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
}

.sidebar-nav {
  padding: 0.5rem 0;
  overflow-y: auto;
  max-height: calc(100vh - 60px);
  scrollbar-width: thin;
  scrollbar-color: #333 #1a1a2e;
}

.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: #1a1a2e;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #ccc;
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-item:hover {
  background-color: #16213e;
  color: #fff;
}

.nav-item.active {
  background-color: #0f3460;
  color: #fff;
  border-left: 3px solid #e94560;
}

.has-submenu {
  cursor: pointer;
  user-select: none;
}

.submenu-arrow {
  margin-left: auto;
  font-size: 0.7rem;
  opacity: 0.7;
  transition: transform 0.3s ease;
}

.submenu-open .submenu-arrow {
  transform: rotate(90deg);
}

.submenu-items {
  background-color: rgba(0, 0, 0, 0.2);
  border-left: 3px solid transparent;
  overflow: hidden;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease-in-out;
  max-height: 500px;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.nav-sub {
  padding-left: 2.5rem;
  font-size: 0.9rem;
}

.nav-sub .nav-icon {
  font-size: 1rem;
}

.nav-section-divider {
  padding: 0.75rem 1rem 0.25rem 2.5rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #666;
  font-weight: 600;
}

.platform-section {
  border-top: 1px solid #333;
  margin-top: 0.5rem;
  padding-top: 1rem;
}

.nav-icon {
  font-size: 1.2rem;
  margin-right: 0.75rem;
  min-width: 24px;
  text-align: center;
}
</style>
