<template>
  <div class="register-container">
    <div class="register-card">
      <h2>Registro de Usuario</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label for="email">Email:</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required
            placeholder="Ingrese su email"
          />
        </div>
        <div class="form-group">
          <label for="username">Usuario:</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required
            placeholder="Ingrese su usuario"
          />
        </div>
        <div class="form-group">
          <label for="password">Contraseña:</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required
            placeholder="Ingrese su contraseña"
          />
        </div>
        <div class="form-group">
          <label for="full_name">Nombre Completo:</label>
          <input 
            type="text" 
            id="full_name" 
            v-model="full_name" 
            required
            placeholder="Ingrese su nombre completo"
          />
        </div>
        <div class="form-group">
          <button type="submit" class="btn btn-primary">Registrarse</button>
        </div>
        <div class="form-group" v-if="error">
          <p class="error-message">{{ error }}</p>
        </div>
        <div class="form-group" v-if="success">
          <p class="success-message">{{ success }}</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterView',
  data() {
    return {
      email: '',
      username: '',
      password: '',
      full_name: '',
      error: null,
      success: null
    }
  },
  methods: {
    async onSubmit() {
      try {
        await this.$store.dispatch('auth/register', {
          email: this.email,
          username: this.username,
          password: this.password,
          full_name: this.full_name
        })
        this.success = 'Registro exitoso. Ahora puede iniciar sesión.'
        this.error = null
        this.email = ''
        this.username = ''
        this.password = ''
        this.full_name = ''
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al registrarse'
        this.success = null
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
}

.register-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.btn:hover {
  background-color: #0056b3;
}

.btn-primary {
  background-color: #28a745;
}

.btn-primary:hover {
  background-color: #218838;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.success-message {
  color: #28a745;
  background-color: #d4edda;
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid #c3e6cb;
}
</style>