document.addEventListener("DOMContentLoaded", function () {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const preview = document.getElementById('preview');
  
    fileInputs.forEach(input => {
      input.addEventListener('change', function () {
        const file = this.files[0];
        if (file && preview) {
          const reader = new FileReader();
          reader.onload = function () {
            preview.setAttribute('src', reader.result);
            preview.style.display = 'block';
          };
          reader.readAsDataURL(file);
        }
      });
    });
  });
  
  function copyMessage() {
    const msg = document.getElementById("copiable-message");
    navigator.clipboard.writeText(msg.innerText).then(() => {
      alert("Mensagem copiada!");
    });
  }
  