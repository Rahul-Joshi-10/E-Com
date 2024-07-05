function displayFlashMessage(category, message) {
  const flashMessagesContainer = document.getElementById("flash-messages");
  const flashMessageDiv = document.createElement("div");
  flashMessageDiv.className = `alert alert-${category}`;
  flashMessageDiv.innerHTML = `${message}
      <button type="button" class="close" onclick="this.parentElement.style.display='none';">&times;</button>`;
  flashMessagesContainer.appendChild(flashMessageDiv);
  setTimeout(() => {
    flashMessageDiv.style.opacity = "0";
    setTimeout(() => flashMessageDiv.remove(), 300);
  }, 5000);
}
function AddToWishlist(product_id) {
  fetch(`/check_wishlist/${product_id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        displayFlashMessage(
          "success",
          "Product added to wishlist successfully"
        );
      } else {
        displayFlashMessage("error", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      displayFlashMessage("error", "An error occurred. Please try again.");
    });
}
function RemoveWishlist(product_id) {
  fetch(`/check_wishlist/${product_id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        displayFlashMessage("success", "Product Remove From wishlist");
      } else {
        displayFlashMessage("error", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      displayFlashMessage(
        "error",
        "Ajinkya mc error solve karun de mala. Please try again."
      );
    });
}
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".heart-icon-add").forEach(function (element) {
    element.addEventListener("click", function (event) {
      event.preventDefault();
      const productId = this.dataset.productId;
      AddToWishlist(productId);
    });
  });

  document.querySelectorAll(".heart-icon-remove").forEach(function (element) {
    element.addEventListener("click", function (event) {
      event.preventDefault();
      const productId = this.dataset.productId;
      // console.log(productId);
      RemoveWishlist(productId);
    });
  });

  document.querySelectorAll(".pro").forEach(function (element) {
    element.addEventListener("click", function (event) {
      event.preventDefault();
      const productId = this.dataset.productId;
       window.location.href=`/product_details/${productId}`
    });
  });
});


document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll(".product_edit").forEach(function (element) {
    element.addEventListener("click", function () {
      const productId = this.dataset.product_id;
      console.log(productId)
       window.location.href=`/edit_product/${String(productId)}`
    });
  });

  document.querySelectorAll('.delete-form').forEach(function(form) {
      form.addEventListener('submit', function(event) {
          event.preventDefault();
          const confirmed = confirm('Are you sure you want to delete this product?');
          if (confirmed) {
              fetch(this.action, {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json'
                  },
              })
              .then(response => response.json())
              .then(data => {
                  if (data.status === 'success') {
                      alert('Product deleted successfully');
                      window.location.reload(); // Reload the page to reflect the changes
                  } else {
                      alert(data.message);
                  }
              })
              .catch(error => {
                  console.error('Error:', error);
                  alert('An error occurred. Please try again.');
              });
          }
      });
  });
});






