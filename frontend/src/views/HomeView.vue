<template>
  <div class="home">
    <h1>Sistema de Gestión Empresarial</h1>
    <p>Bienvenido al sistema integral de gestión comercial.</p>
    <div class="buttons">
      <router-link to="/login" class="btn">Iniciar Sesión</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 20px;
}
.buttons {
  margin-top: 30px;
}
.btn {
  display: inline-block;
  margin: 0 10px;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s;
}
.btn:hover {
  background-color: #0056b3;
}
</style>