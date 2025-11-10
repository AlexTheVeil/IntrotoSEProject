// Example for Remove or Quantity buttons
document.querySelectorAll(".cart-item-button").forEach(button => {
  button.addEventListener("click", function() {
    const itemId = this.dataset.itemId;  // Make sure your buttons have data-item-id attribute
    const action = this.dataset.action;  // e.g., "increase", "decrease", "remove"

    fetch(`/cart/update/${itemId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")  // CSRF token helper function
      },
      body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Update the UI: qty, item total, cart total, etc.
        if (data.removed) {
          document.getElementById(`cart-item-${itemId}`).remove();
        } else {
          document.querySelector(`#cart-item-${itemId} .item-qty`).textContent = data.qty;
          document.querySelector(`#cart-item-${itemId} .item-total`).textContent = data.item_total.toFixed(2);
        }
        document.querySelector("#cart-total").textContent = data.cart_total.toFixed(2);
      } else {
        console.error(data.error);
      }
    });
  });
});

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
