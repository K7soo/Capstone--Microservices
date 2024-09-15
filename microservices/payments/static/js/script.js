document.getElementById('payment-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect form data
    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;
    const item_name = document.getElementById('item_name').value;
    const quantity = document.getElementById('quantity').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    // Prepare data to send
    const data = {
        amount: parseInt(amount, 10),  // Convert to integer
        description: description,
        item_name: item_name,
        quantity: parseInt(quantity, 10),  // Convert to integer
        name: name,  
        email: email,
    };

    // Log the data being sent (for debugging)
    console.log('Data being sent:', data);

    // Send POST request to Django backend
    fetch('/create-checkout-session/', {  // URL found in urls.py
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorDetails => {
                console.error('API error details:', errorDetails);
                throw new Error(`Error ${response.status}: ${errorDetails.error || 'Unknown error'}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        if (data.checkout_url) {
            // Redirect to the checkout URL
            window.location.href = data.checkout_url;
        } else {
            console.error('Failed to get checkout URL:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
