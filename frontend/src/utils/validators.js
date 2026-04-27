export function validateNIT(nit) {
  if (!nit || typeof nit !== 'string') {
    return { valid: false, message: 'NIT is required' }
  }
  const cleanNIT = nit.replace(/[-\s]/g, '')
  if (!/^\d+$/.test(cleanNIT)) {
    return { valid: false, message: 'NIT must contain only digits' }
  }
  return { valid: true, message: '' }
}

export function calculateDV(nit) {
  const cleanNIT = nit.replace(/[-\s]/g, '')
  const primes = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
  let sum = 0
  const digits = cleanNIT.split('').reverse()
  for (let i = 0; i < digits.length; i++) {
    sum += parseInt(digits[i]) * primes[i]
  }
  const remainder = sum % 11
  let dv
  if (remainder >= 2) {
    dv = 11 - remainder
  } else {
    dv = remainder
  }
  return dv.toString()
}

export function validateEmail(email) {
  if (!email) {
    return { valid: false, message: 'Email is required' }
  }
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!re.test(email)) {
    return { valid: false, message: 'Invalid email format' }
  }
  return { valid: true, message: '' }
}

export function validateRequired(value, fieldName = 'This field') {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return { valid: false, message: `${fieldName} is required` }
  }
  return { valid: true, message: '' }
}

export function validateMinLength(value, min, fieldName = 'This field') {
  if (!value || value.length < min) {
    return { valid: false, message: `${fieldName} must be at least ${min} characters` }
  }
  return { valid: true, message: '' }
}
