const Toast = {
  install(app) {
    const toastContainer = document.createElement('div')
    toastContainer.id = 'toast-container'
    toastContainer.style.position = 'fixed'
    toastContainer.style.top = '20px'
    toastContainer.style.right = '20px'
    toastContainer.style.zIndex = '1050'
    document.body.appendChild(toastContainer)

    app.config.globalProperties.$toast = {
      success(message) {
        this._createToast(message, 'success')
      },
      error(message) {
        this._createToast(message, 'error')
      },
      info(message) {
        this._createToast(message, 'info')
      },
      warning(message) {
        this._createToast(message, 'warning')
      },
      _createToast(message, type) {
        const toast = document.createElement('div')
        toast.className = `toast toast-${type}`
        toast.innerHTML = `
          <div class="toast-content">
            <span>${message}</span>
          </div>
          <button class="toast-close">&times;</button>
        `
        toast.style.position = 'relative'
        toast.style.marginBottom = '10px'
        toast.style.padding = '15px'
        toast.style.borderRadius = '4px'
        toast.style.color = 'white'
        toast.style.display = 'flex'
        toast.style.justifyContent = 'space-between'
        toast.style.alignItems = 'center'
        
        switch(type) {
          case 'success': toast.style.backgroundColor = '#28a745'; break;
          case 'error': toast.style.backgroundColor = '#dc3545'; break;
          case 'info': toast.style.backgroundColor = '#17a2b8'; break;
          case 'warning': toast.style.backgroundColor = '#ffc107'; toast.style.color = '#212529'; break;
          default: toast.style.backgroundColor = '#6c757d';
        }
        
        const closeBtn = toast.querySelector('.toast-close')
        closeBtn.style.background = 'none'
        closeBtn.style.border = 'none'
        closeBtn.style.color = 'inherit'
        closeBtn.style.fontSize = '1.5rem'
        closeBtn.style.cursor = 'pointer'
        
        toastContainer.appendChild(toast)
        
        setTimeout(() => {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast)
          }
        }, 5000)
        
        closeBtn.addEventListener('click', () => {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast)
          }
        })
      }
    }
  }
}

export default Toast
