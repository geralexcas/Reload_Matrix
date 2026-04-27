<template>
  <div class="backup-view">
    <div class="view-header">
      <h2>Copias de Seguridad (Backup)</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="createBackup" :disabled="loading">
          {{ loading ? 'Procesando...' : '+ Crear Respaldo' }}
        </button>
        <label class="btn btn-secondary ml-2">
          Subir Archivo
          <input type="file" @change="uploadBackup" accept=".zip" class="hidden-input" />
        </label>
      </div>
    </div>

    <div class="card shadow-sm mt-4">
      <div class="alert-box warning mb-4">
        <strong>Atención:</strong> La restauración reemplazará todos los datos actuales. 
        Se recomienda descargar una copia antes de restaurar.
      </div>

      <div v-if="fetching" class="loading-state">
        <p>Cargando archivos...</p>
      </div>

      <div v-else>
        <table class="data-table" v-if="backups.length">
          <thead>
            <tr>
              <th>Fecha y Hora</th>
              <th>Nombre del Archivo</th>
              <th>Tamaño</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="backup in backups" :key="backup.filename">
              <td class="text-muted">{{ formatDate(backup.created_at) }}</td>
              <td><strong>{{ backup.filename }}</strong></td>
              <td>{{ formatSize(backup.size_bytes) }}</td>
              <td class="text-right">
                <button class="btn btn-sm btn-outline-primary" @click="downloadBackup(backup.filename)">
                  Descargar
                </button>
                <button class="btn btn-sm btn-warning mx-1" @click="confirmRestore(backup.filename)">
                  Restaurar
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="deleteBackup(backup.filename)">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">
          <p>No hay copias de seguridad registradas.</p>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación -->
    <div v-if="showRestoreConfirm" class="modal-overlay">
      <div class="modal">
        <h3>Confirmar Restauración</h3>
        <div class="modal-body">
          <p>¿Estás seguro de que deseas restaurar el sistema al estado de:</p>
          <div class="selected-file">{{ selectedBackup }}</div>
          <p class="danger-text">Esta acción borrará los datos actuales y no se puede deshacer.</p>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showRestoreConfirm = false">Cancelar</button>
          <button class="btn btn-warning" @click="executeRestore" :disabled="loading">
            {{ loading ? 'Restaurando...' : 'Confirmar Restauración' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import store from '@/store'

export default {
  name: 'BackupView',
  setup() {
    const backups = ref([])
    const loading = ref(false)
    const fetching = ref(false)
    const showRestoreConfirm = ref(false)
    const selectedBackup = ref('')

    const fetchBackups = async () => {
      fetching.value = true
      try {
        const res = await api.get('/api/v1/admin/backups/')
        backups.value = res.data
      } catch (err) {
        console.error('Error:', err)
      } finally {
        fetching.value = false
      }
    }

    const createBackup = async () => {
      loading.value = true
      try {
        await api.post('/api/v1/admin/backups/create')
        await fetchBackups()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const downloadBackup = async (filename) => {
      try {
        const response = await api.get(`/api/v1/admin/backups/download/${filename}`, {
          responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (err) {
        alert('Error al descargar: ' + (err.response?.data?.detail || err.message))
      }
    }

    const deleteBackup = async (filename) => {
      if (!confirm(`¿Eliminar ${filename}?`)) return
      try {
        await api.delete(`/api/v1/admin/backups/${filename}`)
        await fetchBackups()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      }
    }

    const confirmRestore = (filename) => {
      selectedBackup.value = filename
      showRestoreConfirm.value = true
    }

    const executeRestore = async () => {
      loading.value = true
      try {
        await api.post(`/api/v1/admin/backups/restore/${selectedBackup.value}`)
        showRestoreConfirm.value = false
        alert('Restauración completada con éxito.')
        window.location.reload()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const uploadBackup = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      const formData = new FormData()
      formData.append('file', file)
      loading.value = true
      try {
        await api.post('/api/v1/admin/backups/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        await fetchBackups()
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        loading.value = false
      }
    }

    const formatDate = (d) => new Date(d).toLocaleString('es-CO')
    const formatSize = (b) => {
      if (!b) return '0 B'
      const i = Math.floor(Math.log(b) / Math.log(1024))
      return (b / Math.pow(1024, i)).toFixed(2) + ' ' + ['B', 'KB', 'MB', 'GB'][i]
    }

    onMounted(fetchBackups)

    return {
      backups, loading, fetching, showRestoreConfirm, selectedBackup,
      createBackup, downloadBackup, deleteBackup, confirmRestore, executeRestore,
      uploadBackup, formatDate, formatSize
    }
  }
}
</script>

<style scoped>
.backup-view {
  padding: 20px;
  text-align: left;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.alert-box {
  padding: 15px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.alert-box.warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 12px;
  border-bottom: 2px solid #eee;
  text-align: left;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.text-right { text-align: right; }
.text-muted { color: #6c757d; font-size: 0.85rem; }
.ml-2 { margin-left: 0.5rem; }
.mx-1 { margin-left: 0.25rem; margin-right: 0.25rem; }

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: inline-block;
}

.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-primary { background: #007bff; color: white; }
.btn-primary:hover { background: #0056b3; }

.btn-secondary { background: #6c757d; color: white; cursor: pointer; }

.btn-warning { background: #ffc107; color: #212529; }
.btn-warning:hover { background: #e0a800; }

.btn-outline-primary {
  background: transparent;
  border: 1px solid #007bff;
  color: #007bff;
}
.btn-outline-primary:hover { background: #007bff; color: white; }

.btn-outline-danger {
  background: transparent;
  border: 1px solid #dc3545;
  color: #dc3545;
}
.btn-outline-danger:hover { background: #dc3545; color: white; }

.btn-sm {
  padding: 4px 10px;
  font-size: 0.8rem;
}

.hidden-input { display: none; }

.modal-overlay {
  position: fixed;
  top:0; left:0; right:0; bottom:0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 25px;
  border-radius: 12px;
  width: 400px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal h3 { margin-top: 0; color: #dc3545; }
.selected-file {
  background: #f8f9fa;
  padding: 10px;
  margin: 15px 0;
  border-radius: 4px;
  font-weight: bold;
  word-break: break-all;
}
.danger-text { color: #dc3545; font-size: 0.9rem; margin-top: 15px; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.loading-state, .empty-state {
  padding: 40px;
  text-align: center;
  color: #6c757d;
}
</style>
