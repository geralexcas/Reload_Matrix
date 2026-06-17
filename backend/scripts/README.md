# Scripts de Inicialización - Reload Matrix

## create_admin.py

Script para crear o actualizar el usuario administrador del sistema.

### Uso básico

```bash
# Crear admin con valores por defecto (admin / Admin@123456)
docker compose exec backend python scripts/create_admin.py

# Crear admin con parámetros personalizados
docker compose exec backend python scripts/create_admin.py --email admin@empresa.com --username admin --password "NuevaClave@123"
```

### Restablecer contraseña

Si el usuario ya existe y necesitas cambiar la contraseña, usa el flag `--reset`:

```bash
# Resetear a la contraseña por defecto (Admin@123456)
docker compose exec backend python scripts/create_admin.py --reset

# Resetear con una contraseña personalizada
docker compose exec backend python scripts/create_admin.py --reset --password "NuevaClave@123"
```

### Verificar login después de crear/resetear

```bash
docker compose exec backend python scripts/create_admin.py --reset --verify
```

### Parámetros disponibles

| Parámetro | Default | Descripción |
|---|---|---|
| `--email` | admin@reloadmatrix.com | Email del admin |
| `--username` | admin | Nombre de usuario |
| `--password` | Admin@123456 | Contraseña (debe cumplir política de fortaleza) |
| `--full-name` | Administrador Sistema | Nombre completo |
| `--company-id` | None | ID de empresa a asociar |
| `--reset` | false | Actualizar contraseña si el usuario ya existe |
| `--verify` | false | Verificar login después de crear/resetear |

### Política de contraseñas

- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un dígito
- Al menos un carácter especial
