// --- Helper function to get CSRF token ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// --- Function to update the cart display ---
function updateCartDisplay(tr, data, action) {
    if (data.success) {
        const cartTotalElem = document.getElementById('cart-total');

        // Item was reduced and still exists
        if (action === 'reduce' && data.qty > 0) {
            tr.querySelector('td:nth-child(3)').textContent = data.qty; // Quantity
            tr.querySelector('td:nth-child(4)').textContent = `$${data.item_total.toFixed(2)}`; // Item total
        } else {
            // Item was removed or reduced to 0
            tr.remove();
        }

        // Update the cart total display
        if (cartTotalElem) {
            cartTotalElem.textContent = data.cart_total.toFixed(2);
        }

        // If no items left, display empty message
        if (document.querySelectorAll('tbody tr').length === 0) {
            const table = document.querySelector('.cart-table');
            if (table) {
                table.outerHTML = '<p>Your cart is empty.</p>';
            }
        }
    } else {
        alert(data.error || "Something went wrong updating your cart.");
    }
}

// --- Event listeners for buttons ---
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.reduce-btn').forEach(button => {
        button.addEventListener('click', () => {
            const tr = button.closest('tr');
            const itemId = tr.dataset.id;

            fetch(`/update-cart/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ action: 'reduce' })
            })
            .then(res => res.json())
            .then(data => updateCartDisplay(tr, data, 'reduce'))
            .catch(err => console.error('Error:', err));
        });
    });

    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', () => {
            const tr = button.closest('tr');
            const itemId = tr.dataset.id;

            fetch(`/update-cart/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ action: 'remove' })
            })
            .then(res => res.json())
            .then(data => updateCartDisplay(tr, data, 'remove'))
            .catch(err => console.error('Error:', err));
        });
    });
});
