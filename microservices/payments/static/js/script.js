// // Handle form submission
// document.getElementById('payment-form').addEventListener('submit', function(event) {
//     event.preventDefault(); // Prevent default form submission

//     // Collect form data
//     const amount = document.getElementById('amount').value;
//     const description = document.getElementById('description').value;
//     const item_name = document.getElementById('item_name').value;
//     const quantity = document.getElementById('quantity').value;

//     // Prepare data to send
//     const data = {
//         amount: parseInt(amount) * 100,  // Convert to centavos (PHP to centavos)
//         description: description,
//         item_name: item_name,
//         quantity: parseInt(quantity)
//     };

//     // Send POST request to Django backend
//     fetch('/create-checkout-session/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     })
//     .then(response => response.json())
//     .then(result => {
//         if (result.checkout_url) {
//             // Redirect user to the checkout URL
//             window.location.href = result.checkout_url;
//         } else {
//             // Display error message
//             document.getElementById('result').innerText = 'Error: ' + result.error;
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         document.getElementById('result').innerText = 'An error occurred.';
//     });
// });

// Handle form submission
document.getElementById('payment-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect form data
    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;
    const item_name = document.getElementById('item_name').value;
    const quantity = document.getElementById('quantity').value;

    // Prepare data to send
    const data = {
        amount: parseInt(amount) * 100,  // Convert to centavos (PHP to centavos)
        description: description,
        item_name: item_name,
        quantity: parseInt(quantity)
    };

    // Send POST request to Django backend
    fetch('/create-checkout-session/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.checkout_url) {
            // Redirect user to the checkout URL
            window.location.href = result.checkout_url;
        } else {
            // Display error message
            document.getElementById('result').innerText = 'Error: ' + result.error;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'An error occurred.';
    });
});
