// Custom JavaScript for Campus Voice
document.addEventListener('DOMContentLoaded', function() {
  // HTMX config
  htmx.config.defaultSwapStyle = 'outerHTML';
  
  document.body.addEventListener('htmx:configRequest', function(evt) {
    const csrfMatch = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrfMatch) {
      evt.detail.headers['X-CSRFToken'] = csrfMatch[1];
    }
  });
});