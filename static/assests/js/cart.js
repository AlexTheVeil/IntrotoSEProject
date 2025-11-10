function addToCart(productId, qty) {
    const pid = this.dataset.pid;
    const qty = qtyInput ? qtyInput.value : 1;

    fetch(`/add-to-cart/${pid}/`, {   // Make sure trailing slash matches urls.py
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `qty=${qty}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const cartCountElem = document.getElementById('cart-count');
            if (cartCountElem) cartCountElem.textContent = data.new_cart_count;
            alert(`${data.product_name} added to cart!`);
        } else {
            alert("Failed to add item to cart.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Something went wrong.");
    });
}
